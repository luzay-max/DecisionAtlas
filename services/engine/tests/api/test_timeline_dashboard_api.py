from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.models import Artifact, Decision, ImportJob, Workspace
from app.main import create_app


def _seed_dashboard_fixture(db_path: Path) -> None:
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        workspace = Workspace(slug="imported-workspace", name="Imported", repo_url="https://github.com/org/repo")
        session.add(workspace)
        session.flush()
        session.add_all(
            [
                Artifact(
                    workspace_id=workspace.id,
                    type="issue",
                    source_id="1",
                    repo="org/repo",
                    title="Issue A",
                    content="Issue body",
                    author="alice",
                    url="https://github.com/org/repo/issues/1",
                    timestamp=None,
                    metadata_json=None,
                ),
                Decision(
                    workspace_id=workspace.id,
                    title="Use Redis Cache",
                    status="active",
                    review_state="accepted",
                    problem="Latency too high",
                    context=None,
                    constraints=None,
                    chosen_option="Use Redis as cache only",
                    tradeoffs="Extra dependency",
                    confidence=0.9,
                ),
                Decision(
                    workspace_id=workspace.id,
                    title="Use Queue",
                    status="active",
                    review_state="candidate",
                    problem="Sync calls too slow",
                    context=None,
                    constraints=None,
                    chosen_option="Use queue",
                    tradeoffs="More infra",
                    confidence=0.6,
                ),
            ]
        )
        session.add(
            ImportJob(
                job_id="job-123",
                workspace_id=workspace.id,
                repo="org/repo",
                mode="full",
                status="succeeded",
                imported_count=5,
                summary_json={
                    "artifact_counts": {"issue": 1, "pr": 1, "commit": 2, "doc": 1},
                    "document_summary": {
                        "selected": 2,
                        "imported": 1,
                        "skipped": {"outside_high_signal_paths": 4, "non_markdown": 6, "generated_or_vendor_path": 1},
                    },
                },
            )
        )
        session.commit()


def test_timeline_returns_accepted_decisions(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "timeline.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    _seed_dashboard_fixture(db_path)

    client = TestClient(create_app())
    response = client.get("/timeline", params={"workspace_slug": "imported-workspace"})

    assert response.status_code == 200
    body = response.json()
    assert body["workspace_mode"] == "imported"
    assert len(body["items"]) == 1
    assert body["items"][0]["title"] == "Use Redis Cache"


def test_dashboard_summary_returns_counts(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "dashboard.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    _seed_dashboard_fixture(db_path)

    client = TestClient(create_app())
    response = client.get("/dashboard/summary", params={"workspace_slug": "imported-workspace"})

    assert response.status_code == 200
    body = response.json()
    assert body["workspace_mode"] == "imported"
    assert "source_summary" in body
    assert body["artifact_count"] == 1
    assert body["decision_counts"]["accepted"] == 1
    assert body["decision_counts"]["candidate"] == 1
    assert body["latest_import"]["summary"]["artifact_counts"]["doc"] == 1
