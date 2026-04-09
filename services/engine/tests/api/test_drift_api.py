from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.models import Artifact, Decision, DriftAlert, ImportJob, Workspace
from app.main import create_app


def _seed_drift_fixture(db_path: Path) -> None:
    engine = create_engine(f"sqlite:///{db_path}")
    baseline = datetime(2026, 3, 18, 9, 0, 0)
    with Session(engine) as session:
        workspace = Workspace(slug="imported-workspace", name="Imported", repo_url="https://github.com/org/repo")
        session.add(workspace)
        session.flush()
        artifact = Artifact(
            workspace_id=workspace.id,
            type="pull_request",
            source_id="2",
            repo="org/repo",
            title="Persist sessions in Redis",
            content="Persist session state in Redis as the primary database for auth reads.",
            author="bob",
            url="https://github.com/org/repo/pull/2",
            timestamp=baseline + timedelta(days=1),
            metadata_json=None,
        )
        decision = Decision(
            workspace_id=workspace.id,
            title="Use Redis Cache",
            status="active",
            review_state="accepted",
            problem="Latency too high",
            context=None,
            constraints="Redis stays cache-only.",
            chosen_option="Use Redis as cache only and keep PostgreSQL primary.",
            tradeoffs="Extra dependency",
            confidence=0.92,
            created_at=baseline,
            updated_at=baseline,
        )
        session.add_all([artifact, decision])
        session.flush()
        session.add(
            ImportJob(
                job_id="job-drift-1",
                workspace_id=workspace.id,
                repo="org/repo",
                mode="full",
                status="succeeded",
                imported_count=2,
                finished_at=baseline + timedelta(days=1),
                summary_json={
                    "stage": "completed",
                    "outcome": "ok",
                    "drift_evaluation": {
                        "evaluated_at": (baseline + timedelta(days=1, minutes=1)).isoformat(),
                        "evaluated_rules": 1,
                        "created_alerts": 1,
                    },
                },
            )
        )
        session.add(
            DriftAlert(
                workspace_id=workspace.id,
                artifact_id=artifact.id,
                decision_id=decision.id,
                alert_type="possible_drift",
                summary="Accepted decision 'Use Redis Cache' keeps Redis cache-only.",
                status="open",
            )
        )
        session.commit()


