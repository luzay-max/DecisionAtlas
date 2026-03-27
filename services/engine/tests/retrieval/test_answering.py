from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.models import Artifact, Decision, SourceRef, Workspace
from app.indexing.embedder import FakeEmbedder
from app.retrieval.answering import answer_why_question
from app.retrieval.query_rewrite import rewrite_query


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
    assert response["supporting_context"] == []


def test_rewrite_query_keeps_rc_aliases_aligned(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "answer-rc-alias.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}")

    with Session(engine) as session:
        workspace = Workspace(slug="imported-workspace", name="Imported", repo_url="https://github.com/org/repo")
        session.add(workspace)
        session.flush()
        artifact = Artifact(
            workspace_id=workspace.id,
            type="pr",
            source_id="rc-1",
            repo="org/repo",
            title="Release candidate branch operations",
            content="Use a GitHub App token when ensuring release candidate branches.",
            author="alice",
            url="https://github.com/org/repo/pull/1",
            timestamp=None,
            metadata_json=None,
        )
        session.add(artifact)
        session.flush()
        decision = Decision(
            workspace_id=workspace.id,
            title="Use GitHub App token for release candidate branch operations",
            status="active",
            review_state="accepted",
            problem="Default token cannot manage release candidate branches",
            context=None,
            constraints=None,
            chosen_option="Use a GitHub App token for release candidate branches",
            tradeoffs="Requires app setup",
            confidence=0.92,
        )
        session.add(decision)
        session.flush()
        session.add_all(
            [
                SourceRef(
                    decision_id=decision.id,
                    artifact_id=artifact.id,
                    span_start=0,
                    span_end=52,
                    quote="Use a GitHub App token when ensuring release candidate branches.",
                    url=artifact.url,
                    relevance_score=0.9,
                ),
                SourceRef(
                    decision_id=decision.id,
                    artifact_id=artifact.id,
                    span_start=0,
                    span_end=30,
                    quote="release candidate branches",
                    url=artifact.url,
                    relevance_score=0.82,
                ),
            ]
        )
        session.commit()

    assert rewrite_query("why use a github app token for rc branches") == rewrite_query(
        "why use a github app token for release candidate branches"
    )

    with Session(engine) as session:
        response = answer_why_question(
            session=session,
            workspace_slug="imported-workspace",
            question="why use a github app token for rc branches",
            embedder=FakeEmbedder(),
        )

    assert response["status"] == "ok"
    assert response["primary_decision"]["title"] == "Use GitHub App token for release candidate branch operations"


def test_answering_exposes_supporting_context_only_for_broad_questions(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "answer-supporting-context.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}")

    with Session(engine) as session:
        workspace = Workspace(slug="imported-workspace", name="Imported", repo_url="https://github.com/org/repo")
        session.add(workspace)
        session.flush()
        app_artifact = Artifact(
            workspace_id=workspace.id,
            type="pr",
            source_id="release-1",
            repo="org/repo",
            title="GitHub App token for release candidates",
            content="Use a GitHub App identity when ensuring release candidate branches.",
            author="alice",
            url="https://github.com/org/repo/pull/10",
            timestamp=None,
            metadata_json=None,
        )
        prerelease_artifact = Artifact(
            workspace_id=workspace.id,
            type="pr",
            source_id="release-2",
            repo="org/repo",
            title="Remove prerelease tag manually",
            content="Prerelease tags are not removed automatically when promoting releases to latest.",
            author="alice",
            url="https://github.com/org/repo/pull/11",
            timestamp=None,
            metadata_json=None,
        )
        session.add_all([app_artifact, prerelease_artifact])
        session.flush()
        app_decision = Decision(
            workspace_id=workspace.id,
            title="Use GitHub App token for release candidate branch operations",
            status="active",
            review_state="accepted",
            problem="Release candidate branch operations fail with the default token",
            context=None,
            constraints=None,
            chosen_option="Use a GitHub App token for release candidate branch operations",
            tradeoffs="Requires separate app identity",
            confidence=0.92,
        )
        prerelease_decision = Decision(
            workspace_id=workspace.id,
            title="Remove prerelease tag manually when promoting GitHub releases to latest",
            status="active",
            review_state="accepted",
            problem="Promoted releases remain marked as prerelease",
            context=None,
            constraints=None,
            chosen_option="Remove the prerelease tag during release promotion",
            tradeoffs="Adds a manual or automated release step",
            confidence=0.9,
        )
        session.add_all([app_decision, prerelease_decision])
        session.flush()
        session.add_all(
            [
                SourceRef(
                    decision_id=app_decision.id,
                    artifact_id=app_artifact.id,
                    span_start=0,
                    span_end=68,
                    quote="Use a GitHub App identity when ensuring release candidate branches.",
                    url=app_artifact.url,
                    relevance_score=0.9,
                ),
                SourceRef(
                    decision_id=app_decision.id,
                    artifact_id=app_artifact.id,
                    span_start=0,
                    span_end=30,
                    quote="release candidate branches",
                    url=app_artifact.url,
                    relevance_score=0.83,
                ),
                SourceRef(
                    decision_id=prerelease_decision.id,
                    artifact_id=prerelease_artifact.id,
                    span_start=0,
                    span_end=80,
                    quote="Prerelease tags are not removed automatically when promoting releases to latest.",
                    url=prerelease_artifact.url,
                    relevance_score=0.88,
                ),
                SourceRef(
                    decision_id=prerelease_decision.id,
                    artifact_id=prerelease_artifact.id,
                    span_start=0,
                    span_end=34,
                    quote="promoting releases to latest",
                    url=prerelease_artifact.url,
                    relevance_score=0.78,
                ),
            ]
        )
        session.commit()

    with Session(engine) as session:
        focused_response = answer_why_question(
            session=session,
            workspace_slug="imported-workspace",
            question="why use github app token for release candidate branch operations",
            embedder=FakeEmbedder(),
        )
        broad_response = answer_why_question(
            session=session,
            workspace_slug="imported-workspace",
            question="why did we change release candidate branches and release tags",
            embedder=FakeEmbedder(),
        )

    assert focused_response["status"] == "ok"
    assert focused_response["supporting_context"] == []
    assert broad_response["status"] == "ok"
    assert broad_response["primary_decision"]["title"] in {
        "Use GitHub App token for release candidate branch operations",
        "Remove prerelease tag manually when promoting GitHub releases to latest",
    }
    assert len(broad_response["supporting_context"]) == 1
    assert broad_response["supporting_context"][0]["title"] != broad_response["primary_decision"]["title"]
