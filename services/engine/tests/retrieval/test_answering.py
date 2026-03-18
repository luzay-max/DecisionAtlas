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
