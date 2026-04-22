from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.models import ImportJob, Workspace
from app.main import create_app


def test_post_imports_github_returns_job_id(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "api.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")

    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        session.add(Workspace(slug="demo-workspace", name="Demo", repo_url="https://github.com/org/repo"))
        session.commit()

    scheduled: list[dict] = []

    def fake_queue_github_import(*, workspace_slug: str | None, repo: str, mode: str, **kwargs):
        return {
            "job_id": "job-123",
            "workspace_slug": workspace_slug,
            "repo": repo,
            "mode": mode,
            "status": "queued",
            "sync_origin": "manual_full",
            "imported_count": 0,
            "summary": {"stage": "queued"},
        }

    def fake_run_github_import(**kwargs):
        scheduled.append(kwargs)
        return {
            "job_id": kwargs["job_id"],
            "workspace_slug": kwargs["workspace_slug"],
            "repo": kwargs["repo"],
            "mode": kwargs["mode"],
            "status": "succeeded",
            "imported_count": 7,
            "summary": {
                "stage": "completed",
                "outcome": "ok",
                "artifact_counts": {"issue": 1, "pr": 1, "commit": 3, "doc": 2},
                "document_summary": {
                    "selected": 3,
                    "imported": 2,
                    "skipped": {"outside_high_signal_paths": 4, "non_markdown": 8, "generated_or_vendor_path": 1},
                },
            },
        }

    monkeypatch.setattr("app.api.imports.queue_github_import", fake_queue_github_import)
    monkeypatch.setattr("app.api.imports.run_github_import", fake_run_github_import)

    client = TestClient(create_app())

    response = client.post(
        "/imports/github",
        json={"workspace_slug": "demo-workspace", "repo": "org/repo", "mode": "full"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "job_id": "job-123",
        "workspace_slug": "demo-workspace",
        "repo": "org/repo",
        "mode": "full",
        "status": "queued",
        "sync_origin": "manual_full",
        "imported_count": 0,
        "summary": {"stage": "queued"},
    }
    assert scheduled == [
        {
            "job_id": "job-123",
            "workspace_slug": "demo-workspace",
            "repo": "org/repo",
            "mode": "full",
        }
    ]


def test_get_import_job_status_returns_job(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "job-status.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")

    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        workspace = Workspace(slug="imported-workspace", name="Imported", repo_url="https://github.com/org/repo")
        session.add(workspace)
        session.flush()
        session.add(
            ImportJob(
                job_id="job-123",
                workspace_id=workspace.id,
                repo="org/repo",
                mode="full",
                status="queued",
                imported_count=0,
            )
        )
        session.commit()

    def fake_get_import_job_status(job_id: str):
        return {
            "job_id": job_id,
            "workspace_slug": "imported-workspace",
            "repo": "org/repo",
            "mode": "full",
            "status": "succeeded",
            "imported_count": 9,
            "summary": {
                "stage": "completed",
                "outcome": "insufficient_evidence",
                "artifact_counts": {"issue": 1, "pr": 2, "commit": 4, "doc": 2},
                "document_summary": {
                    "selected": 2,
                    "imported": 2,
                    "skipped": {"outside_high_signal_paths": 6, "non_markdown": 9, "generated_or_vendor_path": 1},
                },
            },
        }

    monkeypatch.setattr("app.api.imports.get_import_job_status", fake_get_import_job_status)

    client = TestClient(create_app())
    response = client.get("/imports/job-123")

    assert response.status_code == 200
    assert response.json()["job_id"] == "job-123"
    assert response.json()["workspace_slug"] == "imported-workspace"
    assert response.json()["summary"]["artifact_counts"]["doc"] == 2
    assert response.json()["summary"]["outcome"] == "insufficient_evidence"


def test_post_imports_github_creates_live_workspace_when_slug_missing(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "live-import.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")

    scheduled: list[dict] = []

    def fake_queue_github_import(*, workspace_slug: str | None, repo: str, mode: str, **kwargs):
        return {
            "job_id": "job-live",
            "workspace_slug": "github-org-repo",
            "repo": repo,
            "mode": mode,
            "status": "queued",
            "sync_origin": "manual_full",
            "imported_count": 0,
            "summary": {"stage": "queued"},
        }

    def fake_run_github_import(**kwargs):
        scheduled.append(kwargs)
        return {"job_id": kwargs["job_id"]}

    monkeypatch.setattr("app.api.imports.queue_github_import", fake_queue_github_import)
    monkeypatch.setattr("app.api.imports.run_github_import", fake_run_github_import)

    client = TestClient(create_app())
    response = client.post("/imports/github", json={"repo": "org/repo", "mode": "full"})

    assert response.status_code == 200
    assert response.json()["workspace_slug"] == "github-org-repo"
    assert scheduled == [
        {
            "job_id": "job-live",
            "workspace_slug": "github-org-repo",
            "repo": "org/repo",
            "mode": "full",
        }
    ]


def test_post_imports_github_rejects_repo_workspace_mismatch(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "mismatch-import.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")

    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        session.add(
            Workspace(
                slug="demo-workspace",
                name="Demo",
                repo_url="https://github.com/original/repo",
            )
        )
        session.commit()

    client = TestClient(create_app())
    response = client.post(
        "/imports/github",
        json={"workspace_slug": "demo-workspace", "repo": "other/repo", "mode": "full"},
    )

    assert response.status_code == 400
    assert "cannot import other/repo" in response.json()["detail"]


def test_get_imports_lookup_reports_existing_workspace_and_latest_job(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "lookup-import.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")

    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        workspace = Workspace(slug="github-org-repo", name="org/repo", repo_url="https://github.com/org/repo")
        session.add(workspace)
        session.flush()
        session.add(
            ImportJob(
                job_id="job-old",
                workspace_id=workspace.id,
                repo="org/repo",
                mode="full",
                status="succeeded",
                imported_count=8,
                summary_json={"stage": "completed", "outcome": "ok"},
            )
        )
        session.commit()

    client = TestClient(create_app())
    response = client.get("/imports/lookup", params={"repo": "org/repo"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["workspace_exists"] is True
    assert payload["workspace_slug"] == "github-org-repo"
    assert payload["has_successful_import"] is True
    assert payload["can_incremental_sync"] is True
    assert payload["latest_import"]["job_id"] == "job-old"
    assert payload["access_source_type"] == "public"
    assert payload["access_source_label"] == "Public GitHub access"


def test_bind_installation_marks_workspace_as_installation_backed(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "bind-installation.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")

    client = TestClient(create_app())
    response = client.post(
        "/imports/github/installations/bind",
        json={
            "repo": "org/repo",
            "installation_id": "12345",
            "account_login": "decisionatlas-dev",
            "account_type": "Organization",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["workspace_exists"] is True
    assert body["workspace_slug"] == "github-org-repo"
    assert body["access_source_type"] == "github_app_installation"
    assert body["access_source_label"] == "GitHub App installation #12345"


def test_bind_private_access_marks_workspace_as_token_backed(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "bind-private-access.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")

    monkeypatch.setattr(
        "app.jobs.import_jobs.GitHubClient.get_repository_metadata",
        lambda self, repo: {"full_name": repo, "private": True, "default_branch": "main"},
    )

    client = TestClient(create_app())
    response = client.post(
        "/imports/github/private-access/bind",
        json={
            "repo": "org/private-repo",
            "token": "ghp-private-token",
            "source_ref": "org/private-repo",
            "source_label": "team private repo",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["workspace_exists"] is True
    assert body["workspace_slug"] == "github-org-private-repo"
    assert body["repo_private"] is True
    assert body["access_source_type"] == "github_token"
    assert body["access_source_status"] == "authorized"
    assert "Private GitHub source team private repo" == body["access_source_label"]


def test_post_imports_github_returns_credential_required_for_private_repo_without_source(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "private-import-required.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")

    request = httpx.Request("GET", "https://api.github.com/repos/org/private-repo")
    response = httpx.Response(404, request=request, json={"message": "Not Found"})

    def fake_get_repository_metadata(self, repo: str):
        raise httpx.HTTPStatusError("not found", request=request, response=response)

    monkeypatch.setattr("app.jobs.import_jobs.GitHubClient.get_repository_metadata", fake_get_repository_metadata)

    client = TestClient(create_app())
    import_response = client.post("/imports/github", json={"repo": "org/private-repo", "mode": "full"})

    assert import_response.status_code == 403
    assert "not publicly reachable" in import_response.json()["detail"]


def test_lookup_reports_private_access_requirement_when_repo_is_not_publicly_reachable(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "private-lookup-required.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")

    request = httpx.Request("GET", "https://api.github.com/repos/org/private-repo")
    response = httpx.Response(404, request=request, json={"message": "Not Found"})

    def fake_get_repository_metadata(self, repo: str):
        raise httpx.HTTPStatusError("not found", request=request, response=response)

    monkeypatch.setattr("app.jobs.import_jobs.GitHubClient.get_repository_metadata", fake_get_repository_metadata)

    client = TestClient(create_app())
    lookup_response = client.get("/imports/lookup", params={"repo": "org/private-repo"})

    assert lookup_response.status_code == 200
    body = lookup_response.json()
    assert body["workspace_exists"] is False
    assert body["access_requirement"] == "credential_required"
    assert "not publicly reachable" in body["access_requirement_detail"]


def test_webhook_enqueues_incremental_sync_for_installation_backed_workspace(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "webhook-import.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")

    client = TestClient(create_app())
    bind_response = client.post(
        "/imports/github/installations/bind",
        json={
            "repo": "org/repo",
            "installation_id": "12345",
        },
    )
    assert bind_response.status_code == 200
    monkeypatch.setattr(
        "app.jobs.import_jobs.GitHubClient.get_repository_metadata",
        lambda self, repo: {"full_name": repo, "private": False, "default_branch": "main"},
    )

    scheduled: list[dict] = []

    def fake_run_github_import(**kwargs):
        scheduled.append(kwargs)
        return {"job_id": kwargs["job_id"]}

    monkeypatch.setattr("app.api.imports.run_github_import", fake_run_github_import)

    response = client.post(
        "/imports/github/webhook",
        headers={
            "X-GitHub-Event": "pull_request",
            "X-GitHub-Delivery": "delivery-1",
        },
        json={
            "action": "opened",
            "installation": {"id": 12345},
            "repository": {"full_name": "org/repo"},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "queued"
    assert body["workspace_slug"] == "github-org-repo"
    assert body["job_id"]
    assert scheduled == [
        {
            "job_id": body["job_id"],
            "workspace_slug": "github-org-repo",
            "repo": "org/repo",
            "mode": "since_last_sync",
        }
    ]
