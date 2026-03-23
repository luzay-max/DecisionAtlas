from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.models import Artifact, Decision, DriftAlert, ImportJob, Workspace
from app.main import create_app


def _seed_drift_fixture(db_path: Path) -> None:
    engine = create_engine(f"sqlite:///{db_path}")
    baseline = datetime(2026, 3, 18, 9, 0, 0)
    with Session(engine) as session:
        workspace = Workspace(slug="imported-workspace", name="Imported", repo_url="https://github.com/org/repo")
        session.add(workspace)
        session.flush()
        artifact = Artifact(
            workspace_id=workspace.id,
            type="pull_request",
            source_id="2",
            repo="org/repo",
            title="Persist sessions in Redis",
            content="Persist session state in Redis as the primary database for auth reads.",
            author="bob",
            url="https://github.com/org/repo/pull/2",
            timestamp=baseline + timedelta(days=1),
            metadata_json=None,
        )
        decision = Decision(
            workspace_id=workspace.id,
            title="Use Redis Cache",
            status="active",
            review_state="accepted",
            problem="Latency too high",
            context=None,
            constraints="Redis stays cache-only.",
            chosen_option="Use Redis as cache only and keep PostgreSQL primary.",
            tradeoffs="Extra dependency",
            confidence=0.92,
            created_at=baseline,
            updated_at=baseline,
        )
        session.add_all([artifact, decision])
        session.flush()
        session.add(
            ImportJob(
                job_id="job-drift-1",
                workspace_id=workspace.id,
                repo="org/repo",
                mode="full",
                status="succeeded",
                imported_count=2,
                finished_at=baseline + timedelta(days=1),
                summary_json={
                    "stage": "completed",
                    "outcome": "ok",
                    "drift_evaluation": {
                        "evaluated_at": (baseline + timedelta(days=1, minutes=1)).isoformat(),
                        "evaluated_rules": 1,
                        "created_alerts": 1,
                    },
                },
            )
        )
        session.add(
            DriftAlert(
                workspace_id=workspace.id,
                artifact_id=artifact.id,
                decision_id=decision.id,
                alert_type="possible_drift",
                summary="Accepted decision 'Use Redis Cache' keeps Redis cache-only.",
                status="open",
            )
        )
        session.commit()


def test_list_drift_alerts_returns_joined_context(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "drift-api.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    _seed_drift_fixture(db_path)

    client = TestClient(create_app())
    response = client.get("/drift", params={"workspace_slug": "imported-workspace"})

    assert response.status_code == 200
    body = response.json()
    assert body["workspace_mode"] == "imported"
    assert body["evaluation"]["state"] == "alerts_present"
    assert len(body["alerts"]) == 1
    assert body["alerts"][0]["confidence_label"] == "high"
    assert body["alerts"][0]["artifact"]["title"] == "Persist sessions in Redis"
    assert body["alerts"][0]["decision"]["title"] == "Use Redis Cache"


def test_post_drift_evaluate_returns_counts(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "drift-evaluate-api.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}")
    baseline = datetime(2026, 3, 18, 9, 0, 0)

    with Session(engine) as session:
        workspace = Workspace(slug="imported-workspace", name="Imported", repo_url="https://github.com/org/repo")
        session.add(workspace)
        session.flush()
        session.add(
            Artifact(
                workspace_id=workspace.id,
                type="pull_request",
                source_id="2",
                repo="org/repo",
                title="Persist sessions in Redis",
                content="Persist session state in Redis as the primary database for auth reads.",
                author="bob",
                url="https://github.com/org/repo/pull/2",
                timestamp=baseline + timedelta(days=1),
                metadata_json=None,
            )
        )
        session.add(
            Decision(
                workspace_id=workspace.id,
                title="Use Redis Cache",
                status="active",
                review_state="accepted",
                problem="Latency too high",
                context=None,
                constraints="Redis stays cache-only.",
                chosen_option="Use Redis as cache only and keep PostgreSQL primary.",
                tradeoffs="Extra dependency",
                confidence=0.92,
                created_at=baseline,
                updated_at=baseline,
            )
        )
        session.add(
            ImportJob(
                job_id="job-drift-eval",
                workspace_id=workspace.id,
                repo="org/repo",
                mode="full",
                status="succeeded",
                imported_count=2,
                summary_json={"stage": "completed", "outcome": "ok"},
            )
        )
        session.commit()

    client = TestClient(create_app())
    response = client.post("/drift/evaluate", json={"workspace_slug": "imported-workspace"})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["created_alerts"] == 1
    assert body["evaluation"]["state"] == "alerts_present"
