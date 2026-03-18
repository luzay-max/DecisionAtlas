from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.models import Decision, Workspace
from app.indexing.embedder import FakeEmbedder
from app.retrieval.hybrid import hybrid_search


def test_hybrid_search_merges_full_text_and_vector_hits(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "hybrid.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}")

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
                ),
            ]
        )
        session.commit()

    with Session(engine) as session:
        hits = hybrid_search(
            session=session,
            workspace_slug="demo-workspace",
            query="why use redis cache",
            embedder=FakeEmbedder(),
        )

    assert hits
    assert hits[0].title == "Use Redis Cache"


def test_hybrid_search_filters_stopword_noise_for_specific_queries(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "hybrid-stopwords.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}")

    with Session(engine) as session:
        workspace = Workspace(slug="demo-workspace", name="Demo", repo_url="https://github.com/encode/httpx")
        session.add(workspace)
        session.flush()
        session.add_all(
            [
                Decision(
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
                ),
                Decision(
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
                ),
            ]
        )
        session.commit()

    with Session(engine) as session:
        hits = hybrid_search(
            session=session,
            workspace_slug="demo-workspace",
            query="why move long-running jobs to a queue",
            embedder=FakeEmbedder(),
        )

    assert hits
    assert hits[0].title == "Queue Long-Running Jobs"
