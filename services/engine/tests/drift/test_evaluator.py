from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.models import Artifact, Decision, SourceRef, Workspace
from app.drift.evaluator import DriftEvaluator
from app.drift.semantic_recall import SemanticCandidate
from app.indexing.embedder import FakeEmbedder
from app.repositories.drift_alerts import DriftAlertRepository


def _patch_semantic_recall(monkeypatch) -> None:
    def _fake_recall(*, session: Session, workspace_slug: str, artifact: Artifact, embedder=None, limit: int = 3):
        decision = session.query(Decision).filter_by(review_state="accepted").first()
        if decision is None:
            return []
        content = " ".join(filter(None, [artifact.title, artifact.content])).lower()
        score = 2.8 if "replace redis cache with dragonfly" in content else 2.0
        return [
            SemanticCandidate(
                decision_id=decision.id,
                title=decision.title,
                problem=decision.problem,
                chosen_option=decision.chosen_option,
                tradeoffs=decision.tradeoffs,
                score=score,
                created_at=decision.created_at,
            )
        ]

    monkeypatch.setattr("app.drift.evaluator.recall_related_decisions", _fake_recall)


def test_evaluator_persists_possible_drift_for_violating_artifact(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "drift.db"
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
        source_artifact = Artifact(
            workspace_id=workspace.id,
            type="issue",
            source_id="1",
            repo="org/repo",
            title="Cache rationale",
            content="Use Redis as cache only because latency is high.",
            author="alice",
            url="https://github.com/org/repo/issues/1",
            timestamp=baseline,
            metadata_json=None,
        )
        violating_artifact = Artifact(
            workspace_id=workspace.id,
            type="pull_request",
            source_id="2",
            repo="org/repo",
            title="Persist sessions in Redis",
            content="This PR will persist session state in Redis as the primary database for auth reads.",
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
        )
        session.add_all([source_artifact, violating_artifact, decision])
        session.flush()
        session.add(
            SourceRef(
                decision_id=decision.id,
                artifact_id=source_artifact.id,
                span_start=0,
                span_end=44,
                quote="Use Redis as cache only because latency is high.",
                url=source_artifact.url,
                relevance_score=0.9,
            )
        )
        session.commit()

    _patch_semantic_recall(monkeypatch)
    with Session(engine) as session:
        result = DriftEvaluator(session, embedder=FakeEmbedder()).evaluate_workspace("demo-workspace")
        alerts = DriftAlertRepository(session).list_by_workspace(1)

    assert result.evaluated_rules == 1
    assert result.created_alerts == 1
    assert len(alerts) == 1
    assert alerts[0].alert_type == "possible_drift"
    assert "primary database" in alerts[0].summary.lower()


def test_evaluator_skips_non_violating_artifact(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "drift-clean.db"
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
        session.add(
            Artifact(
                workspace_id=workspace.id,
                type="issue",
                source_id="1",
                repo="org/repo",
                title="Warm cache",
                content="Keep Redis warm and use it as a cache in front of PostgreSQL.",
                author="alice",
                url="https://github.com/org/repo/issues/1",
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
            )
        )
        session.commit()

    _patch_semantic_recall(monkeypatch)
    with Session(engine) as session:
        result = DriftEvaluator(session, embedder=FakeEmbedder()).evaluate_workspace("demo-workspace")
        alerts = DriftAlertRepository(session).list_by_workspace(1)

    assert result.created_alerts == 0
    assert alerts == []


def test_evaluator_adds_semantic_supersession_alert_when_rule_does_not_fire(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "semantic-alert.db"
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
            )
        )
        session.add(
            Artifact(
                workspace_id=workspace.id,
                type="pull_request",
                source_id="3",
                repo="org/repo",
                title="Replace Redis cache with Dragonfly",
                content="This proposal will replace the Redis cache with Dragonfly to cut cost while keeping low latency.",
                author="carol",
                url="https://github.com/org/repo/pull/3",
                timestamp=baseline + timedelta(days=2),
                metadata_json=None,
            )
        )
        session.commit()

    _patch_semantic_recall(monkeypatch)
    with Session(engine) as session:
        result = DriftEvaluator(session, embedder=FakeEmbedder()).evaluate_workspace("demo-workspace")
        alerts = DriftAlertRepository(session).list_by_workspace(1)

    assert result.created_alerts == 1
    assert len(alerts) == 1
    assert alerts[0].alert_type == "possible_supersession"


def test_evaluator_downgrades_noisy_changelog_case_to_needs_review(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "semantic-changelog-alert.db"
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
            Decision(
                workspace_id=workspace.id,
                title="Add migration to expand variables.value column",
                status="active",
                review_state="accepted",
                problem="Long variable values fail to save",
                context=None,
                constraints="Preserve compatibility across supported databases.",
                chosen_option="Expand variables.value from varchar(255) to varchar(1000) or TEXT where appropriate.",
                tradeoffs="Requires a schema migration on existing installations.",
                confidence=0.92,
                created_at=baseline,
            )
        )
        session.add(
            Artifact(
                workspace_id=workspace.id,
                type="doc",
                source_id="CHANGELOG.md",
                repo="org/repo",
                title="CHANGELOG",
                content="Release notes: replace the variable length limit to support longer values in MySQL and MariaDB as well.",
                author="maintainer",
                url="https://github.com/org/repo/blob/main/CHANGELOG.md",
                timestamp=baseline + timedelta(days=2),
                metadata_json={"path": "CHANGELOG.md", "signal_category": "release_notes"},
            )
        )
        session.commit()

    _patch_semantic_recall(monkeypatch)
    with Session(engine) as session:
        result = DriftEvaluator(session, embedder=FakeEmbedder()).evaluate_workspace("imported-workspace")
        alerts = DriftAlertRepository(session).list_by_workspace(1)

    assert result.created_alerts == 1
    assert len(alerts) == 1
    assert alerts[0].alert_type == "needs_review"


def test_evaluator_groups_repeated_followup_alerts_for_same_decision(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "grouped-followups.db"
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
        session.add(
            Decision(
                workspace_id=workspace.id,
                title="Enable HTTP-based downloads for remote browsers with agent status tracking",
                status="active",
                review_state="accepted",
                problem="Remote browser downloads need richer progress and status handling.",
                context=None,
                constraints="Support remote browser flows without removing existing local behavior.",
                chosen_option="Use HTTP-based downloads with explicit remote-browser status tracking.",
                tradeoffs="Adds transport complexity and more operational states to review.",
                confidence=0.95,
                created_at=baseline,
            )
        )
        session.add_all(
            [
                Artifact(
                    workspace_id=workspace.id,
                    type="pull_request",
                    source_id="3875",
                    repo="browser-use/browser-use",
                    title="RFC: HTTP download status tracking follow-up",
                    content=(
                        "This RFC evaluates follow-up work around HTTP-based downloads for remote browsers with "
                        "agent status tracking, including active_downloads and failed_downloads state."
                    ),
                    author="maintainer",
                    url="https://github.com/browser-use/browser-use/pull/3875",
                    timestamp=baseline + timedelta(days=1),
                    metadata_json=None,
                ),
                Artifact(
                    workspace_id=workspace.id,
                    type="pull_request",
                    source_id="3901",
                    repo="browser-use/browser-use",
                    title="Evaluate remote browser cookie transfer for HTTP downloads",
                    content=(
                        "Evaluate a follow-up to HTTP-based downloads for remote browsers with agent status tracking "
                        "so active_downloads and failed_downloads stay accurate."
                    ),
                    author="maintainer",
                    url="https://github.com/browser-use/browser-use/pull/3901",
                    timestamp=baseline + timedelta(days=2),
                    metadata_json=None,
                ),
            ]
        )
        session.commit()

    _patch_semantic_recall(monkeypatch)
    with Session(engine) as session:
        result = DriftEvaluator(session, embedder=FakeEmbedder()).evaluate_workspace("imported-workspace")
        alerts = DriftAlertRepository(session).list_by_workspace(1)

    assert result.created_alerts == 1
    assert len(alerts) == 1
    assert alerts[0].alert_type == "needs_review"
    assert "related follow-up artifact" in alerts[0].summary


def test_evaluator_keeps_possible_supersession_separate_from_grouped_followups(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "followup-and-supersession.db"
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
            )
        )
        session.add_all(
            [
                Artifact(
                    workspace_id=workspace.id,
                    type="issue",
                    source_id="12",
                    repo="org/repo",
                    title="RFC: evaluate Redis follow-up",
                    content=(
                        "This RFC evaluates follow-up work around the Redis cache, cache-only policy, and "
                        "keeping PostgreSQL primary to keep the current choice healthy."
                    ),
                    author="erin",
                    url="https://github.com/org/repo/issues/12",
                    timestamp=baseline + timedelta(days=1),
                    metadata_json=None,
                ),
                Artifact(
                    workspace_id=workspace.id,
                    type="pull_request",
                    source_id="13",
                    repo="org/repo",
                    title="Replace Redis cache with Dragonfly",
                    content="This PR will replace the Redis cache with Dragonfly to reduce cost.",
                    author="erin",
                    url="https://github.com/org/repo/pull/13",
                    timestamp=baseline + timedelta(days=2),
                    metadata_json=None,
                ),
            ]
        )
        session.commit()

    _patch_semantic_recall(monkeypatch)
    with Session(engine) as session:
        result = DriftEvaluator(session, embedder=FakeEmbedder()).evaluate_workspace("demo-workspace")
        alerts = DriftAlertRepository(session).list_by_workspace(1)

    assert result.created_alerts == 2
    assert len(alerts) == 2
    assert {alert.alert_type for alert in alerts} == {"needs_review", "possible_supersession"}


def test_evaluator_downgrades_implementation_substitution_from_supersession(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "implementation-substitution.db"
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
        session.add(
            Decision(
                workspace_id=workspace.id,
                title="Enable HTTP-based downloads for remote browsers with agent status tracking",
                status="active",
                review_state="accepted",
                problem="Remote browser downloads need richer progress and status handling.",
                context=None,
                constraints="Support remote browser flows without removing existing local behavior.",
                chosen_option="Use HTTP-based downloads with explicit remote-browser status tracking.",
                tradeoffs="Adds transport complexity and more operational states to review.",
                confidence=0.95,
                created_at=baseline,
            )
        )
        session.add(
                Artifact(
                    workspace_id=workspace.id,
                    type="pull_request",
                    source_id="4001",
                    repo="browser-use/browser-use",
                    title="Feature Request: Use cloakbrowser replace playwright",
                    content=(
                        "Use cloakbrowser replace playwright while keeping HTTP-based downloads for remote browsers "
                        "with agent status tracking, active_downloads, and failed_downloads intact."
                    ),
                    author="maintainer",
                    url="https://github.com/browser-use/browser-use/pull/4001",
                    timestamp=baseline + timedelta(days=2),
                    metadata_json=None,
            )
        )
        session.commit()

    _patch_semantic_recall(monkeypatch)
    with Session(engine) as session:
        result = DriftEvaluator(session, embedder=FakeEmbedder()).evaluate_workspace("imported-workspace")
        alerts = DriftAlertRepository(session).list_by_workspace(1)

    assert result.created_alerts == 1
    assert len(alerts) == 1
    assert alerts[0].alert_type == "needs_review"
    assert "accepted decision" in alerts[0].summary


def test_evaluator_downgrades_bugfix_heavy_replacement_to_needs_review(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "bugfix-heavy-replacement.db"
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
        session.add(
            Decision(
                workspace_id=workspace.id,
                title="Enable HTTP-based downloads for remote browsers with agent status tracking",
                status="active",
                review_state="accepted",
                problem="Remote browser downloads need richer progress and status handling.",
                context=None,
                constraints="Support remote browser flows without removing existing local behavior.",
                chosen_option="Use HTTP-based downloads with explicit remote-browser status tracking.",
                tradeoffs="Adds transport complexity and more operational states to review.",
                confidence=0.95,
                created_at=baseline,
            )
        )
        session.add(
                Artifact(
                    workspace_id=workspace.id,
                    type="pull_request",
                    source_id="4002",
                    repo="browser-use/browser-use",
                    title="fix: cookie persistence bugs + comprehensive tests",
                    content=(
                        "This fix replaces the previous HTTP-based remote browser downloads flow with a more reliable "
                        "cookie transfer path while keeping HTTP-based downloads for remote browsers with agent "
                        "status tracking intact."
                    ),
                    author="maintainer",
                    url="https://github.com/browser-use/browser-use/pull/4002",
                    timestamp=baseline + timedelta(days=2),
                    metadata_json=None,
            )
        )
        session.commit()

    _patch_semantic_recall(monkeypatch)
    with Session(engine) as session:
        result = DriftEvaluator(session, embedder=FakeEmbedder()).evaluate_workspace("imported-workspace")
        alerts = DriftAlertRepository(session).list_by_workspace(1)

    assert result.created_alerts == 1
    assert len(alerts) == 1
    assert alerts[0].alert_type == "needs_review"


def test_evaluator_downgrades_lifecycle_fix_replacement_to_needs_review(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "lifecycle-fix-replacement.db"
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
        session.add(
            Decision(
                workspace_id=workspace.id,
                title="Gracefully stop browser session on agent close with keep_alive=True to prevent asyncio deadlock",
                status="active",
                review_state="accepted",
                problem="Agent shutdown can deadlock when keep_alive=True.",
                context=None,
                constraints="Support keep_alive without reintroducing asyncio deadlock.",
                chosen_option="Update Agent.close() to call await self.browser_session.stop() when keep_alive is True.",
                tradeoffs="Adds an extra shutdown step but prevents deadlock.",
                confidence=0.95,
                created_at=baseline,
            )
        )
        session.add(
                Artifact(
                    workspace_id=workspace.id,
                    type="pull_request",
                    source_id="4003",
                    repo="browser-use/browser-use",
                    title="fix: preserve CDP WebSocket connections on Agent.close() with keep_alive=True",
                    content=(
                        "This fix replaces the previous keep_alive close behavior with a safer shutdown path "
                        "while preserving websocket connections, graceful browser session stop behavior, and the "
                        "broader keep_alive decision."
                    ),
                    author="maintainer",
                    url="https://github.com/browser-use/browser-use/pull/4003",
                    timestamp=baseline + timedelta(days=2),
                    metadata_json=None,
            )
        )
        session.commit()

    _patch_semantic_recall(monkeypatch)
    with Session(engine) as session:
        result = DriftEvaluator(session, embedder=FakeEmbedder()).evaluate_workspace("imported-workspace")
        alerts = DriftAlertRepository(session).list_by_workspace(1)

    assert result.created_alerts == 1
    assert len(alerts) == 1
    assert alerts[0].alert_type == "needs_review"


def test_evaluator_replaces_stale_supersession_when_thread_downgrades(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "stale-supersession-replacement.db"
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
        artifact = Artifact(
            workspace_id=workspace.id,
            type="pull_request",
            source_id="14",
            repo="org/repo",
            title="Replace Redis cache with Dragonfly",
            content="This PR will replace the Redis cache with Dragonfly to reduce cost.",
            author="erin",
            url="https://github.com/org/repo/pull/14",
            timestamp=baseline + timedelta(days=2),
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
        )
        session.add_all([artifact, decision])
        session.commit()

    _patch_semantic_recall(monkeypatch)
    with Session(engine) as session:
        DriftEvaluator(session, embedder=FakeEmbedder()).evaluate_workspace("demo-workspace")

    with Session(engine) as session:
        artifact = session.query(Artifact).filter_by(source_id="14").one()
        artifact.title = "RFC: evaluate Redis follow-up"
        artifact.content = (
            "This RFC evaluates follow-up work around the Redis cache, cache-only policy, and keeping PostgreSQL "
            "primary to keep the current choice healthy."
        )
        session.commit()

    with Session(engine) as session:
        result = DriftEvaluator(session, embedder=FakeEmbedder()).evaluate_workspace("demo-workspace")
        alerts = DriftAlertRepository(session).list_by_workspace(1)

    assert result.created_alerts == 1
    assert len(alerts) == 1
    assert alerts[0].alert_type == "needs_review"
    assert "possible_supersession" not in {alert.alert_type for alert in alerts}


def test_evaluator_replaces_stale_needs_review_when_thread_upgrades(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "stale-needs-review-replacement.db"
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
        artifact = Artifact(
            workspace_id=workspace.id,
            type="issue",
            source_id="15",
            repo="org/repo",
            title="RFC: evaluate Redis follow-up",
            content="This RFC evaluates follow-up work around the Redis cache to keep the current choice healthy.",
            author="erin",
            url="https://github.com/org/repo/issues/15",
            timestamp=baseline + timedelta(days=2),
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
        )
        session.add_all([artifact, decision])
        session.commit()

    _patch_semantic_recall(monkeypatch)
    with Session(engine) as session:
        DriftEvaluator(session, embedder=FakeEmbedder()).evaluate_workspace("demo-workspace")

    with Session(engine) as session:
        artifact = session.query(Artifact).filter_by(source_id="15").one()
        artifact.title = "Replace Redis cache with Dragonfly"
        artifact.content = (
            "This PR will replace the Redis cache with Dragonfly while changing the cache-only policy and the "
            "current PostgreSQL primary setup to reduce cost."
        )
        session.commit()

    with Session(engine) as session:
        result = DriftEvaluator(session, embedder=FakeEmbedder()).evaluate_workspace("demo-workspace")
        alerts = DriftAlertRepository(session).list_by_workspace(1)

    assert result.created_alerts == 1
    assert len(alerts) == 1
    assert alerts[0].alert_type == "possible_supersession"
    assert "needs_review" not in {alert.alert_type for alert in alerts}


def test_evaluator_keeps_semantic_checks_after_rule_checks(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "semantic-order.db"
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
            )
        )
        session.add(
            Artifact(
                workspace_id=workspace.id,
                type="pull_request",
                source_id="4",
                repo="org/repo",
                title="Replace Redis cache and persist sessions",
                content="This proposal will replace the Redis cache and persist session state in Redis as the primary database.",
                author="dana",
                url="https://github.com/org/repo/pull/4",
                timestamp=baseline + timedelta(days=2),
                metadata_json=None,
            )
        )
        session.commit()

    with Session(engine) as session:
        DriftEvaluator(session, embedder=FakeEmbedder()).evaluate_workspace("demo-workspace")
        alerts = DriftAlertRepository(session).list_by_workspace(1)

    assert len(alerts) == 1
    assert alerts[0].alert_type == "possible_drift"
