from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import os
from threading import Barrier, Event, local
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, event, inspect, select, text
from sqlalchemy.orm import Session

from app.auth import SESSION_HEADER
from app.db.models import Actor, AuthSession, OwnerScope, OwnerScopeMembership
from app.main import create_app
from app.repositories.auth import AuthRepository, hash_password, verify_password


def _engine(url: str):
    if url.startswith("sqlite"):
        return create_engine(
            url,
            connect_args={"timeout": 30, "check_same_thread": False},
        )
    return create_engine(url)


def _dispose_cached_app_engine(url: str) -> None:
    # get_db_session caches engines by URL; dispose the test URL so Windows can
    # remove temporary SQLite files and later tests cannot reuse stale pools.
    from app.db import session as db_session

    with db_session._engine_lock:
        engine = db_session._engines.pop(url, None)
        db_session._session_factories.pop(url, None)
    if engine is not None:
        engine.dispose()


@pytest.fixture(params=("sqlite", "postgresql"), ids=("file-sqlite", "postgresql-17"))
def password_concurrency_database(request, tmp_path, monkeypatch) -> str:
    if request.param == "sqlite":
        url = f"sqlite:///{tmp_path / 'password-concurrency.db'}"
    else:
        url = os.getenv("DECISIONATLAS_PASSWORD_CONCURRENCY_DATABASE_URL", "")
        if not url.startswith("postgresql+psycopg://"):
            pytest.skip("PostgreSQL 17 password concurrency test requires the isolated CI URL")

    monkeypatch.setenv("DATABASE_URL", url)
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", url)
    expected_version = ScriptDirectory.from_config(config).get_current_head()
    engine = _engine(url)
    try:
        with engine.connect() as connection:
            if url.startswith("postgresql"):
                server_version = int(connection.scalar(text("SHOW server_version_num")))
                assert server_version >= 170000, f"Expected PostgreSQL 17+, got {server_version}"
            has_alembic_version = inspect(connection).has_table("alembic_version")
            current_version = (
                connection.scalar(text("SELECT version_num FROM alembic_version"))
                if has_alembic_version
                else None
            )
        # Close the inspection connection before Alembic writes. In particular,
        # an open SQLite read transaction must not hold the schema migration.
        if current_version is None:
            command.upgrade(config, "head")
        else:
            assert current_version == expected_version, (
                "Refuse to run password concurrency tests against an unexpected schema"
            )
        with engine.connect() as connection:
            assert connection.scalar(text("SELECT version_num FROM alembic_version")) == (
                expected_version
            )
    finally:
        engine.dispose()

    try:
        yield url
    finally:
        _dispose_cached_app_engine(url)


@dataclass(frozen=True)
class ActorCase:
    username: str
    actor_id: int
    scope_id: int


def _legacy_hash(password: str) -> str:
    salt = uuid4().hex
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("ascii"), 100_000)
    return f"{salt}${digest.hex()}"


@contextmanager
def _actor_case(url: str, stored_hash: str):
    username = f"b05-{uuid4().hex}"
    scope_key = f"b05-{uuid4().hex}"
    engine = _engine(url)
    case: ActorCase | None = None
    try:
        with Session(engine) as session:
            repo = AuthRepository(session)
            scope = repo.create_scope(
                scope_key=scope_key,
                display_name="B05 password concurrency test",
                scope_type="team",
            )
            actor = repo.create_actor(username=username, password_hash=stored_hash)
            repo.ensure_membership(actor_id=actor.id, owner_scope_id=scope.id, role="admin")
            session.commit()
            case = ActorCase(username=username, actor_id=actor.id, scope_id=scope.id)
        yield case
    finally:
        if case is not None:
            with engine.begin() as connection:
                connection.execute(delete(AuthSession).where(AuthSession.actor_id == case.actor_id))
                connection.execute(
                    delete(OwnerScopeMembership).where(OwnerScopeMembership.actor_id == case.actor_id)
                )
                connection.execute(delete(Actor).where(Actor.id == case.actor_id))
                connection.execute(delete(OwnerScope).where(OwnerScope.id == case.scope_id))
        engine.dispose()


