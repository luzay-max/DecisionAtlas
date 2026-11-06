from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.db.models import Actor, AuthSession
from app.main import create_app
from app.repositories.auth import (
    AuthRepository,
    hash_password,
    password_hash_needs_rehash,
    verify_password,
)


def _legacy_pbkdf2_hash(password: str) -> str:
    # Exact legacy format written by the pre-B05 implementation.
    salt = "00112233445566778899aabbccddeeff"
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
    return f"{salt}${digest.hex()}"


def _setup_legacy_actor(db_path: Path, monkeypatch, password_hash: str) -> int:
    database_url = f"sqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(config, "head")

    engine = create_engine(database_url)
    with Session(engine) as session:
        repo = AuthRepository(session)
        scope = repo.create_scope(scope_key="team-passwords", display_name="Password Tests", scope_type="team")
        actor = repo.create_actor(username="legacy-user", password_hash=password_hash)
        repo.ensure_membership(actor_id=actor.id, owner_scope_id=scope.id, role="admin")
        session.commit()
        actor_id = actor.id
    engine.dispose()
    return actor_id


def _stored_password_hash(db_path: Path) -> str:
    engine = create_engine(f"sqlite:///{db_path}")
    try:
        with Session(engine) as session:
            actor = session.scalar(select(Actor).where(Actor.username == "legacy-user"))
            assert actor is not None
            return actor.password_hash
    finally:
        engine.dispose()


def _session_count(db_path: Path) -> int:
    engine = create_engine(f"sqlite:///{db_path}")
    try:
        with Session(engine) as session:
            return int(session.scalar(select(func.count(AuthSession.id))) or 0)
    finally:
        engine.dispose()


def test_argon2id_hashes_and_legacy_pbkdf2_verification_are_compatible() -> None:
    current_hash = hash_password("correct horse battery staple")
    legacy_hash = _legacy_pbkdf2_hash("correct horse battery staple")

    assert current_hash.startswith("$argon2id$v=19$")
    assert verify_password("correct horse battery staple", current_hash)
    assert not verify_password("wrong password", current_hash)
    assert not password_hash_needs_rehash(current_hash)

    assert verify_password("correct horse battery staple", legacy_hash)
    assert not verify_password("wrong password", legacy_hash)
    assert password_hash_needs_rehash(legacy_hash)


@pytest.mark.parametrize(
    "stored_hash",
    [
        "",
        "not-a-password-hash",
        "salt$not-hex",
        "z" * 32 + "$" + "0" * 64,
        "a" * 32 + "$" + "0" * 63,
        "$argon2id$malformed",
        "$argon2i$v=19$m=19456,t=2,p=1$bad$bad",
    ],
)
def test_malformed_password_hashes_fail_closed(stored_hash: str) -> None:
    assert not verify_password("any password", stored_hash)



@pytest.mark.parametrize(
    ("parameter", "excessive_value"),
    [
        ("m=19456", "m=1048576"),
        ("t=2", "t=999"),
        ("p=1", "p=999"),
    ],
)
def test_argon2id_hashes_with_excessive_phc_parameters_fail_before_verification(
    monkeypatch, parameter: str, excessive_value: str
) -> None:
    import app.repositories.auth as auth_repository

    safe_hash = hash_password("bounded password")
    untrusted_hash = safe_hash.replace(parameter, excessive_value, 1)
    assert untrusted_hash != safe_hash

    def verification_must_not_run(*args, **kwargs):
        pytest.fail("Argon2 verification ran before PHC resource limits were checked")

    monkeypatch.setattr(auth_repository.PasswordHasher, "verify", verification_must_not_run)
    assert not verify_password("bounded password", untrusted_hash)
    assert not password_hash_needs_rehash(untrusted_hash)


def test_login_upgrades_legacy_hash_only_after_correct_password(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "legacy-login.db"
    legacy_hash = _legacy_pbkdf2_hash("old-password")
    _setup_legacy_actor(db_path, monkeypatch, legacy_hash)
    client = TestClient(create_app())

    wrong = client.post("/auth/login", json={"username": "legacy-user", "password": "wrong-password"})
    assert wrong.status_code == 401
    assert _stored_password_hash(db_path) == legacy_hash
    assert _session_count(db_path) == 0

    correct = client.post("/auth/login", json={"username": "legacy-user", "password": "old-password"})
    assert correct.status_code == 200
    upgraded_hash = _stored_password_hash(db_path)
    assert upgraded_hash.startswith("$argon2id$v=19$")
    assert upgraded_hash != legacy_hash
    assert verify_password("old-password", upgraded_hash)
    assert not verify_password("wrong-password", upgraded_hash)
    assert not password_hash_needs_rehash(upgraded_hash)
    assert _session_count(db_path) == 1


def test_password_reset_winning_login_upgrade_race_rejects_old_password(
    tmp_path: Path, monkeypatch
) -> None:
    db_path = tmp_path / "concurrent-password-reset.db"
    legacy_hash = _legacy_pbkdf2_hash("old-password")
    actor_id = _setup_legacy_actor(db_path, monkeypatch, legacy_hash)
    engine = create_engine(f"sqlite:///{db_path}")
    original_compare_and_set = AuthRepository.compare_and_set_password_hash
    race = {"reset_committed": False}

    def reset_before_compare(
        repository: AuthRepository,
        *,
        actor_id: int,
        expected_hash: str,
        new_hash: str,
    ) -> bool:
        if not race["reset_committed"]:
            with Session(engine) as concurrent_session:
                AuthRepository(concurrent_session).reset_actor_password(
                    actor_id=actor_id,
                    password="replacement-password",
                )
                concurrent_session.commit()
            race["reset_committed"] = True
        return original_compare_and_set(
            repository,
            actor_id=actor_id,
            expected_hash=expected_hash,
            new_hash=new_hash,
        )

    monkeypatch.setattr(AuthRepository, "compare_and_set_password_hash", reset_before_compare)
    client = TestClient(create_app())

    stale_login = client.post(
        "/auth/login",
        json={"username": "legacy-user", "password": "old-password"},
    )
    assert stale_login.status_code == 401
    assert race["reset_committed"] is True
    assert verify_password("replacement-password", _stored_password_hash(db_path))
    assert _session_count(db_path) == 0

    current_login = client.post(
        "/auth/login",
        json={"username": "legacy-user", "password": "replacement-password"},
    )
    assert current_login.status_code == 200
    assert _session_count(db_path) == 1
    engine.dispose()


def test_failed_login_transaction_rolls_back_hash_upgrade_and_session(
    tmp_path: Path, monkeypatch
) -> None:
    db_path = tmp_path / "rollback-password-upgrade.db"
    legacy_hash = _legacy_pbkdf2_hash("old-password")
    _setup_legacy_actor(db_path, monkeypatch, legacy_hash)
    original_create_session = AuthRepository.create_session

    def fail_after_session_flush(
        repository: AuthRepository,
        *,
        actor_id: int,
        owner_scope_id: int,
    ) -> AuthSession:
        original_create_session(repository, actor_id=actor_id, owner_scope_id=owner_scope_id)
        raise RuntimeError("simulated failure before login transaction commit")

    monkeypatch.setattr(AuthRepository, "create_session", fail_after_session_flush)
    client = TestClient(create_app(), raise_server_exceptions=False)
    response = client.post(
        "/auth/login",
        json={"username": "legacy-user", "password": "old-password"},
    )

    assert response.status_code == 500
    assert _stored_password_hash(db_path) == legacy_hash
    assert _session_count(db_path) == 0
