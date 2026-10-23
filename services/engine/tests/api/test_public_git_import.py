"""Public GitLab/Gitee import boundary tests; no live tokens or network."""
from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.auth import SESSION_HEADER
from app.db.models import ImportJob, Workspace
from app.ingest.git_provider_clients import GitProviderError
from app.jobs.public_git_import import normalize_public_repo, queue_public_git_import
from app.main import create_app
from app.repositories.auth import AuthRepository, hash_password


def _db(tmp_path: Path, monkeypatch) -> Path:
    path = tmp_path / "git-provider-import.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{path}")
    conf = Config("alembic.ini")
    conf.set_main_option("sqlalchemy.url", f"sqlite:///{path}")
    command.upgrade(conf, "head")
    return path


def _auth(path: Path, *, name: str, role: str, scope: str = "local-default") -> str:
    engine = create_engine(f"sqlite:///{path}")
    with Session(engine) as session:
        auth = AuthRepository(session)
        owner = auth.get_scope_by_key(scope)
        if owner is None:
            owner = auth.create_scope(scope_key=scope, display_name=scope, scope_type="team")
        actor = auth.create_actor(username=name, password_hash=hash_password("test-password"), display_name=name)
        auth.ensure_membership(actor_id=actor.id, owner_scope_id=owner.id, role=role)
        token = auth.create_session(actor_id=actor.id, owner_scope_id=owner.id).session_token
        session.commit()
        return token


@pytest.mark.parametrize(("provider", "value", "expected"), [
    ("gitlab", "team/subgroup/repo", "team/subgroup/repo"),
    ("gitlab", "https://gitlab.com/team/subgroup/repo.git", "team/subgroup/repo"),
    ("gitee", "team/repo", "team/repo"),
    ("gitee", "https://gitee.com/team/repo", "team/repo"),
])
def test_public_repository_normalization(provider: str, value: str, expected: str):
    assert normalize_public_repo(provider=provider, repo=value)[0] == expected


@pytest.mark.parametrize(("provider", "value"), [
    ("gitee", "https://gitlab.com/team/repo"),
    ("gitlab", "https://gitlab.example.org/team/repo"),
    ("gitee", "http://gitee.com/team/repo"),
    ("gitlab", "https://gitlab.com@evil.example/a/b"),
    ("gitlab", "https://gitlab.com:8443/a/b"),
    ("gitlab", "https://gitlab.com:badport/a/b"),
    ("gitlab", "https://gitlab.com/a/b?token=secret"),
    ("gitlab", "https://gitlab.com/a/b#anchor"),
    ("gitee", "a/b/c"),
    ("gitlab", "../etc/passwd"),
    ("gitlab", "org//repo"),
    ("gitee", "team/repo;evil"),
    ("github", "org/repo"),
])
def test_public_repo_rejects_untrusted_sources(provider, value):
    with pytest.raises((GitProviderError, ValueError)):
        normalize_public_repo(provider=provider, repo=value)


def test_public_import_queue_is_isolated_and_deduplicated(tmp_path: Path, monkeypatch):
    path = _db(tmp_path, monkeypatch)
    first = queue_public_git_import(
        provider="gitlab", repo="https://gitlab.com/company/group/docs",
        mode="full", owner_scope="local-default",
    )
    assert first["status"] == "queued"
    assert first["repo"] == "company/group/docs"
    assert first["workspace_slug"].startswith("gitlab-")
    with pytest.raises(Exception, match="already queued or running"):
        queue_public_git_import(
            provider="gitlab", repo="company/group/docs",
            mode="full", owner_scope="local-default",
        )
    second = queue_public_git_import(
        provider="gitlab", repo="company/group/docs",
        mode="full", owner_scope="company-team",
    )
    other_provider = queue_public_git_import(
        provider="gitee", repo="company/docs",
        mode="full", owner_scope="local-default",
    )
    assert len({first["workspace_slug"], second["workspace_slug"], other_provider["workspace_slug"]}) == 3
    with pytest.raises(GitProviderError, match="not available"):
        queue_public_git_import(
            provider="gitlab", repo="company/group/docs", mode="full",
            owner_scope="company-team", workspace_slug=first["workspace_slug"],
        )
    engine = create_engine(f"sqlite:///{path}")
    with Session(engine) as session:
        workspaces = session.scalars(select(Workspace)).all()
        jobs = session.scalars(select(ImportJob)).all()
        assert len(workspaces) == 3
        assert len(jobs) == 3
        assert any(w.repo_identity == "gitlab:company/group/docs" for w in workspaces)
        assert any(w.access_source_type == "gitee_public" for w in workspaces)