def _actor_snapshot(url: str, actor_id: int) -> tuple[str, str]:
    engine = _engine(url)
    try:
        with Session(engine) as session:
            actor = session.get(Actor, actor_id)
            assert actor is not None
            return actor.status, actor.password_hash
    finally:
        engine.dispose()


def _session_tokens(url: str, actor_id: int) -> list[str]:
    engine = _engine(url)
    try:
        with Session(engine) as session:
            return list(
                session.scalars(
                    select(AuthSession.session_token).where(AuthSession.actor_id == actor_id)
                ).all()
            )
    finally:
        engine.dispose()


def _login(username: str, password: str) -> tuple[int, dict]:
    with TestClient(create_app()) as client:
        response = client.post(
            "/auth/login",
            json={"username": username, "password": password},
        )
        return response.status_code, response.json()


def test_two_simultaneous_legacy_logins_both_upgrade_and_return_valid_sessions(
    password_concurrency_database: str, monkeypatch
) -> None:
    old_password = "old-password-for-parallel-login"
    with _actor_case(password_concurrency_database, _legacy_hash(old_password)) as actor:
        barrier = Barrier(2, timeout=30)
        first_call = local()
        original_cas = AuthRepository.compare_and_set_password_hash

        def synchronize_first_cas(self, **kwargs):
            if not getattr(first_call, "arrived", False):
                first_call.arrived = True
                barrier.wait()
            return original_cas(self, **kwargs)

        monkeypatch.setattr(AuthRepository, "compare_and_set_password_hash", synchronize_first_cas)
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(_login, actor.username, old_password) for _ in range(2)]
            results = [future.result(timeout=60) for future in futures]

        assert [status for status, _ in results] == [200, 200]
        tokens = [body["session_token"] for _, body in results]
        assert len(set(tokens)) == 2

        status, stored_hash = _actor_snapshot(password_concurrency_database, actor.actor_id)
        assert status == "active"
        assert stored_hash.startswith("$argon2id$v=19$")
        assert verify_password(old_password, stored_hash)
        assert set(_session_tokens(password_concurrency_database, actor.actor_id)) == set(tokens)

        with TestClient(create_app()) as client:
            for token in tokens:
                response = client.get("/auth/session", headers={SESSION_HEADER: token})
                assert response.status_code == 200


def test_password_reset_committing_before_login_cas_rejects_stale_password(
    password_concurrency_database: str, monkeypatch
) -> None:
    old_password = "old-password-before-cas"
    new_password = "replacement-password-before-cas"
    with _actor_case(password_concurrency_database, _legacy_hash(old_password)) as actor:
        operation_engine = _engine(password_concurrency_database)
        original_cas = AuthRepository.compare_and_set_password_hash
        reset_done = Event()

        def reset_before_cas(self, **kwargs):
            if not reset_done.is_set():
                with Session(operation_engine) as reset_session:
                    AuthRepository(reset_session).reset_actor_password(
                        actor_id=actor.actor_id,
                        password=new_password,
                    )
                    reset_session.commit()
                reset_done.set()
            return original_cas(self, **kwargs)

        monkeypatch.setattr(AuthRepository, "compare_and_set_password_hash", reset_before_cas)
        stale_status, _ = _login(actor.username, old_password)
        assert reset_done.is_set()
        assert stale_status == 401
        assert _session_tokens(password_concurrency_database, actor.actor_id) == []

        current_status, current_body = _login(actor.username, new_password)
        assert current_status == 200
        assert current_body["session_token"] in _session_tokens(
            password_concurrency_database, actor.actor_id
        )
        operation_engine.dispose()


