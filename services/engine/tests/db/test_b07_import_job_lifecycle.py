from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session

from app.db.models import Workspace


def test_lifecycle_migration_preserves_existing_jobs_as_legacy_and_downgrades(
    tmp_path: Path, monkeypatch
) -> None:
    db_path = tmp_path / "b07-lifecycle-migration.db"
    url = f"sqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", url)
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", url)

    command.upgrade(config, "0012_review_audit_events")
    engine = create_engine(url)
    with Session(engine) as session:
        workspace = Workspace(
            slug="b07-legacy-workspace",
            name="B07 legacy workspace",
            owner_scope="b07-test",
            access_source_type="public",
        )
        session.add(workspace)
        session.flush()
        session.execute(
            text(
                "INSERT INTO import_jobs "
                "(job_id, workspace_id, repo, mode, status, sync_origin, imported_count) "
                "VALUES (:job_id, :workspace_id, :repo, :mode, :status, :sync_origin, 0)"
            ),
            {
                "job_id": "legacy-queued-job",
                "workspace_id": workspace.id,
                "repo": "example/repo",
                "mode": "full",
                "status": "queued",
                "sync_origin": "manual",
            },
        )
        session.commit()

    command.upgrade(config, "head")
    with engine.connect() as connection:
        columns = {column["name"] for column in inspect(connection).get_columns("import_jobs")}
        expected = {
            "protocol_version", "worker_id", "lease_token", "lease_generation",
            "heartbeat_at", "lease_expires_at", "attempt_count", "available_at",
            "checkpoint_version", "checkpoint_json", "pause_requested_at",
            "last_failure_category",
        }
        assert expected.issubset(columns)
        legacy = connection.execute(
            text(
                "SELECT protocol_version, worker_id, lease_token, lease_generation, "
                "heartbeat_at, lease_expires_at, attempt_count, checkpoint_version, "
                "checkpoint_json, pause_requested_at "
                "FROM import_jobs WHERE job_id = 'legacy-queued-job'"
            )
        ).mappings().one()
        assert legacy["protocol_version"] == "legacy"
        assert legacy["worker_id"] is None
        assert legacy["lease_token"] is None
        assert legacy["lease_generation"] == 0
        assert legacy["heartbeat_at"] is None
        assert legacy["lease_expires_at"] is None
        assert legacy["attempt_count"] == 0
        assert legacy["checkpoint_version"] == 0
        assert legacy["checkpoint_json"] is None
        assert legacy["pause_requested_at"] is None

        indexes = {index["name"] for index in inspect(connection).get_indexes("import_jobs")}
        assert {"ix_import_jobs_claimable", "ix_import_jobs_lease_expiry"}.issubset(indexes)

    command.downgrade(config, "0012_review_audit_events")
    with engine.connect() as connection:
        columns = {column["name"] for column in inspect(connection).get_columns("import_jobs")}
        assert "protocol_version" not in columns
        assert "lease_generation" not in columns
        assert connection.scalar(text("SELECT job_id FROM import_jobs")) == "legacy-queued-job"
    engine.dispose()