def test_list_drift_alerts_returns_joined_context(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "drift-api.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    _seed_drift_fixture(db_path)

    client = TestClient(create_app())
    response = client.get("/drift", params={"workspace_slug": "imported-workspace"})

    assert response.status_code == 200
    body = response.json()
    assert body["workspace_mode"] == "imported"
    assert body["evaluation"]["state"] == "alerts_present"
    assert len(body["alerts"]) == 1
    assert body["alerts"][0]["confidence_label"] == "high"
    assert body["alerts"][0]["artifact"]["title"] == "Persist sessions in Redis"
    assert body["alerts"][0]["decision"]["title"] == "Use Redis Cache"


def test_post_drift_evaluate_returns_counts(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "drift-evaluate-api.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}")
    baseline = datetime(2026, 3, 18, 9, 0, 0)

    with Session(engine) as session:
        workspace = Workspace(slug="imported-workspace", name="Imported", repo_url="https://github.com/org/repo")
        session.add(workspace)
        session.flush()
        session.add(
            Artifact(
                workspace_id=workspace.id,
                type="pull_request",
                source_id="2",
                repo="org/repo",
                title="Persist sessions in Redis",
                content="Persist session state in Redis as the primary database for auth reads.",
                author="bob",
                url="https://github.com/org/repo/pull/2",
                timestamp=baseline + timedelta(days=1),
                metadata_json=None,
            )
        )
        session.add(
            Decision(
                workspace_id=workspace.id,
                title="Use Redis Cache",
                status="active",
                review_state="accepted",
                problem="Latency too high",
                context=None,
                constraints="Redis stays cache-only.",
                chosen_option="Use Redis as cache only and keep PostgreSQL primary.",
                tradeoffs="Extra dependency",
                confidence=0.92,
                created_at=baseline,
                updated_at=baseline,
            )
        )
        session.add(
            ImportJob(
                job_id="job-drift-eval",
                workspace_id=workspace.id,
                repo="org/repo",
                mode="full",
                status="succeeded",
                imported_count=2,
                summary_json={"stage": "completed", "outcome": "ok"},
            )
        )
        session.commit()

    client = TestClient(create_app())
    response = client.post("/drift/evaluate", json={"workspace_slug": "imported-workspace"})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["created_alerts"] == 1
    assert body["evaluation"]["state"] == "alerts_present"


def test_list_drift_alerts_maps_semantic_alert_confidence_labels(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "drift-semantic-api.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}")
    baseline = datetime(2026, 3, 18, 9, 0, 0)

    with Session(engine) as session:
        workspace = Workspace(slug="imported-workspace", name="Imported", repo_url="https://github.com/org/repo")
        session.add(workspace)
        session.flush()
        artifact = Artifact(
            workspace_id=workspace.id,
            type="doc",
            source_id="CHANGELOG.md",
            repo="org/repo",
            title="CHANGELOG",
            content="This release note is related to the existing database migration decision.",
            author="bob",
            url="https://github.com/org/repo/blob/main/CHANGELOG.md",
            timestamp=baseline + timedelta(days=1),
            metadata_json={"path": "CHANGELOG.md"},
        )
        decision = Decision(
            workspace_id=workspace.id,
            title="Expand variables.value column",
            status="active",
            review_state="accepted",
            problem="Long values fail to save",
            context=None,
            constraints=None,
            chosen_option="Expand variables.value to 1000 chars",
            tradeoffs="Requires migration",
            confidence=0.92,
            created_at=baseline,
            updated_at=baseline,
        )
        session.add_all([artifact, decision])
        session.flush()
        session.add(
            ImportJob(
                job_id="job-drift-semantic",
                workspace_id=workspace.id,
                repo="org/repo",
                mode="full",
                status="succeeded",
                imported_count=2,
                finished_at=baseline + timedelta(days=1),
                summary_json={"stage": "completed", "outcome": "ok"},
            )
        )
        session.add(
            DriftAlert(
                workspace_id=workspace.id,
                artifact_id=artifact.id,
                decision_id=decision.id,
                alert_type="needs_review",
                summary="Artifact 'CHANGELOG' appears related to accepted decision 'Expand variables.value column'. Review whether the newer work changes or reinforces the prior choice.",
                status="open",
            )
        )
        session.commit()

    client = TestClient(create_app())
    response = client.get("/drift", params={"workspace_slug": "imported-workspace"})

    assert response.status_code == 200
    body = response.json()
    assert body["alerts"][0]["alert_type"] == "needs_review"
    assert body["alerts"][0]["confidence_label"] == "low"
    assert "changes or reinforces" in body["alerts"][0]["summary"]


def test_list_drift_alerts_returns_grouped_followup_summary(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "drift-grouped-followup-api.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}")
    baseline = datetime(2026, 3, 18, 9, 0, 0)

    with Session(engine) as session:
        workspace = Workspace(slug="imported-workspace", name="Imported", repo_url="https://github.com/browser-use/browser-use")
        session.add(workspace)
        session.flush()
        artifact = Artifact(
            workspace_id=workspace.id,
            type="pull_request",
            source_id="3901",
            repo="browser-use/browser-use",
            title="Evaluate remote browser cookie transfer for HTTP downloads",
            content="This follow-up continues HTTP download support for remote browsers.",
            author="maintainer",
            url="https://github.com/browser-use/browser-use/pull/3901",
            timestamp=baseline + timedelta(days=2),
            metadata_json=None,
        )
        decision = Decision(
            workspace_id=workspace.id,
            title="Enable HTTP-based downloads for remote browsers with agent status tracking",
            status="active",
            review_state="accepted",
            problem="Remote browser downloads need richer progress and status handling.",
            context=None,
            constraints=None,
            chosen_option="Use HTTP-based downloads with remote browser status tracking.",
            tradeoffs="Adds transport complexity.",
            confidence=0.95,
            created_at=baseline,
            updated_at=baseline,
        )
        session.add_all([artifact, decision])
        session.flush()
        session.add(
            ImportJob(
                job_id="job-drift-grouped-followup",
                workspace_id=workspace.id,
                repo="browser-use/browser-use",
                mode="full",
                status="succeeded",
                imported_count=2,
                finished_at=baseline + timedelta(days=2),
                summary_json={"stage": "completed", "outcome": "ok"},
            )
        )
        session.add(
            DriftAlert(
                workspace_id=workspace.id,
                artifact_id=artifact.id,
                decision_id=decision.id,
                alert_type="needs_review",
                summary="Artifact 'Evaluate remote browser cookie transfer for HTTP downloads' and 2 related follow-up artifacts appear connected to accepted decision 'Enable HTTP-based downloads for remote browsers with agent status tracking'. Review whether this newer work only continues the prior choice or introduces a real decision change. Closest prior choice: Use HTTP-based downloads with remote browser status tracking.",
                status="open",
            )
        )
        session.commit()

    client = TestClient(create_app())
    response = client.get("/drift", params={"workspace_slug": "imported-workspace"})

    assert response.status_code == 200
    body = response.json()
    assert body["alerts"][0]["alert_type"] == "needs_review"
    assert "related follow-up artifacts" in body["alerts"][0]["summary"]


def test_list_drift_alerts_preserves_weaker_semantics_for_implementation_substitution(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "drift-implementation-substitution-api.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}")
    baseline = datetime(2026, 3, 18, 9, 0, 0)

    with Session(engine) as session:
        workspace = Workspace(slug="imported-workspace", name="Imported", repo_url="https://github.com/browser-use/browser-use")
        session.add(workspace)
        session.flush()
        artifact = Artifact(
            workspace_id=workspace.id,
            type="pull_request",
            source_id="4001",
            repo="browser-use/browser-use",
            title="Feature Request: Use cloakbrowser replace playwright",
            content="Use cloakbrowser replace playwright while keeping HTTP-based downloads and status tracking intact.",
            author="maintainer",
            url="https://github.com/browser-use/browser-use/pull/4001",
            timestamp=baseline + timedelta(days=2),
            metadata_json=None,
        )
        decision = Decision(
            workspace_id=workspace.id,
            title="Enable HTTP-based downloads for remote browsers with agent status tracking",
            status="active",
            review_state="accepted",
            problem="Remote browser downloads need richer progress and status handling.",
            context=None,
            constraints=None,
            chosen_option="Use HTTP-based downloads with remote browser status tracking.",
            tradeoffs="Adds transport complexity.",
            confidence=0.95,
            created_at=baseline,
            updated_at=baseline,
        )
        session.add_all([artifact, decision])
        session.flush()
        session.add(
            ImportJob(
                job_id="job-drift-implementation-substitution",
                workspace_id=workspace.id,
                repo="browser-use/browser-use",
                mode="full",
                status="succeeded",
                imported_count=2,
                finished_at=baseline + timedelta(days=2),
                summary_json={"stage": "completed", "outcome": "ok"},
            )
        )
        session.add(
            DriftAlert(
                workspace_id=workspace.id,
                artifact_id=artifact.id,
                decision_id=decision.id,
                alert_type="needs_review",
                summary="Artifact 'Feature Request: Use cloakbrowser replace playwright' appears related to accepted decision 'Enable HTTP-based downloads for remote browsers with agent status tracking', but the change currently looks closer to an implementation-level substitution than a replacement of the prior choice. Closest prior choice: Use HTTP-based downloads with remote browser status tracking.",
                status="open",
            )
        )
        session.commit()

    client = TestClient(create_app())
    response = client.get("/drift", params={"workspace_slug": "imported-workspace"})

    assert response.status_code == 200
    body = response.json()
    assert body["alerts"][0]["alert_type"] == "needs_review"
    assert body["alerts"][0]["confidence_label"] == "low"
    assert "implementation-level substitution" in body["alerts"][0]["summary"]


def test_list_drift_alerts_keeps_bugfix_heavy_case_on_weaker_path(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "drift-bugfix-heavy-api.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}")
    baseline = datetime(2026, 3, 18, 9, 0, 0)

    with Session(engine) as session:
        workspace = Workspace(slug="imported-workspace", name="Imported", repo_url="https://github.com/browser-use/browser-use")
        session.add(workspace)
        session.flush()
        artifact = Artifact(
            workspace_id=workspace.id,
            type="pull_request",
            source_id="4002",
            repo="browser-use/browser-use",
            title="fix: cookie persistence bugs + comprehensive tests",
            content="This fix replaces the previous HTTP-based remote browser downloads flow with a more reliable cookie transfer path while keeping agent status tracking intact.",
            author="maintainer",
            url="https://github.com/browser-use/browser-use/pull/4002",
            timestamp=baseline + timedelta(days=2),
            metadata_json=None,
        )
        decision = Decision(
            workspace_id=workspace.id,
            title="Enable HTTP-based downloads for remote browsers with agent status tracking",
            status="active",
            review_state="accepted",
            problem="Remote browser downloads need richer progress and status handling.",
            context=None,
            constraints=None,
            chosen_option="Use HTTP-based downloads with remote browser status tracking.",
            tradeoffs="Adds transport complexity.",
            confidence=0.95,
            created_at=baseline,
            updated_at=baseline,
        )
        session.add_all([artifact, decision])
        session.flush()
        session.add(
            ImportJob(
                job_id="job-drift-bugfix-heavy",
                workspace_id=workspace.id,
                repo="browser-use/browser-use",
                mode="full",
                status="succeeded",
                imported_count=2,
                finished_at=baseline + timedelta(days=2),
                summary_json={"stage": "completed", "outcome": "ok"},
            )
        )
        session.add(
            DriftAlert(
                workspace_id=workspace.id,
                artifact_id=artifact.id,
                decision_id=decision.id,
                alert_type="needs_review",
                summary="Artifact 'fix: cookie persistence bugs + comprehensive tests' appears related to accepted decision 'Enable HTTP-based downloads for remote browsers with agent status tracking', but the change currently looks closer to an implementation-level substitution than a replacement of the prior choice. Closest prior choice: Use HTTP-based downloads with remote browser status tracking.",
                status="open",
            )
        )
        session.commit()

    client = TestClient(create_app())
    response = client.get("/drift", params={"workspace_slug": "imported-workspace"})

    assert response.status_code == 200
    body = response.json()
    assert body["alerts"][0]["alert_type"] == "needs_review"
    assert body["alerts"][0]["confidence_label"] == "low"


def test_post_drift_evaluate_replaces_stale_semantic_alerts(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "drift-stale-alert-replacement-api.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}")
    baseline = datetime(2026, 3, 18, 9, 0, 0)

    with Session(engine) as session:
        workspace = Workspace(slug="imported-workspace", name="Imported", repo_url="https://github.com/browser-use/browser-use")
        session.add(workspace)
        session.flush()
        artifact = Artifact(
            workspace_id=workspace.id,
            type="pull_request",
            source_id="4001",
            repo="browser-use/browser-use",
            title="Feature Request: Use cloakbrowser replace playwright",
            content="Use cloakbrowser replace playwright while keeping HTTP-based downloads and status tracking intact.",
            author="maintainer",
            url="https://github.com/browser-use/browser-use/pull/4001",
            timestamp=baseline + timedelta(days=2),
            metadata_json=None,
        )
        decision = Decision(
            workspace_id=workspace.id,
            title="Enable HTTP-based downloads for remote browsers with agent status tracking",
            status="active",
            review_state="accepted",
            problem="Remote browser downloads need richer progress and status handling.",
            context=None,
            constraints=None,
            chosen_option="Use HTTP-based downloads with remote browser status tracking.",
            tradeoffs="Adds transport complexity.",
            confidence=0.95,
            created_at=baseline,
            updated_at=baseline,
        )
        session.add_all([artifact, decision])
        session.flush()
        session.add(
            ImportJob(
                job_id="job-drift-stale-alert-replacement",
                workspace_id=workspace.id,
                repo="browser-use/browser-use",
                mode="full",
                status="succeeded",
                imported_count=2,
                finished_at=baseline + timedelta(days=2),
                summary_json={"stage": "completed", "outcome": "ok"},
            )
        )
        session.add(
            DriftAlert(
                workspace_id=workspace.id,
                artifact_id=artifact.id,
                decision_id=decision.id,
                alert_type="possible_supersession",
                summary="Artifact 'Feature Request: Use cloakbrowser replace playwright' may indicate that accepted decision 'Enable HTTP-based downloads for remote browsers with agent status tracking' is being replaced.",
                status="open",
            )
        )
        session.commit()

    client = TestClient(create_app())
    evaluate_response = client.post("/drift/evaluate", json={"workspace_slug": "imported-workspace"})

    assert evaluate_response.status_code == 200
    assert evaluate_response.json()["created_alerts"] == 1

    list_response = client.get("/drift", params={"workspace_slug": "imported-workspace"})

    assert list_response.status_code == 200
    body = list_response.json()
    assert len(body["alerts"]) == 1
    assert body["alerts"][0]["alert_type"] == "needs_review"
    assert "implementation-level substitution" in body["alerts"][0]["summary"]
