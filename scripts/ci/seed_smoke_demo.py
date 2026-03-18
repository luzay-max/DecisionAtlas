from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import sys

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

ENGINE_DIR = Path(__file__).resolve().parents[2] / "services" / "engine"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from app.config import get_settings
from app.db.models import Artifact, Decision, DriftAlert, SourceRef, Workspace


def seed_smoke_demo() -> None:
    settings = get_settings()
    engine = create_engine(settings.database_url)
    baseline = datetime(2026, 3, 18, 9, 0, 0)

    with Session(engine) as session:
        workspace = session.scalar(select(Workspace).where(Workspace.slug == "demo-workspace"))
        if workspace is None:
            workspace = Workspace(
                slug="demo-workspace",
                name="DecisionAtlas Demo Workspace",
                repo_url="https://github.com/example/example",
            )
            session.add(workspace)
            session.flush()

        issue_artifact = session.scalar(select(Artifact).where(Artifact.source_id == "seed-issue-1"))
        if issue_artifact is None:
            issue_artifact = Artifact(
                workspace_id=workspace.id,
                type="issue",
                source_id="seed-issue-1",
                repo="org/repo",
                title="Redis cache rationale",
                content="We decided to use Redis as cache only because latency mattered.",
                author="alice",
                url="https://github.com/org/repo/issues/1",
                timestamp=baseline,
                metadata_json=None,
            )
            session.add(issue_artifact)
            session.flush()

        accepted_decision = session.scalar(select(Decision).where(Decision.title == "Use Redis Cache"))
        if accepted_decision is None:
            accepted_decision = Decision(
                workspace_id=workspace.id,
                title="Use Redis Cache",
                status="active",
                review_state="accepted",
                problem="Latency too high",
                context="Read load increased",
                constraints="Redis stays cache-only",
                chosen_option="Use Redis as cache only",
                tradeoffs="Extra dependency",
                confidence=0.92,
                created_at=baseline,
            )
            session.add(accepted_decision)
            session.flush()

        source_ref = session.scalar(select(SourceRef).where(SourceRef.decision_id == accepted_decision.id))
        if source_ref is None:
            session.add(
                SourceRef(
                    decision_id=accepted_decision.id,
                    artifact_id=issue_artifact.id,
                    span_start=0,
                    span_end=58,
                    quote="We decided to use Redis as cache only because latency mattered.",
                    url=issue_artifact.url,
                    relevance_score=0.92,
                )
            )

        candidate_decision = session.scalar(select(Decision).where(Decision.title == "Adopt Queue for Async Jobs"))
        if candidate_decision is None:
            session.add(
                Decision(
                    workspace_id=workspace.id,
                    title="Adopt Queue for Async Jobs",
                    status="active",
                    review_state="candidate",
                    problem="Synchronous jobs block requests",
                    context="Need better background processing",
                    constraints=None,
                    chosen_option="Move long-running jobs to a queue",
                    tradeoffs="More operational complexity",
                    confidence=0.78,
                    created_at=baseline + timedelta(hours=2),
                )
            )

        drift_artifact = session.scalar(select(Artifact).where(Artifact.source_id == "seed-pr-2"))
        if drift_artifact is None:
            drift_artifact = Artifact(
                workspace_id=workspace.id,
                type="pull_request",
                source_id="seed-pr-2",
                repo="org/repo",
                title="Persist sessions in Redis",
                content="Persist session state in Redis as the primary database for auth reads.",
                author="bob",
                url="https://github.com/org/repo/pull/2",
                timestamp=baseline + timedelta(days=1),
                metadata_json=None,
            )
            session.add(drift_artifact)
            session.flush()

        drift_alert = session.scalar(
            select(DriftAlert).where(
                DriftAlert.workspace_id == workspace.id,
                DriftAlert.artifact_id == drift_artifact.id,
                DriftAlert.decision_id == accepted_decision.id,
            )
        )
        if drift_alert is None:
            session.add(
                DriftAlert(
                    workspace_id=workspace.id,
                    artifact_id=drift_artifact.id,
                    decision_id=accepted_decision.id,
                    alert_type="possible_drift",
                    summary="Accepted decision 'Use Redis Cache' keeps Redis cache-only.",
                    status="open",
                )
            )

        session.commit()


if __name__ == "__main__":
    seed_smoke_demo()
    print("Seeded smoke demo data.")
