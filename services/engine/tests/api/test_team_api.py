from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.auth import SESSION_HEADER
from app.db.models import Decision, Workspace
from app.main import create_app
from app.repositories.auth import AuthRepository, hash_password


def _upgrade(db_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")


def _create_actor_session(db_path: Path, *, username: str, role: str, scope_key: str = "team-alpha") -> str:
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        repo = AuthRepository(session)
        scope = repo.get_scope_by_key(scope_key)
        if scope is None:
            scope = repo.create_scope(scope_key=scope_key, display_name=scope_key.title(), scope_type="team")
        actor = repo.get_actor_by_username(username)
        if actor is None:
            actor = repo.create_actor(
                username=username,
                password_hash=hash_password("password123"),
                display_name=username.title(),
            )
        repo.ensure_membership(actor_id=actor.id, owner_scope_id=scope.id, role=role)
        auth_session = repo.create_session(actor_id=actor.id, owner_scope_id=scope.id)
        session.commit()
        return auth_session.session_token


def _seed_workspace(db_path: Path) -> None:
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        workspace = Workspace(
            slug="team-alpha-workspace",
            name="Team Alpha",
            repo_url="https://github.com/org/repo",
            owner_scope="team-alpha",
        )
        session.add(workspace)
        session.flush()
        session.add(
            Decision(
                workspace_id=workspace.id,
                title="Use Redis Cache",
                status="active",
                review_state="candidate",
                problem="Latency too high",
                chosen_option="Use Redis",
                tradeoffs="Extra dependency",
                confidence=0.8,
            )
        )
        session.commit()


def test_admin_can_manage_team_accounts_and_viewer_cannot(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "team-accounts.db"
    _upgrade(db_path, monkeypatch)
    admin_token = _create_actor_session(db_path, username="admin-user", role="admin")
    viewer_token = _create_actor_session(db_path, username="viewer-user", role="viewer")

    client = TestClient(create_app())
    denied = client.post(
        "/team/accounts",
        headers={SESSION_HEADER: viewer_token},
        json={"username": "reviewer-user", "password": "password123", "role": "reviewer"},
    )
    assert denied.status_code == 403

    created = client.post(
        "/team/accounts",
        headers={SESSION_HEADER: admin_token},
        json={"username": "reviewer-user", "password": "password123", "role": "reviewer"},
    )
    assert created.status_code == 200
    account = created.json()["account"]
    assert account["username"] == "reviewer-user"
    assert account["role"] == "reviewer"
    assert account["status"] == "active"

    listed = client.get("/team/accounts", headers={SESSION_HEADER: admin_token})
    assert listed.status_code == 200
    assert {item["username"] for item in listed.json()["accounts"]} >= {"admin-user", "viewer-user", "reviewer-user"}

    disabled = client.post(f"/team/accounts/{account['id']}/disable", headers={SESSION_HEADER: admin_token})
    assert disabled.status_code == 200
    assert disabled.json()["account"]["status"] == "disabled"


def test_workspace_membership_overrides_scope_role_for_review(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "team-workspace-members.db"
    _upgrade(db_path, monkeypatch)
    _seed_workspace(db_path)
    admin_token = _create_actor_session(db_path, username="admin-user", role="admin")
    reviewer_token = _create_actor_session(db_path, username="reviewer-user", role="reviewer")

    client = TestClient(create_app())
    reviewer_before_override = client.post(
        "/decisions/1/review",
        headers={SESSION_HEADER: reviewer_token},
        json={"review_state": "accepted"},
    )
    assert reviewer_before_override.status_code == 200

    reset_candidate = client.post(
        "/decisions/1/review",
        headers={SESSION_HEADER: admin_token},
        json={"review_state": "candidate"},
    )
    assert reset_candidate.status_code == 200

    accounts = client.get("/team/accounts", headers={SESSION_HEADER: admin_token}).json()["accounts"]
    reviewer_id = next(item["id"] for item in accounts if item["username"] == "reviewer-user")

    assigned_viewer = client.put(
        f"/team/workspaces/team-alpha-workspace/members/{reviewer_id}",
        headers={SESSION_HEADER: admin_token},
        json={"role": "viewer"},
    )
    assert assigned_viewer.status_code == 200

    reviewer_after_override = client.post(
        "/decisions/1/review",
        headers={SESSION_HEADER: reviewer_token},
        json={"review_state": "accepted"},
    )
    assert reviewer_after_override.status_code == 403

    assigned_reviewer = client.put(
        f"/team/workspaces/team-alpha-workspace/members/{reviewer_id}",
        headers={SESSION_HEADER: admin_token},
        json={"role": "reviewer"},
    )
    assert assigned_reviewer.status_code == 200

    reviewer_restored = client.post(
        "/decisions/1/review",
        headers={SESSION_HEADER: reviewer_token},
        json={"review_state": "accepted"},
    )
    assert reviewer_restored.status_code == 200
