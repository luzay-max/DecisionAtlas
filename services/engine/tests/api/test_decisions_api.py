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
        session.add(
            SourceRef(
                decision_id=decision.id,
                artifact_id=artifact.id,
                span_start=12,
                span_end=55,
                quote="use Redis as a cache because latency mattered",
                url="https://github.com/org/repo/issues/1",
                relevance_score=0.82,
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
    assert body[0]["workspace_mode"] == "imported"
    assert body[0]["review_evidence"]["state"] == "grounded"
    assert body[0]["review_evidence"]["source_ref_count"] == 2
    assert body[0]["review_evidence"]["source_ref_preview"][0]["quote"].startswith("We decided to use Redis")
    assert body[0]["candidate_quality"]["label"] == "strong"
    assert body[0]["candidate_quality"]["summary"] == (
        "Multiple grounded refs with previewable evidence, provenance, and source URL support."
    )
    assert body[0]["candidate_quality"]["previewable_source_ref_count"] == 2
    assert body[0]["candidate_quality"]["has_primary_artifact"] is True
    assert body[0]["candidate_quality"]["has_source_url"] is True
    assert body[0]["candidate_quality"]["confidence_bucket"] == "high"
    assert body[0]["review_evidence"]["primary_artifact"] == {
        "id": 1,
        "type": "issue",
        "title": "Cache decision",
        "repo": "org/repo",
        "url": "https://github.com/org/repo/issues/1",
    }
    assert body[1]["review_evidence"]["state"] == "missing"
    assert body[1]["review_evidence"]["source_ref_count"] == 0
    assert body[1]["review_evidence"]["source_ref_preview"] == []
    assert body[1]["review_evidence"]["primary_artifact"] is None
    assert body[1]["candidate_quality"]["label"] == "thin"
    assert body[1]["candidate_quality"]["reasons"] == [
        "missing_source_refs",
        "missing_previewable_quote",
        "missing_artifact_provenance",
        "missing_source_url",
        "low_confidence",
    ]


def test_candidate_quality_boundaries_do_not_promote_weak_evidence(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "quality-boundaries.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")

    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        workspace = Workspace(slug="quality-workspace", name="Quality", repo_url="https://github.com/org/repo")
        session.add(workspace)
        session.flush()
        artifact_without_url = Artifact(
            workspace_id=workspace.id,
            type="pr",
            source_id="2",
            repo="org/repo",
            title="Queue decision",
            content="Use a queue for slow jobs.",
            author="alice",
            url=None,
            timestamp=None,
            metadata_json=None,
        )
        session.add(artifact_without_url)
        session.flush()
        partial_decision = Decision(
            workspace_id=workspace.id,
            title="Use Queue",
            status="active",
            review_state="candidate",
            problem="Slow jobs",
            context=None,
            constraints=None,
            chosen_option="Use a queue",
            tradeoffs="More moving parts",
            confidence=0.92,
        )
        weak_decision = Decision(
            workspace_id=workspace.id,
            title="Use Cache",
            status="active",
            review_state="candidate",
            problem="Slow reads",
            context=None,
            constraints=None,
            chosen_option="Use cache",
            tradeoffs="More infra",
            confidence=0.97,
        )
        session.add_all([partial_decision, weak_decision])
        session.flush()
        session.add(
            SourceRef(
                decision_id=partial_decision.id,
                artifact_id=artifact_without_url.id,
                span_start=0,
                span_end=24,
                quote="Use a queue for slow jobs.",
                url=None,
                relevance_score=0.9,
            )
        )
        session.commit()

    client = TestClient(create_app())
    response = client.get("/decisions", params={"workspace_slug": "quality-workspace", "review_state": "candidate"})

    assert response.status_code == 200
    by_title = {item["title"]: item for item in response.json()}
    assert by_title["Use Queue"]["candidate_quality"]["label"] == "partial"
    assert by_title["Use Queue"]["candidate_quality"]["reasons"] == [
        "single_source_ref",
        "previewable_quote",
        "artifact_provenance",
        "missing_source_url",
        "high_confidence",
    ]
    assert by_title["Use Cache"]["candidate_quality"]["label"] == "thin"
    assert by_title["Use Cache"]["candidate_quality"]["reasons"] == [
        "missing_source_refs",
        "missing_previewable_quote",
        "missing_artifact_provenance",
        "missing_source_url",
        "high_confidence",
    ]


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
    assert body["candidate_quality"]["label"] == "strong"
    assert len(body["source_refs"]) == 2


def test_review_decision_updates_review_state(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "review.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    _seed_review_fixture(db_path)

    client = TestClient(create_app())
    response = client.post(
        "/decisions/1/review",
        json={"review_state": "accepted", "review_rationale": "Source refs support the decision."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["review_state"] == "accepted"
    assert body["audit_event"]["target_type"] == "decision"
    assert body["audit_event"]["target_id"] == 1
    assert body["audit_event"]["action"] == "decision_review_accepted"
    assert body["audit_event"]["actor_username"] == "local-admin"
    assert body["audit_event"]["previous_state"]["review_state"] == "candidate"
    assert body["audit_event"]["new_state"]["review_state"] == "accepted"
    assert body["audit_event"]["rationale"] == "Source refs support the decision."
    assert body["review_history"][0]["action"] == "decision_review_accepted"

    detail_response = client.get("/decisions/1")
    assert detail_response.status_code == 200
    assert detail_response.json()["review_history"][0]["rationale"] == "Source refs support the decision."
