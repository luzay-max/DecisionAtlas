"""File-backed SQLite 0012 -> 0013 migration, backup, recovery, and restart.

Only synthetic data is used. No runtime revision capture or private data.
"""

from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import Session

from app.db.models import ArtifactCurrentRevision, ArtifactRevision, SourceRef


def _alembic_config(db_path: Path, monkeypatch) -> Config:
    url = f"sqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", url)
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", url)
    return config


def _engine_with_fks(db_path: Path):
    engine = create_engine(f"sqlite:///{db_path}")

    @event.listens_for(engine, "connect")
    def _enable_fk(dbapi_connection, _record):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    return engine


def _sqlite_online_backup(source: Path, destination: Path) -> None:
    # SQLite's native backup API, not a hot copy of a live WAL database.
    with sqlite3.connect(source) as source_db, sqlite3.connect(destination) as destination_db:
        source_db.backup(destination_db)


def test_file_sqlite_migration_can_be_backed_up_restored_and_restarted(
    tmp_path: Path, monkeypatch
) -> None:
    db_path = tmp_path / "workspace.db"
    before_path = tmp_path / "before-0013.sqlite3"
    after_path = tmp_path / "after-0013.sqlite3"
    restored_path = tmp_path / "restored.sqlite3"
    config = _alembic_config(db_path, monkeypatch)
    command.upgrade(config, "0012_review_audit_events")

    engine = _engine_with_fks(db_path)
    with engine.begin() as connection:
        workspace_id = connection.execute(text(
            "INSERT INTO workspaces (slug, name) VALUES ('backup-legacy', 'Backup Legacy')"
        )).lastrowid
        artifact_id = connection.execute(text(
            "INSERT INTO artifacts (workspace_id, type, source_id, content) "
            "VALUES (:workspace, 'issue', 'historic', 'A historically reviewed quote')"
        ), {"workspace": workspace_id}).lastrowid
        decision_id = connection.execute(text(
            "INSERT INTO decisions (workspace_id, title, problem, chosen_option, tradeoffs) "
            "VALUES (:workspace, 'Choice', 'Problem', 'Selected', 'Tradeoff')"
        ), {"workspace": workspace_id}).lastrowid
        source_ref_id = connection.execute(text(
            "INSERT INTO source_refs (decision_id, artifact_id, quote) "
            "VALUES (:decision, :artifact, 'A historically reviewed quote')"
        ), {"decision": decision_id, "artifact": artifact_id}).lastrowid
    engine.dispose()

    _sqlite_online_backup(db_path, before_path)
    command.upgrade(config, "head")

    engine = _engine_with_fks(db_path)
    with engine.begin() as connection:
        revision_id = connection.execute(text(
            "INSERT INTO artifact_revisions "
            "(artifact_id, revision_number, capture_fingerprint, content_sha256, "
            "content, capture_method, verification_state) "
            "VALUES (:artifact, 1, :fingerprint, :sha, 'Current synthetic text', "
            "'test_only', 'local_hash_only')"
        ), {
            "artifact": artifact_id,
            "fingerprint": "a" * 64,
            "sha": hashlib.sha256(b"Current synthetic text").hexdigest(),
        }).lastrowid
        connection.execute(text(
            "INSERT INTO artifact_current_revisions (artifact_id, revision_id) "
            "VALUES (:artifact, :revision)"
        ), {"artifact": artifact_id, "revision": revision_id})
        assert connection.scalar(text(
            "SELECT COUNT(*) FROM source_refs "
            "WHERE id=:id AND artifact_revision_id IS NULL"
        ), {"id": source_ref_id}) == 1
        assert connection.scalar(text(
            "SELECT generation FROM artifact_current_revisions WHERE artifact_id=:artifact"
        ), {"artifact": artifact_id}) == 1
    engine.dispose()

    _sqlite_online_backup(db_path, after_path)
    # Restore the backed-up DB into a new writable database path, then simulate
    # application restart by reconnecting (not inspecting an already-open pool).
    _sqlite_online_backup(after_path, restored_path)
    restored_engine = _engine_with_fks(restored_path)
    with restored_engine.connect() as connection:
        assert connection.scalar(text("PRAGMA integrity_check")) == "ok"
        assert connection.scalar(text("PRAGMA foreign_key_check")) is None
        assert connection.scalar(text("PRAGMA foreign_keys")) == 1
        assert connection.scalar(text("SELECT version_num FROM alembic_version")) == "0013_artifact_revisions"
        assert connection.scalar(text("SELECT content FROM artifacts WHERE id=:id"), {"id": artifact_id}) == "A historically reviewed quote"
        assert connection.scalar(text(
            "SELECT quote FROM source_refs WHERE id=:id AND artifact_revision_id IS NULL"
        ), {"id": source_ref_id}) == "A historically reviewed quote"
        assert "generation" in {c["name"] for c in inspect(connection).get_columns("artifact_current_revisions")}
    with Session(restored_engine) as session:
        assert session.get(ArtifactCurrentRevision, artifact_id).generation == 1
        revision = session.get(ArtifactRevision, revision_id)
        assert revision.content == "Current synthetic text"
        assert session.get(SourceRef, source_ref_id).artifact_revision_id is None

    # A *new* connection to the restored file must enforce FKs too.
    with restored_engine.connect() as connection:
        assert connection.scalar(text("PRAGMA foreign_keys")) == 1
    restored_engine.dispose()

    # Pre-migration backup is independently recoverable, so an operator can
    # choose a tested forward-recovery route without destructively downgrading.
    legacy_engine = _engine_with_fks(before_path)
    with legacy_engine.connect() as connection:
        assert connection.scalar(text("PRAGMA integrity_check")) == "ok"
        assert "artifact_current_revisions" not in inspect(connection).get_table_names()
        assert connection.scalar(text("SELECT COUNT(*) FROM source_refs")) == 1
    legacy_engine.dispose()
