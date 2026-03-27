from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
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

    def fake_queue_github_import(*, workspace_slug: str | None, repo: str, mode: str):
        return {
            "job_id": "job-123",
            "workspace_slug": workspace_slug,
            "repo": repo,
            "mode": mode,
            "status": "queued",
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


def test_get_import_job_status_returns_job(monkeypatch) -> None:
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

    def fake_queue_github_import(*, workspace_slug: str | None, repo: str, mode: str):
        return {
            "job_id": "job-live",
            "workspace_slug": "github-org-repo",
            "repo": repo,
            "mode": mode,
            "status": "queued",
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
