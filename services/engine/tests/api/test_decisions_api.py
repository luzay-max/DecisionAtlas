from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.models import Artifact, Decision, SourceRef, Workspace
from app.main import create_app


def _seed_review_fixture(db_path: Path) -> None:
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
            title="Cache decision",
            content="We decided to use Redis as a cache because latency mattered.",
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
            review_state="candidate",
            problem="Latency too high",
            context="Read traffic increased",
            constraints="Budget is limited",
            chosen_option="Use Redis as cache only",
            tradeoffs="Extra dependency",
            confidence=0.88,
        )
        session.add(decision)
        session.flush()
        session.add(
            Decision(
                workspace_id=workspace.id,
                title="Add Queue",
                status="active",
                review_state="candidate",
                problem="Background tasks are slow",
                context="Need more reliability",
                constraints=None,
                chosen_option="Queue long-running jobs",
                tradeoffs="More infra",
                confidence=0.55,
            )
        )
        session.add(
            SourceRef(
                decision_id=decision.id,
                artifact_id=artifact.id,
                span_start=0,
                span_end=42,
                quote="We decided to use Redis as a cache because latency mattered.",
                url="https://github.com/org/repo/issues/1",
                relevance_score=0.88,
            )
        )
        session.commit()


def test_list_decisions_by_review_state(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "decisions.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    _seed_review_fixture(db_path)

    client = TestClient(create_app())
    response = client.get("/decisions", params={"workspace_slug": "imported-workspace", "review_state": "candidate"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert body[0]["review_state"] == "candidate"
    assert body[0]["title"] == "Use Redis Cache"


def test_get_decision_detail_includes_source_refs(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "detail.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    _seed_review_fixture(db_path)

    client = TestClient(create_app())
    response = client.get("/decisions/1")

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Use Redis Cache"
    assert body["workspace_mode"] == "imported"
    assert "source_summary" in body
    assert len(body["source_refs"]) == 1


def test_review_decision_updates_review_state(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "review.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    _seed_review_fixture(db_path)

    client = TestClient(create_app())
    response = client.post("/decisions/1/review", json={"review_state": "accepted"})

    assert response.status_code == 200
    assert response.json()["review_state"] == "accepted"
