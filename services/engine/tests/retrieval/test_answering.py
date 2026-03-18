from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.models import Artifact, Decision, SourceRef, Workspace
from app.indexing.embedder import FakeEmbedder
from app.retrieval.answering import answer_why_question


def test_answering_returns_insufficient_evidence_when_no_hits(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "answer-empty.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        session.add(Workspace(slug="demo-workspace", name="Demo", repo_url="https://github.com/org/repo"))
        session.commit()

    with Session(engine) as session:
        response = answer_why_question(
            session=session,
            workspace_slug="demo-workspace",
            question="why use redis",
            embedder=FakeEmbedder(),
        )

    assert response["status"] == "insufficient_evidence"
    assert response["citations"] == []


def test_answering_includes_two_or_more_citations(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "answer.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}")

    with Session(engine) as session:
        workspace = Workspace(slug="demo-workspace", name="Demo", repo_url="https://github.com/org/repo")
        session.add(workspace)
        session.flush()
        artifact = Artifact(
            workspace_id=workspace.id,
            type="issue",
            source_id="1",
            repo="org/repo",
            title="Redis decision",
            content="We decided to use Redis as cache because latency mattered.",
            author="alice",
            url="https://github.com/org/repo/issues/1",
            timestamp=None,
            metadata_json=None,
        )
        session.add(artifact)
        session.flush()
        decision = Decision(
            workspace_id=workspace.id,
            title="Use Redis Cache",
            status="active",
            review_state="accepted",
            problem="Latency too high",
            context="Read load increased",
            constraints=None,
            chosen_option="Use Redis as cache only",
            tradeoffs="Extra dependency",
            confidence=0.88,
        )
        session.add(decision)
        session.flush()
        session.add_all(
            [
                SourceRef(
                    decision_id=decision.id,
                    artifact_id=artifact.id,
                    span_start=0,
                    span_end=20,
                    quote="We decided to use Redis as cache",
                    url="https://github.com/org/repo/issues/1",
                    relevance_score=0.88,
                ),
                SourceRef(
                    decision_id=decision.id,
                    artifact_id=artifact.id,
                    span_start=21,
                    span_end=52,
                    quote="because latency mattered",
                    url="https://github.com/org/repo/issues/1",
                    relevance_score=0.82,
                ),
            ]
        )
        session.commit()

    with Session(engine) as session:
        response = answer_why_question(
            session=session,
            workspace_slug="demo-workspace",
            question="why use redis cache",
            embedder=FakeEmbedder(),
        )

    assert response["status"] == "ok"
    assert len(response["citations"]) >= 2
    assert "Use Redis Cache" in response["answer"]


def test_answering_prefers_the_dominant_hit_over_weak_noise(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "answer-dominant.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}")

    with Session(engine) as session:
        workspace = Workspace(slug="demo-workspace", name="Demo", repo_url="https://github.com/org/repo")
        session.add(workspace)
        session.flush()

        artifact = Artifact(
            workspace_id=workspace.id,
            type="issue",
            source_id="queue-1",
            repo="org/repo",
            title="Queue decision",
            content="We moved long-running jobs to a queue because synchronous requests were timing out.",
            author="alice",
            url="https://github.com/org/repo/issues/2",
            timestamp=None,
            metadata_json=None,
        )
        review_artifact = Artifact(
            workspace_id=workspace.id,
            type="note",
            source_id="review-1",
            repo="org/repo",
            title="Review workflow",
            content="Candidate decisions stay human-reviewed before acceptance.",
            author="bob",
            url="https://github.com/org/repo/issues/3",
            timestamp=None,
            metadata_json=None,
        )
        session.add_all([artifact, review_artifact])
        session.flush()

        queue_decision = Decision(
            workspace_id=workspace.id,
            title="Queue Long-Running Jobs",
            status="active",
            review_state="accepted",
            problem="Synchronous jobs block requests",
            context="Need background processing for long-running jobs",
            constraints=None,
            chosen_option="Move long-running jobs to a queue",
            tradeoffs="More operational complexity",
            confidence=0.9,
        )
        review_decision = Decision(
            workspace_id=workspace.id,
            title="Human Review Before Acceptance",
            status="active",
            review_state="accepted",
            problem="Candidate decisions can be wrong",
            context="Review keeps the memory evidence-first",
            constraints=None,
            chosen_option="Require human review before acceptance",
            tradeoffs="Slower curation",
            confidence=0.8,
        )
        session.add_all([queue_decision, review_decision])
        session.flush()
        session.add_all(
            [
                SourceRef(
                    decision_id=queue_decision.id,
                    artifact_id=artifact.id,
                    span_start=0,
                    span_end=40,
                    quote="We moved long-running jobs to a queue",
                    url=artifact.url,
                    relevance_score=0.91,
                ),
                SourceRef(
                    decision_id=queue_decision.id,
                    artifact_id=artifact.id,
                    span_start=41,
                    span_end=82,
                    quote="because synchronous requests were timing out",
                    url=artifact.url,
                    relevance_score=0.84,
                ),
                SourceRef(
                    decision_id=review_decision.id,
                    artifact_id=review_artifact.id,
                    span_start=0,
                    span_end=56,
                    quote="Candidate decisions stay human-reviewed before acceptance",
                    url=review_artifact.url,
                    relevance_score=0.8,
                ),
                SourceRef(
                    decision_id=review_decision.id,
                    artifact_id=review_artifact.id,
                    span_start=0,
                    span_end=34,
                    quote="Review keeps the memory evidence-first",
                    url=review_artifact.url,
                    relevance_score=0.74,
                ),
            ]
        )
        session.commit()

    with Session(engine) as session:
        response = answer_why_question(
            session=session,
            workspace_slug="demo-workspace",
            question="why move long-running jobs to a queue",
            embedder=FakeEmbedder(),
        )

    assert response["status"] == "ok"
    assert "Queue Long-Running Jobs" in response["answer"]
    assert "Human Review Before Acceptance" not in response["answer"]