def test_public_import_rejects_reusing_foreign_github_workspace(tmp_path: Path, monkeypatch):
    path = _db(tmp_path, monkeypatch)
    engine = create_engine(f"sqlite:///{path}")
    with Session(engine) as session:
        session.add(Workspace(
            slug="github-existing", name="GitHub",
            repo_url="https://github.com/company/docs", repo_identity="company/docs",
            owner_scope="local-default", access_source_type="public",
        ))
        session.commit()
    with pytest.raises(GitProviderError, match="not available"):
        queue_public_git_import(
            provider="gitee", repo="company/docs", mode="full",
            owner_scope="local-default", workspace_slug="github-existing",
        )


def test_public_import_route_requires_admin_and_never_accepts_tokens(tmp_path: Path, monkeypatch):
    path = _db(tmp_path, monkeypatch)
    # CI enables demo auto-bootstrap; disable it explicitly so this test
    # verifies real session and role authorization without changing demo defaults.
    monkeypatch.setenv("AUTH_AUTO_BOOTSTRAP_LOCAL", "false")
    admin = _auth(path, name="public-import-admin", role="admin")
    viewer = _auth(path, name="public-import-viewer", role="viewer")
    invocations: list[dict] = []

    def fake_queue(**kwargs):
        invocations.append(kwargs)
        return {
            "job_id": "job-public", "workspace_slug": "gitlab-team-repo",
            "repo": "team/repo", "mode": "full", "status": "queued",
        }

    def fake_runner(**kwargs):
        invocations.append({"runner": kwargs})
        return {"status": "succeeded"}

    monkeypatch.setattr("app.api.imports.queue_public_git_import", fake_queue)
    monkeypatch.setattr("app.api.imports.run_github_import", fake_runner)
    app = TestClient(create_app())
    data = {"provider": "gitlab", "repo": "team/repo", "mode": "full"}

    assert app.post("/imports/git-sources/import", json=data).status_code == 401
    assert app.post(
        "/imports/git-sources/import", json=data, headers={SESSION_HEADER: viewer},
    ).status_code == 403
    assert app.post(
        "/imports/git-sources/import",
        json={**data, "token": "secret"},
        headers={SESSION_HEADER: admin},
    ).status_code == 422

    response = app.post("/imports/git-sources/import", json=data, headers={SESSION_HEADER: admin})
    assert response.status_code == 200
    assert response.json()["job_id"] == "job-public"
    assert invocations[0] == {
        "provider": "gitlab", "repo": "team/repo", "mode": "full",
        "owner_scope": "local-default", "workspace_slug": None,
    }
    assert invocations[1]["runner"]["provider"] == "gitlab"
    assert invocations[1]["runner"]["repo"] == "team/repo"



@pytest.mark.parametrize(("provider", "visibility"), [
    ("gitlab", {"visibility": "private"}),
    ("gitee", {"private": True}),
    ("gitlab", {}),
    ("gitee", {}),
])
def test_import_worker_fails_closed_for_private_or_unknown_repository(
    tmp_path: Path, monkeypatch, provider: str, visibility: dict,
) -> None:
    from app.jobs import import_jobs

    _db(tmp_path, monkeypatch)
    job = queue_public_git_import(
        provider=provider, repo="group/repo", mode="full",
        owner_scope="local-default",
    )

    class StubClient:
        def __init__(self, *, max_pages: int):
            pass

        def get_repository_metadata(self, repo: str) -> dict:
            return visibility

        def fetch_issues(self, repo: str, *, since=None):
            pytest.fail("private repository must not be fetched")

    monkeypatch.setattr(import_jobs, "GitLabClient" if provider == "gitlab" else "GiteeClient", StubClient)
    result = import_jobs.run_github_import(
        job_id=job["job_id"], workspace_slug=job["workspace_slug"],
        repo="group/repo", mode="full", provider=provider,
    )
    assert result["status"] == "failed"
    assert result["summary"]["failure_category"] == "provider_access_failure"
    assert "not public" in result["error_message"]


def test_import_worker_rejects_mismatched_workspace_provider_before_network(
    tmp_path: Path, monkeypatch,
) -> None:
    from app.jobs import import_jobs

    _db(tmp_path, monkeypatch)
    job = queue_public_git_import(
        provider="gitlab", repo="group/repo", mode="full",
        owner_scope="local-default",
    )

    class NoNetwork:
        def __init__(self, *, max_pages: int):
            pytest.fail("provider client must not be initialized for mismatched job")

    monkeypatch.setattr(import_jobs, "GiteeClient", NoNetwork)
    result = import_jobs.run_github_import(
        job_id=job["job_id"], workspace_slug=job["workspace_slug"],
        repo="group/repo", mode="full", provider="gitee",
    )
    assert result["status"] == "failed"
    assert result["summary"]["failure_category"] == "provider_access_failure"
