from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.models import Workspace
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

    def fake_queue_github_import(*, workspace_slug: str, repo: str, mode: str):
        return {"job_id": "job-123", "repo": repo, "mode": mode, "status": "queued", "imported_count": 0}

    def fake_run_github_import(**kwargs):
        scheduled.append(kwargs)
        return {"job_id": kwargs["job_id"], "repo": kwargs["repo"], "mode": kwargs["mode"], "status": "succeeded", "imported_count": 7}

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
        "repo": "org/repo",
        "mode": "full",
        "status": "queued",
        "imported_count": 0,
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
        return {"job_id": job_id, "repo": "org/repo", "mode": "full", "status": "succeeded", "imported_count": 9}

    monkeypatch.setattr("app.api.imports.get_import_job_status", fake_get_import_job_status)

    client = TestClient(create_app())
    response = client.get("/imports/job-123")

    assert response.status_code == 200
    assert response.json()["job_id"] == "job-123"
