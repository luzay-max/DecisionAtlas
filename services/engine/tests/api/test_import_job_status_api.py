from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.models import ImportJob, Workspace
from app.main import create_app


def test_import_job_status_returns_summary(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "import-job-status.db"
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
                status="succeeded",
                imported_count=9,
                summary_json={
                    "artifact_counts": {"issue": 1, "pr": 2, "commit": 4, "doc": 2},
                    "document_summary": {
                        "selected": 3,
                        "imported": 2,
                        "skipped": {"outside_high_signal_paths": 6, "non_markdown": 9, "generated_or_vendor_path": 1},
                    },
                },
            )
        )
        session.commit()

    client = TestClient(create_app())
    response = client.get("/imports/job-123")

    assert response.status_code == 200
    body = response.json()
    assert body["summary"]["artifact_counts"]["doc"] == 2
    assert body["summary"]["document_summary"]["skipped"]["non_markdown"] == 9