@pytest.mark.parametrize("initial_hash_kind", ("legacy", "argon2id"))
@pytest.mark.parametrize("operation", ("password-reset", "account-disable"))
def test_login_cas_first_then_reset_or_disable_revokes_the_login_session(
    password_concurrency_database: str,
    monkeypatch,
    initial_hash_kind: str,
    operation: str,
) -> None:
    old_password = "old-password-cas-first"
    new_password = "replacement-password-cas-first"
    initial_hash = (
        _legacy_hash(old_password)
        if initial_hash_kind == "legacy"
        else hash_password(old_password)
    )
    with _actor_case(password_concurrency_database, initial_hash) as actor:
        cas_acquired = Event()
        allow_login_commit = Event()
        first_mutation_ready = Event()
        allow_operation_mutation = Event()
        mutation_statements: list[str] = []
        original_cas = AuthRepository.compare_and_set_password_hash

        def hold_login_after_cas(self, **kwargs):
            updated = original_cas(self, **kwargs)
            if updated:
                cas_acquired.set()
                if not allow_login_commit.wait(timeout=30):
                    raise TimeoutError("test did not release the login transaction")
            return updated

        monkeypatch.setattr(AuthRepository, "compare_and_set_password_hash", hold_login_after_cas)

        operation_engine = _engine(password_concurrency_database)

        def pause_first_mutation(conn, cursor, statement, parameters, context, executemany):
            normalized = " ".join(statement.lower().split())
            if normalized.startswith("update actors") or normalized.startswith("delete from auth_sessions"):
                mutation_statements.append(normalized)
                if len(mutation_statements) == 1:
                    first_mutation_ready.set()
                    if not allow_operation_mutation.wait(timeout=30):
                        raise TimeoutError("test did not release the reset/disable statement")

        event.listen(operation_engine, "before_cursor_execute", pause_first_mutation)

        def mutate_account() -> None:
            with Session(operation_engine) as operation_session:
                repo = AuthRepository(operation_session)
                if operation == "password-reset":
                    assert repo.reset_actor_password(
                        actor_id=actor.actor_id,
                        password=new_password,
                    ) is not None
                else:
                    assert repo.set_actor_status(
                        actor_id=actor.actor_id,
                        status="disabled",
                    ) is not None
                operation_session.commit()

        mutation_future = None
        try:
            with ThreadPoolExecutor(max_workers=2) as pool:
                login_future = pool.submit(_login, actor.username, old_password)
                assert cas_acquired.wait(timeout=30), "login did not acquire the CAS write lock"
                mutation_future = pool.submit(mutate_account)
                assert first_mutation_ready.wait(timeout=30), (
                    "reset/disable did not reach its first database mutation"
                )
                assert not login_future.done(), "login transaction unexpectedly committed before the barrier"
                # Both operations are now staged on independent DB connections:
                # the login holds the CAS transaction while reset/disable reaches
                # its first write. Releasing both lets the database serialize them.
                allow_operation_mutation.set()
                allow_login_commit.set()
                login_status, login_body = login_future.result(timeout=60)
                mutation_future.result(timeout=60)
        finally:
            allow_operation_mutation.set()
            allow_login_commit.set()
            event.remove(operation_engine, "before_cursor_execute", pause_first_mutation)
            operation_engine.dispose()

        assert login_status == 200
        assert mutation_statements, "expected an account mutation statement"
        assert mutation_statements[0].startswith("update actors"), (
            "password reset/disable must lock/update the actor row before deleting sessions"
        )
        assert any(statement.startswith("delete from auth_sessions") for statement in mutation_statements), (
            "password reset/disable must revoke sessions after the actor row update"
        )

        status, stored_hash = _actor_snapshot(password_concurrency_database, actor.actor_id)
        assert login_body["session_token"] not in _session_tokens(
            password_concurrency_database, actor.actor_id
        )
        with TestClient(create_app()) as client:
            invalidated = client.get(
                "/auth/session",
                headers={SESSION_HEADER: login_body["session_token"]},
            )
            assert invalidated.status_code == 401

        if operation == "password-reset":
            assert status == "active"
            assert verify_password(new_password, stored_hash)
            assert not verify_password(old_password, stored_hash)
            current_status, current_body = _login(actor.username, new_password)
            assert current_status == 200
            assert current_body["session_token"] in _session_tokens(
                password_concurrency_database, actor.actor_id
            )
        else:
            assert status == "disabled"
            assert verify_password(old_password, stored_hash)
            disabled_status, _ = _login(actor.username, old_password)
            assert disabled_status == 401
            assert _session_tokens(password_concurrency_database, actor.actor_id) == []
            assert _actor_snapshot(password_concurrency_database, actor.actor_id)[0] == "disabled"
