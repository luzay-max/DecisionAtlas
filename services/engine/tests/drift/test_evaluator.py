from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.models import Artifact, Decision, SourceRef, Workspace
from app.drift.evaluator import DriftEvaluator
from app.repositories.drift_alerts import DriftAlertRepository


def test_evaluator_persists_possible_drift_for_violating_artifact(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "drift.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}")
    baseline = datetime(2026, 3, 18, 9, 0, 0)

    with Session(engine) as session:
        workspace = Workspace(slug="demo-workspace", name="Demo", repo_url="https://github.com/org/repo")
        session.add(workspace)
        session.flush()
        source_artifact = Artifact(
            workspace_id=workspace.id,
            type="issue",
            source_id="1",
            repo="org/repo",
            title="Cache rationale",
            content="Use Redis as cache only because latency is high.",
            author="alice",
            url="https://github.com/org/repo/issues/1",
            timestamp=baseline,
            metadata_json=None,
        )
        violating_artifact = Artifact(
            workspace_id=workspace.id,
            type="pull_request",
            source_id="2",
            repo="org/repo",
            title="Persist sessions in Redis",
            content="This PR will persist session state in Redis as the primary database for auth reads.",
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
        )
        session.add_all([source_artifact, violating_artifact, decision])
        session.flush()
        session.add(
            SourceRef(
                decision_id=decision.id,
                artifact_id=source_artifact.id,
                span_start=0,
                span_end=44,
                quote="Use Redis as cache only because latency is high.",
                url=source_artifact.url,
                relevance_score=0.9,
            )
        )
        session.commit()

    with Session(engine) as session:
        result = DriftEvaluator(session).evaluate_workspace("demo-workspace")
        alerts = DriftAlertRepository(session).list_by_workspace(1)

    assert result.evaluated_rules == 1
    assert result.created_alerts == 1
    assert len(alerts) == 1
    assert alerts[0].alert_type == "possible_drift"
    assert "primary database" in alerts[0].summary.lower()


def test_evaluator_skips_non_violating_artifact(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "drift-clean.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}")
    baseline = datetime(2026, 3, 18, 9, 0, 0)

    with Session(engine) as session:
        workspace = Workspace(slug="demo-workspace", name="Demo", repo_url="https://github.com/org/repo")
        session.add(workspace)
        session.flush()
        session.add(
            Artifact(
                workspace_id=workspace.id,
                type="issue",
                source_id="1",
                repo="org/repo",
                title="Warm cache",
                content="Keep Redis warm and use it as a cache in front of PostgreSQL.",
                author="alice",
                url="https://github.com/org/repo/issues/1",
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
            )
        )
        session.commit()

    with Session(engine) as session:
        result = DriftEvaluator(session).evaluate_workspace("demo-workspace")
        alerts = DriftAlertRepository(session).list_by_workspace(1)

    assert result.created_alerts == 0
    assert alerts == []
