from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.auth import SESSION_HEADER
from app.db.models import Actor, Decision, Workspace
from app.main import create_app
from app.repositories.auth import AuthRepository, hash_password


def _upgrade(db_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")


def _create_actor_session(
    db_path: Path,
    *,
    username: str,
    role: str,
    scope_key: str = "team-alpha",
    display_name: str | None = None,
) -> str:
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        repo = AuthRepository(session)
        scope = repo.get_scope_by_key(scope_key)
        if scope is None:
            scope = repo.create_scope(scope_key=scope_key, display_name=display_name or scope_key.title(), scope_type="team")
        actor = repo.get_actor_by_username(username)
        if actor is None:
            actor = repo.create_actor(
                username=username,
                password_hash=hash_password("password123"),
                display_name=display_name or username.title(),
            )
        repo.ensure_membership(actor_id=actor.id, owner_scope_id=scope.id, role=role)
        auth_session = repo.create_session(actor_id=actor.id, owner_scope_id=scope.id)
        session.commit()
        return auth_session.session_token


def test_auth_bootstrap_returns_session_and_scope(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "auth-bootstrap.db"
    _upgrade(db_path, monkeypatch)

    client = TestClient(create_app())
    bootstrap = client.post("/auth/bootstrap")

    assert bootstrap.status_code == 200
    payload = bootstrap.json()
    assert payload["session_token"]
    assert payload["actor"]["username"] == "local-admin"
    assert payload["current_owner_scope"] == "local-default"
    assert payload["role"] == "admin"

    session_response = client.get("/auth/session", headers={SESSION_HEADER: payload["session_token"]})
    assert session_response.status_code == 200
    session_payload = session_response.json()
    assert session_payload["actor"]["bootstrap"] is True
    assert session_payload["current_owner_scope"] == "local-default"
    assert session_payload["role"] == "admin"


def test_import_requires_admin_role(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "auth-import-role.db"
    _upgrade(db_path, monkeypatch)
    viewer_token = _create_actor_session(db_path, username="viewer-user", role="viewer")

    client = TestClient(create_app())
    response = client.post(
        "/imports/github",
        headers={SESSION_HEADER: viewer_token},
        json={"repo": "org/repo", "mode": "full"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden"


def test_disabled_actor_cannot_login_or_recover_existing_session(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "auth-disabled.db"
    _upgrade(db_path, monkeypatch)
    disabled_token = _create_actor_session(db_path, username="disabled-user", role="viewer")

    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        actor = session.query(Actor).filter_by(username="disabled-user").one()
        actor.status = "disabled"
        session.commit()

    client = TestClient(create_app())
    session_response = client.get("/auth/session", headers={SESSION_HEADER: disabled_token})
    assert session_response.status_code == 401
    assert session_response.json()["detail"] == "User account is disabled"

    login_response = client.post(
        "/auth/login",
        json={"username": "disabled-user", "password": "password123"},
    )
    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "User account is disabled"


def test_reviewer_can_review_but_viewer_cannot(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "auth-review-role.db"
    _upgrade(db_path, monkeypatch)
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
                context=None,
                constraints=None,
                chosen_option="Use Redis",
                tradeoffs="Extra dependency",
                confidence=0.8,
            )
        )
        session.commit()

    viewer_token = _create_actor_session(db_path, username="viewer-user", role="viewer")
    reviewer_token = _create_actor_session(db_path, username="reviewer-user", role="reviewer")

    client = TestClient(create_app())
    viewer_response = client.post(
        "/decisions/1/review",
        headers={SESSION_HEADER: viewer_token},
        json={"review_state": "accepted"},
    )
    assert viewer_response.status_code == 403

    reviewer_response = client.post(
        "/decisions/1/review",
        headers={SESSION_HEADER: reviewer_token},
        json={"review_state": "accepted"},
    )
    assert reviewer_response.status_code == 200
    assert reviewer_response.json()["review_state"] == "accepted"


def test_scope_mismatch_hides_workspace_reads(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "auth-scope-mismatch.db"
    _upgrade(db_path, monkeypatch)
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        session.add(
            Workspace(
                slug="team-beta-workspace",
                name="Team Beta",
                repo_url="https://github.com/org/repo",
                owner_scope="team-beta",
            )
        )
        session.commit()

    alpha_token = _create_actor_session(db_path, username="alpha-user", role="viewer", scope_key="team-alpha")
    client = TestClient(create_app())
    response = client.get(
        "/dashboard/summary",
        headers={SESSION_HEADER: alpha_token},
        params={"workspace_slug": "team-beta-workspace"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Workspace not found"


def test_drift_evaluate_requires_reviewer_role(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "auth-drift-role.db"
    _upgrade(db_path, monkeypatch)
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        workspace = Workspace(
            slug="team-alpha-workspace",
            name="Team Alpha",
            repo_url="https://github.com/org/repo",
            owner_scope="team-alpha",
        )
        session.add(workspace)
        session.commit()

    viewer_token = _create_actor_session(db_path, username="viewer-user", role="viewer")
    reviewer_token = _create_actor_session(db_path, username="reviewer-user", role="reviewer")

    monkeypatch.setattr("app.api.drift.build_runtime_providers", lambda: SimpleNamespace(embedder=None))

    class _FakeResult:
        workspace_slug = "team-alpha-workspace"
        evaluated_rules = 1
        created_alerts = 0

    class _FakeEvaluator:
        def __init__(self, session, embedder=None) -> None:
            self.session = session
            self.embedder = embedder

        def evaluate_workspace(self, workspace_slug: str):
            return _FakeResult()

    monkeypatch.setattr("app.api.drift.DriftEvaluator", _FakeEvaluator)

    client = TestClient(create_app())
    viewer_response = client.post(
        "/drift/evaluate",
        headers={SESSION_HEADER: viewer_token},
        json={"workspace_slug": "team-alpha-workspace"},
    )
    assert viewer_response.status_code == 403

    reviewer_response = client.post(
        "/drift/evaluate",
        headers={SESSION_HEADER: reviewer_token},
        json={"workspace_slug": "team-alpha-workspace"},
    )
    assert reviewer_response.status_code == 200
    assert reviewer_response.json()["status"] == "ok"
