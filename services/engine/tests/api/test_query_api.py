from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.models import Artifact, Decision, SourceRef, Workspace
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
    assert len(body["citations"]) >= 2
