from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.models import Artifact, Decision, ImportJob, SourceRef, Workspace
from app.main import create_app


def test_post_query_why_returns_answer_with_citations(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "query.db"
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

    client = TestClient(create_app())
    response = client.post(
        "/query/why",
        json={"workspace_slug": "imported-workspace", "question": "why use redis cache"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["answer_context"]["workspace_mode"] == "imported"
    assert body["answer_context"]["workspace_readiness"]["state"] == "why_ready"
    assert len(body["citations"]) >= 2
    assert body["primary_decision"]["title"] == "Use Redis Cache"
    assert body["supporting_context"] == []


def test_post_query_why_requires_review_for_imported_workspace_without_accepted_decisions(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "query-review-required.db"
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
            )
        )
        session.add(
            ImportJob(
                job_id="job-why-1",
                workspace_id=workspace.id,
                repo="org/repo",
                mode="full",
                status="succeeded",
                imported_count=3,
                summary_json={"stage": "completed", "outcome": "ok"},
            )
        )
        session.commit()

    client = TestClient(create_app())
    response = client.post(
        "/query/why",
        json={"workspace_slug": "imported-workspace", "question": "why use queue"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "review_required"
    assert body["answer_context"]["workspace_readiness"]["state"] == "review_ready"


def test_post_query_why_keeps_adjacent_release_decisions_out_of_focused_answer(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "query-focused-answer.db"
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

    client = TestClient(create_app())
    response = client.post(
        "/query/why",
        json={
            "workspace_slug": "imported-workspace",
            "question": "why use github app token for release candidate branch operations",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["primary_decision"]["title"] == "Use GitHub App token for release candidate branch operations"
    assert body["supporting_context"] == []
    assert "Remove prerelease tag manually" not in body["answer"]


def test_post_query_why_returns_limited_support_for_one_citation_imported_answer(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "query-limited-support.db"
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
            source_id="release-1",
            repo="org/repo",
            title="GitHub App token for release candidates",
            content="Use a GitHub App identity when ensuring release candidate branches.",
            author="alice",
            url="https://github.com/org/repo/pull/10",
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
            problem="Release candidate branch operations fail with the default token",
            context=None,
            constraints=None,
            chosen_option="Use a GitHub App token for release candidate branch operations",
            tradeoffs="Requires separate app identity",
            confidence=0.92,
        )
        session.add(decision)
        session.flush()
        session.add(
            SourceRef(
                decision_id=decision.id,
                artifact_id=artifact.id,
                span_start=0,
                span_end=68,
                quote="Use a GitHub App identity when ensuring release candidate branches.",
                url=artifact.url,
                relevance_score=0.9,
            )
        )
        session.commit()

    client = TestClient(create_app())
    response = client.post(
        "/query/why",
        json={
            "workspace_slug": "imported-workspace",
            "question": "why use github app token for release candidate branch operations",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "limited_support"
    assert body["primary_decision"]["title"] == "Use GitHub App token for release candidate branch operations"
    assert len(body["citations"]) == 1
