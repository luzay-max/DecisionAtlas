from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.models import Artifact, Decision, Workspace
from app.drift.semantic_recall import recall_related_decisions
from app.indexing.embedder import FakeEmbedder


def test_semantic_recall_returns_related_accepted_decision(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "semantic-recall.db"
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
        session.add_all(
            [
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
                    confidence=0.88,
                    created_at=baseline,
                ),
                Decision(
                    workspace_id=workspace.id,
                    title="Keep PostgreSQL Primary",
                    status="active",
                    review_state="accepted",
                    problem="Need transactional consistency",
                    context=None,
                    constraints=None,
                    chosen_option="Use PostgreSQL as primary database",
                    tradeoffs="Operational cost",
                    confidence=0.8,
                    created_at=baseline,
                ),
            ]
        )
        artifact = Artifact(
            workspace_id=workspace.id,
            type="pull_request",
            source_id="2",
            repo="org/repo",
            title="Replace Redis cache with Dragonfly",
            content="Proposal to replace the Redis cache with Dragonfly while keeping low-latency reads.",
            author="carol",
            url="https://github.com/org/repo/pull/2",
            timestamp=baseline + timedelta(days=1),
            metadata_json=None,
        )
        session.add(artifact)
        session.commit()

    with Session(engine) as session:
        artifact = session.query(Artifact).filter(Artifact.source_id == "2").one()
        candidates = recall_related_decisions(
            session=session,
            workspace_slug="demo-workspace",
            artifact=artifact,
            embedder=FakeEmbedder(),
        )

    assert candidates
    assert candidates[0].title == "Use Redis Cache"
