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
    repo_ref = settings.demo_repo
    repo_url = f"https://github.com/{repo_ref}"

    with Session(engine) as session:
        workspace = session.scalar(select(Workspace).where(Workspace.slug == "demo-workspace"))
        if workspace is None:
            workspace = Workspace(
                slug="demo-workspace",
                name="DecisionAtlas Demo Workspace",
                repo_url=repo_url,
            )
            session.add(workspace)
            session.flush()
        else:
            workspace.repo_url = repo_url

        issue_artifact = session.scalar(select(Artifact).where(Artifact.source_id == "seed-issue-1"))
        if issue_artifact is None:
            issue_artifact = Artifact(
                workspace_id=workspace.id,
                type="issue",
                source_id="seed-issue-1",
                repo=repo_ref,
                title="Redis cache rationale",
                content="We decided to use Redis as cache only because latency mattered.",
                author="alice",
                url=f"{repo_url}/issues/1",
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

        redis_refs = session.scalars(select(SourceRef).where(SourceRef.decision_id == accepted_decision.id)).all()
        if not redis_refs:
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
            session.add(
                SourceRef(
                    decision_id=accepted_decision.id,
                    artifact_id=issue_artifact.id,
                    span_start=12,
                    span_end=78,
                    quote="Redis stays cache-only to keep reads fast without making it the source of truth.",
                    url=issue_artifact.url,
                    relevance_score=0.84,
                )
            )

        postgres_artifact = session.scalar(select(Artifact).where(Artifact.source_id == "seed-doc-1"))
        if postgres_artifact is None:
            postgres_artifact = Artifact(
                workspace_id=workspace.id,
                type="doc",
                source_id="seed-doc-1",
                repo=repo_ref,
                title="Primary database rationale",
                content=(
                    "PostgreSQL remains the primary database because transactional consistency matters. "
                    "Redis accelerates reads, but PostgreSQL stays the source of truth."
                ),
                author="system",
                url=f"{repo_url}/blob/main/docs/primary-database.md",
                timestamp=baseline + timedelta(minutes=20),
                metadata_json=None,
            )
            session.add(postgres_artifact)
            session.flush()

        postgres_decision = session.scalar(select(Decision).where(Decision.title == "Keep PostgreSQL Primary"))
        if postgres_decision is None:
            postgres_decision = Decision(
                workspace_id=workspace.id,
                title="Keep PostgreSQL Primary",
                status="active",
                review_state="accepted",
                problem="Need transactional consistency",
                context="Caching is useful, but writes still need durable state",
                constraints="Primary storage must stay durable and queryable",
                chosen_option="Use PostgreSQL as the primary database",
                tradeoffs="Higher operational cost than cache-only storage",
                confidence=0.86,
                created_at=baseline + timedelta(minutes=20),
            )
            session.add(postgres_decision)
            session.flush()

        postgres_refs = session.scalars(select(SourceRef).where(SourceRef.decision_id == postgres_decision.id)).all()
        if not postgres_refs:
            session.add(
                SourceRef(
                    decision_id=postgres_decision.id,
                    artifact_id=postgres_artifact.id,
                    span_start=0,
                    span_end=73,
                    quote="PostgreSQL remains the primary database because transactional consistency matters.",
                    url=postgres_artifact.url,
                    relevance_score=0.86,
                )
            )
            session.add(
                SourceRef(
                    decision_id=postgres_decision.id,
                    artifact_id=postgres_artifact.id,
                    span_start=74,
                    span_end=145,
                    quote="Redis accelerates reads, but PostgreSQL stays the source of truth.",
                    url=postgres_artifact.url,
                    relevance_score=0.81,
                )
            )

        queue_artifact = session.scalar(select(Artifact).where(Artifact.source_id == "seed-pr-queue"))
        if queue_artifact is None:
            queue_artifact = Artifact(
                workspace_id=workspace.id,
                type="pull_request",
                source_id="seed-pr-queue",
                repo=repo_ref,
                title="Move long-running work to background jobs",
                content=(
                    "We moved long-running work to a queue because synchronous requests were timing out. "
                    "The queue adds operational complexity, but keeps request latency predictable."
                ),
                author="dana",
                url=f"{repo_url}/pull/9",
                timestamp=baseline + timedelta(hours=1),
                metadata_json=None,
            )
            session.add(queue_artifact)
            session.flush()

        queue_decision = session.scalar(select(Decision).where(Decision.title == "Queue Long-Running Jobs"))
        if queue_decision is None:
            queue_decision = Decision(
                workspace_id=workspace.id,
                title="Queue Long-Running Jobs",
                status="active",
                review_state="accepted",
                problem="Synchronous jobs block requests",
                context="Need better background processing",
                constraints="Keep request latency predictable",
                chosen_option="Move long-running jobs to a queue",
                tradeoffs="More operational complexity",
                confidence=0.83,
                created_at=baseline + timedelta(hours=1),
            )
            session.add(queue_decision)
            session.flush()

        queue_refs = session.scalars(select(SourceRef).where(SourceRef.decision_id == queue_decision.id)).all()
        if not queue_refs:
            session.add(
                SourceRef(
                    decision_id=queue_decision.id,
                    artifact_id=queue_artifact.id,
                    span_start=0,
                    span_end=83,
                    quote="We moved long-running work to a queue because synchronous requests were timing out.",
                    url=queue_artifact.url,
                    relevance_score=0.83,
                )
            )
            session.add(
                SourceRef(
                    decision_id=queue_decision.id,
                    artifact_id=queue_artifact.id,
                    span_start=84,
                    span_end=157,
                    quote="The queue adds operational complexity, but keeps request latency predictable.",
                    url=queue_artifact.url,
                    relevance_score=0.78,
                )
            )

        review_artifact = session.scalar(select(Artifact).where(Artifact.source_id == "seed-note-review"))
        if review_artifact is None:
            review_artifact = Artifact(
                workspace_id=workspace.id,
                type="meeting_note",
                source_id="seed-note-review",
                repo=repo_ref,
                title="Human review workflow",
                content=(
                    "Candidate decisions stay human-reviewed before acceptance because extraction can be wrong. "
                    "The review queue keeps the decision memory evidence-first and reversible."
                ),
                author="erin",
                url=f"{repo_url}/discussions/12",
                timestamp=baseline + timedelta(hours=2),
                metadata_json=None,
            )
            session.add(review_artifact)
            session.flush()

        review_decision = session.scalar(select(Decision).where(Decision.title == "Human Review Before Acceptance"))
        if review_decision is None:
            review_decision = Decision(
                workspace_id=workspace.id,
                title="Human Review Before Acceptance",
                status="active",
                review_state="accepted",
                problem="Extraction can misclassify normal discussion as a real decision",
                context="The system needs a trustworthy decision memory",
                constraints="No automatic promotion of candidate decisions",
                chosen_option="Require human review before acceptance",
                tradeoffs="Slower curation, higher trust",
                confidence=0.8,
                created_at=baseline + timedelta(hours=2),
            )
            session.add(review_decision)
            session.flush()

        review_refs = session.scalars(select(SourceRef).where(SourceRef.decision_id == review_decision.id)).all()
        if not review_refs:
            session.add(
                SourceRef(
                    decision_id=review_decision.id,
                    artifact_id=review_artifact.id,
                    span_start=0,
                    span_end=81,
                    quote="Candidate decisions stay human-reviewed before acceptance because extraction can be wrong.",
                    url=review_artifact.url,
                    relevance_score=0.8,
                )
            )
            session.add(
                SourceRef(
                    decision_id=review_decision.id,
                    artifact_id=review_artifact.id,
                    span_start=82,
                    span_end=153,
                    quote="The review queue keeps the decision memory evidence-first and reversible.",
                    url=review_artifact.url,
                    relevance_score=0.76,
                )
            )

        candidate_decision = session.scalar(select(Decision).where(Decision.title == "Add Decision Diff View"))
        if candidate_decision is None:
            session.add(
                Decision(
                    workspace_id=workspace.id,
                    title="Add Decision Diff View",
                    status="active",
                    review_state="candidate",
                    problem="Reviewers need faster comparison between old and new decisions",
                    context="The review queue is growing and drift reviews need better context",
                    constraints=None,
                    chosen_option="Add a side-by-side decision diff view",
                    tradeoffs="Extra UI complexity",
                    confidence=0.78,
                    created_at=baseline + timedelta(hours=3),
                )
            )

        drift_artifact = session.scalar(select(Artifact).where(Artifact.source_id == "seed-pr-2"))
        if drift_artifact is None:
            drift_artifact = Artifact(
                workspace_id=workspace.id,
                type="pull_request",
                source_id="seed-pr-2",
                repo=repo_ref,
                title="Persist sessions in Redis",
                content="Persist session state in Redis as the primary database for auth reads.",
                author="bob",
                url=f"{repo_url}/pull/2",
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
