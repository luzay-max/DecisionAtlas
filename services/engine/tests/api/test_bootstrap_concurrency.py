"""Issue #48: deterministic local-only identity consistency under concurrent clients.

Only creates temporary file-backed SQLite databases, synthetic identities and
test sessions. Production auto bootstrap must remain impossible.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.auth import SESSION_HEADER
from app.db.models import Actor, AuthSession, OwnerScope, OwnerScopeMembership
from app.main import create_app
from app.repositories.auth import AuthRepository, hash_password


def _migrate(tmp_path: Path, monkeypatch) -> Path:
    path = tmp_path / "issue48-concurrent-bootstrap.db"
    url = f"sqlite:///{path}"
    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("AUTH_AUTO_BOOTSTRAP_LOCAL", "true")
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", url)
    command.upgrade(config, "head")
    return path


@pytest.mark.parametrize("request_count", [2, 8])
def test_simultaneous_local_bootstraps_are_atomic_and_idempotent(
    tmp_path: Path, monkeypatch, request_count: int
) -> None:
    path = _migrate(tmp_path, monkeypatch)
    gate = Barrier(request_count, timeout=20)

    def bootstrap(_index: int) -> tuple[int, dict]:
        with TestClient(create_app()) as client:
            gate.wait()
            response = client.post("/auth/bootstrap")
            return response.status_code, response.json()

    # Every request uses an independent TestClient/session/connection, not a
    # synchronized in-process mock of the repository. File-based SQLite writer
    # locks are shared between distinct connections and processes.
    with ThreadPoolExecutor(max_workers=request_count) as pool:
        responses = list(pool.map(bootstrap, range(request_count)))

    assert all(status == 200 for status, _ in responses)
    identities = [payload for _, payload in responses]
    assert all(entry["actor"]["username"] == "local-admin" for entry in identities)
    assert all(entry["actor"]["bootstrap"] is True for entry in identities)
    assert all(entry["role"] == "admin" for entry in identities)
    assert all(entry["current_owner_scope"] == "local-default" for entry in identities)
    assert len({entry["actor"]["id"] for entry in identities}) == 1
    tokens = [entry["session_token"] for entry in identities]
    assert len(set(tokens)) == request_count

    # Separate reconnect confirms exactly one actor/scope/membership and all
    # unique sessions durable. No partial identity state or duplicate role.
    engine = create_engine(f"sqlite:///{path}")
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(Actor)) == 1
        assert session.scalar(select(func.count()).select_from(OwnerScope)) == 1
        assert session.scalar(select(func.count()).select_from(OwnerScopeMembership)) == 1
        assert session.scalar(select(func.count()).select_from(AuthSession)) == request_count
        sessions = list(session.scalars(select(AuthSession)))
        assert {record.session_token for record in sessions} == set(tokens)
        assert {record.actor_id for record in sessions} == {identities[0]["actor"]["id"]}
    engine.dispose()

    # Every issued token remains valid after the concurrent writes commit.
    with TestClient(create_app()) as client:
        for token in tokens:
            checked = client.get("/auth/session", headers={SESSION_HEADER: token})
            assert checked.status_code == 200
            assert checked.json()["role"] == "admin"


@pytest.mark.parametrize("collision", ["normal_actor", "disabled_bootstrap", "team_scope"])
def test_bootstrap_never_elevates_a_colliding_identity(
    tmp_path: Path, monkeypatch, collision: str
) -> None:
    path = _migrate(tmp_path, monkeypatch)
    engine = create_engine(f"sqlite:///{path}")
    with Session(engine) as session:
        repo = AuthRepository(session)
        if collision == "normal_actor":
            repo.create_actor(
                username="local-admin", password_hash=hash_password("not-bootstrap"),
                is_bootstrap=False,
            )
        elif collision == "disabled_bootstrap":
            actor = repo.create_actor(
                username="local-admin", password_hash=hash_password("no-revival"),
                is_bootstrap=True,
            )
            actor.status = "disabled"
        else:
            repo.create_scope(
                scope_key="local-default", display_name="Preexisting team",
                scope_type="team",
            )
        session.commit()

    with TestClient(create_app()) as client:
        response = client.post("/auth/bootstrap")
        assert response.status_code == 403
        assert response.json()["detail"] == "Local bootstrap identity is unavailable"

    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(OwnerScopeMembership)) == 0
        assert session.scalar(select(func.count()).select_from(AuthSession)) == 0
        if collision == "normal_actor":
            actor = session.scalar(select(Actor).where(Actor.username == "local-admin"))
            assert actor is not None and actor.is_bootstrap is False
        if collision == "disabled_bootstrap":
            actor = session.scalar(select(Actor).where(Actor.username == "local-admin"))
            assert actor is not None and actor.status == "disabled"
    engine.dispose()


def test_production_and_disabled_bootstrap_still_fail_before_database_writes(
    tmp_path: Path, monkeypatch
) -> None:
    path = _migrate(tmp_path, monkeypatch)
    with TestClient(create_app()) as client:
        monkeypatch.setenv("APP_ENV", "production")
        assert client.post("/auth/bootstrap").status_code == 403
        monkeypatch.setenv("APP_ENV", "test")
        monkeypatch.setenv("AUTH_AUTO_BOOTSTRAP_LOCAL", "false")
        assert client.post("/auth/bootstrap").status_code == 403
    engine = create_engine(f"sqlite:///{path}")
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(Actor)) == 0
        assert session.scalar(select(func.count()).select_from(OwnerScope)) == 0
        assert session.scalar(select(func.count()).select_from(AuthSession)) == 0
    engine.dispose()
