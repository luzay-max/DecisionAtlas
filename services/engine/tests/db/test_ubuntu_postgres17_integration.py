"""B04/B07: isolated PostgreSQL 17 integration of the current migrated schema.

This is intentionally not F06b/#34. Uses a fresh, ephemeral public/synthetic
GitHub Actions service DB only; no private sources, paid provider or migration
of a real deployment.
"""
from __future__ import annotations

import os

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
import pytest
from sqlalchemy import create_engine, inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Artifact, Decision, ReviewAuditEvent, SourceRef, Workspace
from app.repositories.decisions import DecisionRepository
from app.retrieval.full_text import full_text_search


def _ci_url() -> str:
    url = os.getenv("DECISIONATLAS_PG17_CI_URL", "")
    if not url.startswith("postgresql+psycopg://"):
        pytest.skip("PostgreSQL integration runs only with explicit CI URL")
    return url


def test_pg17_current_schema_migrate_review_audit_and_scoped_retrieval(monkeypatch) -> None:
    url = _ci_url()
    monkeypatch.setenv("DATABASE_URL", url)
    engine = create_engine(url)
    with engine.connect() as connection:
        assert int(connection.scalar(text("SHOW server_version_num"))) >= 170000
        assert connection.scalar(text(
            "SELECT extversion FROM pg_extension WHERE extname='vector'"
        )) is not None
        # Do not point this test at any existing/local/customer database.
        assert not inspect(connection).has_table("alembic_version")

    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", url)
    expected_version = ScriptDirectory.from_config(config).get_current_head()
    # Exercise the upgrade with a pre-existing job, not only an empty schema.
    command.upgrade(config, "0012_review_audit_events")
    with Session(engine) as session:
        legacy_workspace = Workspace(
            slug="b07-pg17-legacy", name="B07 legacy workspace",
            owner_scope="b07-pg17-legacy", access_source_type="public",
        )
        session.add(legacy_workspace)
        session.flush()
        session.execute(
            text(
                "INSERT INTO import_jobs "
                "(job_id, workspace_id, repo, mode, status, sync_origin, imported_count) "
                "VALUES (:job_id, :workspace_id, :repo, :mode, :status, :sync_origin, 0)"
            ),
            {
                "job_id": "b07-pg17-legacy-queued",
                "workspace_id": legacy_workspace.id,
                "repo": "example/legacy",
                "mode": "full",
                "status": "queued",
                "sync_origin": "manual",
            },
        )
        session.commit()
    command.upgrade(config, "head")

    with engine.connect() as connection:
        assert connection.scalar(text("SELECT version_num FROM alembic_version")) == (
            expected_version
        )
        tables = set(inspect(connection).get_table_names())
        assert {"workspaces", "artifacts", "decisions", "source_refs",
                "review_audit_events", "drift_alerts"}.issubset(tables)
        # Explicitly enforce the maintainer's blocked #34 migration boundary.
        assert not {"artifact_revisions", "artifact_current_revisions",
                    "artifact_extraction_runs"} & tables
        columns = {column["name"] for column in inspect(connection).get_columns("source_refs")}
        assert "artifact_revision_id" not in columns

        import_job_columns = {
            column["name"] for column in inspect(connection).get_columns("import_jobs")
        }
        assert {
            "protocol_version", "worker_id", "lease_token", "lease_generation",
            "heartbeat_at", "lease_expires_at", "attempt_count", "available_at",
            "checkpoint_version", "checkpoint_json", "pause_requested_at",
            "last_failure_category",
        }.issubset(import_job_columns)
        legacy = connection.execute(
            text(
                "SELECT protocol_version, worker_id, lease_token, lease_generation, "
                "heartbeat_at, lease_expires_at, attempt_count, available_at, "
                "checkpoint_version, checkpoint_json, pause_requested_at, "
                "last_failure_category FROM import_jobs "
                "WHERE job_id = 'b07-pg17-legacy-queued'"
            )
        ).mappings().one()
        assert legacy["protocol_version"] == "legacy"
        assert legacy["worker_id"] is None
        assert legacy["lease_token"] is None
        assert legacy["lease_generation"] == 0
        assert legacy["heartbeat_at"] is None
        assert legacy["lease_expires_at"] is None
        assert legacy["attempt_count"] == 0
        assert legacy["available_at"] is None
        assert legacy["checkpoint_version"] == 0
        assert legacy["checkpoint_json"] is None
        assert legacy["pause_requested_at"] is None
        assert legacy["last_failure_category"] is None
        indexes = {index["name"] for index in inspect(connection).get_indexes("import_jobs")}
        assert {"ix_import_jobs_claimable", "ix_import_jobs_lease_expiry"}.issubset(indexes)

    with Session(engine) as session:
        public = Workspace(
            slug="b04-pg17-public", name="Public synthetic workspace",
            owner_scope="b04-public", access_source_type="public",
        )
        other = Workspace(
            slug="b04-pg17-other", name="Other owner",
            owner_scope="b04-other", access_source_type="public",
        )
        session.add_all([public, other])
        session.flush()
        artifact = Artifact(
            workspace_id=public.id, type="doc", source_id="docs/decision.md",
            content="PostgreSQL transaction isolation supports reviewed evidence.",
        )
        session.add(artifact)
        session.flush()
        accepted = Decision(
            workspace_id=public.id, title="PostgreSQL transaction evidence",
            problem="Need reliable audit history", chosen_option="Use PostgreSQL transactions",
            tradeoffs="Operational overhead", review_state="accepted", status="active",
        )
        candidate = Decision(
            workspace_id=public.id, title="PostgreSQL tentative unpublished",
            problem="Not independently reviewed", chosen_option="Do not publish yet",
            tradeoffs="Unverified", review_state="candidate", status="active",
        )
        cross_scope = Decision(
            workspace_id=other.id, title="PostgreSQL private-other-scope",
            problem="Must never show in other workspace", chosen_option="Keep separate",
            tradeoffs="Isolation", review_state="accepted", status="active",
        )
        session.add_all([accepted, candidate, cross_scope])
        session.flush()
        reference = SourceRef(
            decision_id=accepted.id, artifact_id=artifact.id,
            quote="PostgreSQL transaction isolation supports reviewed evidence.",
        )
        audit = ReviewAuditEvent(
            owner_scope="b04-public", workspace_id=public.id,
            actor_username="synthetic-ci-reviewer", actor_role="reviewer",
            target_type="decision", target_id=accepted.id, action="accept",
            previous_state_json={"review_state": "candidate"},
            new_state_json={"review_state": "accepted"},
            rationale="Synthetic migration integration test",
        )
        session.add_all([reference, audit])
        session.commit()
        public_id = public.id
        accepted_id = accepted.id
        reference_id = reference.id

    # Prove data committed to PostgreSQL remains accessible after reconnect.
    engine.dispose()
    engine = create_engine(url)
    with Session(engine) as session:
        accepted_records = DecisionRepository(session).list_by_review_state(
            public_id, "accepted"
        )
        assert [row.id for row in accepted_records] == [accepted_id]
        hits = full_text_search(
            session=session, workspace_slug="b04-pg17-public",
            query="PostgreSQL transaction", review_state="accepted",
        )
        assert len(hits) == 1 and hits[0].decision_id == accepted_id
        assert not full_text_search(
            session=session, workspace_slug="b04-pg17-public",
            query="private-other-scope", review_state="accepted",
        )
        stored = session.get(SourceRef, reference_id)
        assert stored is not None
        assert stored.quote == "PostgreSQL transaction isolation supports reviewed evidence."
        audits = list(session.scalars(
            select(ReviewAuditEvent).where(ReviewAuditEvent.target_id == accepted_id)
        ))
        assert len(audits) == 1
        assert audits[0].new_state_json == {"review_state": "accepted"}

    # PostgreSQL must enforce referential integrity: a SourceRef may not
    # point to an artifact that does not exist. Leave existing evidence intact.
    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(
                text("INSERT INTO source_refs (decision_id, artifact_id, quote) "
                     "VALUES (:decision_id, -99999, 'should reject')"),
                {"decision_id": accepted_id},
            )
    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(text(
                "INSERT INTO workspaces (slug, name) VALUES "
                "('b04-pg17-public', 'duplicate must fail')"
            ))
    with engine.connect() as connection:
        assert connection.scalar(
            text("SELECT COUNT(*) FROM source_refs WHERE id=:ref_id"),
            {"ref_id": reference_id},
        ) == 1
        assert connection.scalar(
            text("SELECT COUNT(*) FROM review_audit_events WHERE target_id=:id"),
            {"id": accepted_id},
        ) == 1

    # Downgrade only the new lifecycle schema and prove the legacy job survives.
    command.downgrade(config, "0012_review_audit_events")
    with engine.connect() as connection:
        columns = {column["name"] for column in inspect(connection).get_columns("import_jobs")}
        assert "protocol_version" not in columns
        assert "lease_generation" not in columns
        indexes = {index["name"] for index in inspect(connection).get_indexes("import_jobs")}
        assert not {"ix_import_jobs_claimable", "ix_import_jobs_lease_expiry"} & indexes
        assert connection.scalar(
            text("SELECT job_id FROM import_jobs WHERE job_id = 'b07-pg17-legacy-queued'")
        ) == "b07-pg17-legacy-queued"
    engine.dispose()
