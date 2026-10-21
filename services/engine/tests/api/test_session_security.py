from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.auth import SESSION_HEADER
from app.db.models import Actor, AuthSession
from app.main import create_app
from app.repositories.auth import AuthRepository, hash_password


def _setup(db_path: Path, monkeypatch) -> tuple[str, str, int]:
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(config, "head")
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        repo = AuthRepository(session)
        scope = repo.create_scope(scope_key="team-a", display_name="Team A")
        admin = repo.create_actor(username="admin", password_hash=hash_password("password123"))
        member = repo.create_actor(username="member", password_hash=hash_password("password123"))
        repo.ensure_membership(actor_id=admin.id, owner_scope_id=scope.id, role="admin")
        repo.ensure_membership(actor_id=member.id, owner_scope_id=scope.id, role="viewer")
        admin_token = repo.create_session(actor_id=admin.id, owner_scope_id=scope.id).session_token
        member_token = repo.create_session(actor_id=member.id, owner_scope_id=scope.id).session_token
        member_id = member.id
        session.commit()
    engine.dispose()
    return admin_token, member_token, member_id


@pytest.mark.parametrize("column,ago", [
    ("created_at", timedelta(hours=25)),
    ("last_seen_at", timedelta(minutes=121)),
])
def test_expired_token_is_rejected_even_with_test_bootstrap_enabled(
    tmp_path: Path, monkeypatch, column: str, ago: timedelta
) -> None:
    db_path = tmp_path / f"expired-{column}.db"
    _, member_token, _ = _setup(db_path, monkeypatch)
    monkeypatch.setenv("AUTH_AUTO_BOOTSTRAP_LOCAL", "true")
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        row = session.scalar(select(AuthSession).where(AuthSession.session_token == member_token))
        assert row is not None
        setattr(row, column, datetime.now(UTC) - ago)
        session.commit()
    engine.dispose()
    response = TestClient(create_app()).get("/auth/session", headers={SESSION_HEADER: member_token})
    assert response.status_code == 401


def test_sign_out_revokes_token_and_does_not_bootstrap_on_reuse(tmp_path: Path, monkeypatch) -> None:
    _, token, _ = _setup(tmp_path / "sign-out.db", monkeypatch)
    client = TestClient(create_app())
    assert client.get("/auth/session", headers={SESSION_HEADER: token}).status_code == 200
    assert client.post("/auth/logout", headers={SESSION_HEADER: token}).json() == {"status": "signed_out"}
    assert client.get("/auth/session", headers={SESSION_HEADER: token}).status_code == 401
    assert client.post("/auth/logout", headers={SESSION_HEADER: token}).status_code == 200


def test_password_reset_revokes_all_sessions(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "reset.db"
    admin_token, member_token, member_id = _setup(db_path, monkeypatch)
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        repo = AuthRepository(session)
        member = repo.get_actor(member_id)
        assert member is not None
        scope = repo.get_scope_by_key("team-a")
        assert scope is not None
        second_token = repo.create_session(actor_id=member_id, owner_scope_id=scope.id).session_token
        session.commit()
    engine.dispose()
    client = TestClient(create_app())
    response = client.post(
        f"/team/accounts/{member_id}/reset-password",
        headers={SESSION_HEADER: admin_token},
        json={"password": "new-password-strong"},
    )
    assert response.status_code == 200
    for token in (member_token, second_token):
        assert client.get("/auth/session", headers={SESSION_HEADER: token}).status_code == 401
    assert client.post("/auth/login", json={"username": "member", "password": "password123"}).status_code == 401
    assert client.post("/auth/login", json={"username": "member", "password": "new-password-strong"}).status_code == 200


def test_disabling_account_revokes_sessions(tmp_path: Path, monkeypatch) -> None:
    admin_token, member_token, member_id = _setup(tmp_path / "disabled.db", monkeypatch)
    client = TestClient(create_app())
    response = client.post(
        f"/team/accounts/{member_id}/disable", headers={SESSION_HEADER: admin_token}
    )
    assert response.status_code == 200
    assert client.get("/auth/session", headers={SESSION_HEADER: member_token}).status_code == 401

def test_production_rejects_plaintext_github_token_binding_before_network(monkeypatch) -> None:
    from app.jobs.import_jobs import RepositoryAccessError, bind_github_private_access_source

    monkeypatch.setenv("APP_ENV", "production")
    with pytest.raises(RepositoryAccessError, match="encrypted credential storage"):
        bind_github_private_access_source(repo="org/private", token="do-not-store")
