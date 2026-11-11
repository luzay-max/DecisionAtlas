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

from app.db.models import Artifact, Decision, GitHubAppInstallation, ReviewAuditEvent, SourceRef, Workspace
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
    # Seed the pre-existing job after 0013 so the duplicate-installation
    # preflight isolates the D1b revision rather than rolling back the chain.
    command.upgrade(config, "0013_import_job_lifecycle")
    with Session(engine) as session:
        legacy_workspace = Workspace(
            slug="b07-pg17-legacy", name="B07 legacy workspace",
            owner_scope="b07-pg17-legacy", access_source_type="public",
        )
        unknown_workspace = Workspace(
            slug="b07-pg17-unknown", name="B07 unknown repository",
            owner_scope="b07-pg17-unknown", access_source_type="public",
        )
        session.add_all([legacy_workspace, unknown_workspace])
        session.flush()
        legacy_workspace_id = legacy_workspace.id
        session.add_all(
            [
                GitHubAppInstallation(
                    owner_scope="b07-pg17-legacy",
                    installation_id="170001",
                    account_login="b07-legacy",
                    account_type="Organization",
                ),
                GitHubAppInstallation(
                    owner_scope="duplicate-owner-a",
                    installation_id="duplicate-170002",
                    account_login="duplicate-a",
                    account_type="Organization",
                ),
                GitHubAppInstallation(
                    owner_scope="duplicate-owner-b",
                    installation_id="duplicate-170002",
                    account_login="duplicate-b",
                    account_type="Organization",
                ),
            ]
        )
        session.execute(
            text(
                "INSERT INTO import_jobs "
                "(job_id, workspace_id, repo, mode, status, sync_origin, imported_count) "
                "VALUES (:job_id, :workspace_id, :repo, :mode, :status, :sync_origin, 0)"
            ),
            [
                {
                    "job_id": "b07-pg17-legacy-queued",
                    "workspace_id": legacy_workspace.id,
                    "repo": "https://github.com/B07-Legacy/Repo.git",
                    "mode": "full",
                    "status": "queued",
                    "sync_origin": "manual",
                },
                {
                    "job_id": "b07-pg17-unknown-queued",
                    "workspace_id": unknown_workspace.id,
                    "repo": "https://gitlab.example/private/repo",
                    "mode": "full",
                    "status": "queued",
                    "sync_origin": "manual",
                },
            ],
        )
        session.commit()

    # Duplicate installation identities across owner scopes must block the
    # migration before any D1b DDL is applied.
    with pytest.raises(RuntimeError, match="duplicate GitHub installation_id") as exc_info:
        command.upgrade(config, "head")
    assert "duplicate-owner-a" in str(exc_info.value)
    assert "duplicate-owner-b" in str(exc_info.value)
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT version_num FROM alembic_version")) == (
            "0013_import_job_lifecycle"
        )
        assert not inspect(connection).has_table("import_history_quarantines")
        assert not inspect(connection).has_table("github_webhook_deliveries")
    with Session(engine) as session:
        session.execute(
            text(
                "DELETE FROM github_app_installations "
                "WHERE installation_id='duplicate-170002'"
            )
        )
        session.add(
            GitHubAppInstallation(
                owner_scope=" ",
                installation_id="invalid-owner-scope-170003",
            )
        )
        session.commit()

    with pytest.raises(RuntimeError, match="empty or padded owner_scope"):
        command.upgrade(config, "head")
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT version_num FROM alembic_version")) == (
            "0013_import_job_lifecycle"
        )
        assert not inspect(connection).has_table("import_history_quarantines")

    with Session(engine) as session:
        session.execute(
            text(
                "DELETE FROM github_app_installations "
                "WHERE installation_id='invalid-owner-scope-170003'"
            )
        )
        session.commit()

    command.upgrade(config, "head")

    with engine.connect() as connection:
        assert connection.scalar(text("SELECT version_num FROM alembic_version")) == (
            expected_version
        )
        tables = set(inspect(connection).get_table_names())
        assert {"workspaces", "artifacts", "decisions", "source_refs",
                "review_audit_events", "drift_alerts", "import_history_quarantines",
                "github_webhook_deliveries"}.issubset(tables)
        quarantines = connection.execute(
            text(
                "SELECT owner_scope, scope_kind, canonical_repo_key, status "
                "FROM import_history_quarantines ORDER BY owner_scope"
            )
        ).mappings().all()
        assert [dict(row) for row in quarantines] == [
            {
                "owner_scope": "b07-pg17-legacy",
                "scope_kind": "repository",
                "canonical_repo_key": "b07-legacy/repo",
                "status": "active",
            },
            {
                "owner_scope": "b07-pg17-unknown",
                "scope_kind": "owner_scope",
                "canonical_repo_key": None,
                "status": "active",
            },
        ]
        installation_indexes = {
            index["name"] for index in inspect(connection).get_indexes("github_app_installations")
        }
        assert "uq_github_app_installations_installation_id" in installation_indexes
        installation_constraints = {
            constraint["name"]
            for constraint in inspect(connection).get_check_constraints("github_app_installations")
        }
        assert "ck_github_app_installations_owner_scope" in installation_constraints
        assert "ck_github_app_installations_installation_id" in installation_constraints
        # Explicitly enforce the maintainer's blocked #34 migration boundary.
        assert not {"artifact_revisions", "artifact_current_revisions",
                    "artifact_extraction_runs"} & tables
        columns = {column["name"] for column in inspect(connection).get_columns("source_refs")}
        assert "artifact_revision_id" not in columns

        import_job_column_types = {
            column["name"]: column["type"]
            for column in inspect(connection).get_columns("import_jobs")
        }
        for field in ("heartbeat_at", "lease_expires_at", "available_at", "pause_requested_at"):
            assert getattr(import_job_column_types[field], "timezone", False), (
                f"{field} must preserve an absolute instant on PostgreSQL"
            )
        import_job_columns = set(import_job_column_types)
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
        assert connection.scalar(
            text("SELECT COUNT(*) FROM import_history_quarantines WHERE status='active'")
        ) == 2
        with pytest.raises(IntegrityError):
            with engine.begin() as write_connection:
                write_connection.execute(
                    text(
                        "INSERT INTO import_history_quarantines "
                        "(owner_scope, scope_kind, canonical_repo_key, status, reason_code) "
                        "VALUES ('b07-pg17-legacy', 'repository', 'b07-legacy/repo', "
                        "'active', 'duplicate')"
                    )
                )
        with pytest.raises(IntegrityError):
            with engine.begin() as write_connection:
                write_connection.execute(
                    text(
                        "INSERT INTO import_history_quarantines "
                        "(owner_scope, scope_kind, canonical_repo_key, status, reason_code) "
                        "VALUES ('b07-pg17-unknown', 'owner_scope', NULL, 'active', 'duplicate')"
                    )
                )
        with pytest.raises(IntegrityError):
            with engine.begin() as write_connection:
                write_connection.execute(
                    text(
                        "INSERT INTO github_app_installations "
                        "(owner_scope, installation_id) VALUES ('other-owner', '170001')"
                    )
                )
        with pytest.raises(IntegrityError):
            with engine.begin() as write_connection:
                write_connection.execute(
                    text(
                        "INSERT INTO github_app_installations "
                        "(owner_scope, installation_id) VALUES (' scope-padded ', '170003')"
                    )
                )
        for invalid_installation_id in ("", " 170004 "):
            with pytest.raises(IntegrityError):
                with engine.begin() as write_connection:
                    write_connection.execute(
                        text(
                            "INSERT INTO github_app_installations "
                            "(owner_scope, installation_id) VALUES "
                            "('b07-pg17-legacy', :installation_id)"
                        ),
                        {"installation_id": invalid_installation_id},
                    )
        with pytest.raises(IntegrityError):
            with engine.begin() as write_connection:
                write_connection.execute(
                    text(
                        "UPDATE import_history_quarantines SET status='cleared' "
                        "WHERE owner_scope='b07-pg17-legacy'"
                    )
                )
        with engine.begin() as write_connection:
            write_connection.execute(
                text(
                    "UPDATE import_history_quarantines "
                    "SET status='cleared', cleared_at=clock_timestamp(), "
                    "cleared_by='pg17-reviewer', "
                    "clearance_rationale='Reviewed legacy partial results' "
                    "WHERE owner_scope='b07-pg17-legacy' AND scope_kind='repository'"
                )
            )
            write_connection.execute(
                text(
                    "INSERT INTO import_history_quarantines "
                    "(owner_scope, scope_kind, canonical_repo_key, status, reason_code) "
                    "VALUES ('b07-pg17-legacy', 'repository', 'b07-legacy/repo', "
                    "'active', 'operator-discovered-history')"
                )
            )
        assert connection.scalar(
            text(
                "SELECT COUNT(*) FROM import_history_quarantines "
                "WHERE owner_scope='b07-pg17-legacy' AND status='cleared'"
            )
        ) == 1
        assert connection.scalar(
            text(
                "SELECT COUNT(*) FROM import_history_quarantines "
                "WHERE owner_scope='b07-pg17-legacy' AND status='active'"
            )
        ) == 1
        with engine.begin() as write_connection:
            write_connection.execute(
                text(
                    "INSERT INTO github_webhook_deliveries "
                    "(installation_id, delivery_id, owner_scope, event_name, payload_sha256, disposition) "
                    "VALUES ('170001', 'pg-delivery-1', 'b07-pg17-legacy', 'push', :digest, 'quarantined')"
                ),
                {"digest": "c" * 64},
            )
        with pytest.raises(IntegrityError):
            with engine.begin() as write_connection:
                write_connection.execute(
                    text(
                        "INSERT INTO github_webhook_deliveries "
                        "(installation_id, delivery_id, owner_scope, event_name, payload_sha256, disposition) "
                        "VALUES ('170001', 'pg-delivery-1', 'b07-pg17-legacy', 'push', :digest, 'quarantined')"
                    ),
                    {"digest": "c" * 64},
                )
        with pytest.raises(IntegrityError):
            with engine.begin() as write_connection:
                write_connection.execute(
                    text(
                        "INSERT INTO github_webhook_deliveries "
                        "(installation_id, delivery_id, owner_scope, event_name, payload_sha256, disposition) "
                        "VALUES ('170001', 'pg-delivery-1', 'b07-pg17-legacy', 'push', :digest, 'quarantined')"
                    ),
                    {"digest": "e" * 64},
                )
        with pytest.raises(IntegrityError):
            with engine.begin() as write_connection:
                write_connection.execute(
                    text(
                        "INSERT INTO github_webhook_deliveries "
                        "(installation_id, delivery_id, owner_scope, event_name, payload_sha256, disposition) "
                        "VALUES ('170001', 'pg-delivery-2', 'b07-pg17-legacy', 'push', 'short', 'ignored')"
                    )
                )
        with pytest.raises(IntegrityError):
            with engine.begin() as write_connection:
                write_connection.execute(
                    text(
                        "INSERT INTO github_webhook_deliveries "
                        "(installation_id, delivery_id, owner_scope, event_name, payload_sha256, disposition) "
                        "VALUES ('170001', '', 'b07-pg17-legacy', 'push', :digest, 'ignored')"
                    ),
                    {"digest": "f" * 64},
                )
        with pytest.raises(RuntimeError, match="force transaction rollback"):
            with engine.begin() as write_connection:
                write_connection.execute(
                    text(
                        "INSERT INTO import_jobs "
                        "(job_id, workspace_id, repo, mode, status, sync_origin, imported_count) "
                        "VALUES ('b07-pg17-atomic-rollback', :workspace_id, 'b07-legacy/repo', "
                        "'full', 'queued', 'webhook', 0)"
                    ),
                    {"workspace_id": legacy_workspace_id},
                )
                write_connection.execute(
                    text(
                        "INSERT INTO github_webhook_deliveries "
                        "(installation_id, delivery_id, owner_scope, event_name, payload_sha256, disposition, job_id) "
                        "VALUES ('170001', 'pg-delivery-rollback', 'b07-pg17-legacy', 'push', "
                        ":digest, 'queued', 'b07-pg17-atomic-rollback')"
                    ),
                    {"digest": "f" * 64},
                )
                raise RuntimeError("force transaction rollback")
        assert connection.scalar(
            text("SELECT COUNT(*) FROM import_jobs WHERE job_id='b07-pg17-atomic-rollback'")
        ) == 0
        assert connection.scalar(
            text("SELECT COUNT(*) FROM github_webhook_deliveries WHERE delivery_id='pg-delivery-rollback'")
        ) == 0

    # Downgrade only the new lifecycle schema and prove the legacy job survives.
    command.downgrade(config, "0013_import_job_lifecycle")
    with engine.connect() as connection:
        tables = set(inspect(connection).get_table_names())
        assert "import_history_quarantines" not in tables
        assert "github_webhook_deliveries" not in tables
        assert connection.scalar(
            text("SELECT COUNT(*) FROM import_jobs WHERE job_id LIKE 'b07-pg17-%'")
        ) == 2
        assert connection.scalar(
            text("SELECT COUNT(*) FROM github_app_installations WHERE installation_id='170001'")
        ) == 1

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
