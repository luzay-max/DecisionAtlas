"""Real PostgreSQL 17 migration + restore assertions for the schema-only Draft.

Runs only with the explicitly configured synthetic CI database. The two tests
execute in separate processes around pg_dump/pg_restore in GitHub Actions.
"""

from __future__ import annotations

import hashlib
import os

from alembic import command
from alembic.config import Config
import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import IntegrityError


def _postgres_url(name: str) -> str:
    value = os.getenv(name)
    if not value:
        pytest.skip(f"{name} is required for PostgreSQL integration acceptance")
    if not value.startswith("postgresql+psycopg://"):
        pytest.fail("PG schema test requires explicit postgresql+psycopg connection")
    return value


def _create_revision(connection, artifact_id: int, number: int, content: str) -> int:
    return connection.execute(text(
        "INSERT INTO artifact_revisions "
        "(artifact_id, revision_number, capture_fingerprint, content_sha256, "
        "content, capture_method, verification_state) "
        "VALUES (:artifact, :number, :fingerprint, :sha, :content, "
        "'synthetic_ci', 'local_hash_only') RETURNING id"
    ), {
        "artifact": artifact_id,
        "number": number,
        "fingerprint": hashlib.sha256(f"capture-{number}".encode()).hexdigest(),
        "sha": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "content": content,
    }).scalar_one()


def test_postgres_upgrade_from_0012_preserves_legacy_and_enforces_cas(monkeypatch) -> None:
    url = _postgres_url("DECISIONATLAS_SCHEMA_PG_URL")
    monkeypatch.setenv("DATABASE_URL", url)
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", url)
    engine = create_engine(url)
    # A fresh CI service database is mandatory. No existing/private DB can be targeted.
    with engine.connect() as connection:
        assert not inspect(connection).has_table("alembic_version")
        assert connection.scalar(text(
            "SELECT extversion FROM pg_extension WHERE extname='vector'"
        )) is not None, "CI PostgreSQL image must include the pgvector extension"
        assert connection.scalar(text("SHOW server_version_num")) >= "170000"

    command.upgrade(cfg, "0012_review_audit_events")
    with engine.begin() as connection:
        workspace = connection.execute(text(
            "INSERT INTO workspaces (slug, name) "
            "VALUES ('schema-pg-ci', 'Postgres synthetic CI') RETURNING id"
        )).scalar_one()
        artifact_a = connection.execute(text(
            "INSERT INTO artifacts (workspace_id, type, source_id, content) "
            "VALUES (:ws, 'issue', 'pg-legacy-a', 'Legacy reviewed quote') RETURNING id"
        ), {"ws": workspace}).scalar_one()
        artifact_b = connection.execute(text(
            "INSERT INTO artifacts (workspace_id, type, source_id, content) "
            "VALUES (:ws, 'issue', 'pg-legacy-b', 'Other artifact') RETURNING id"
        ), {"ws": workspace}).scalar_one()
        decision = connection.execute(text(
            "INSERT INTO decisions (workspace_id, title, problem, chosen_option, tradeoffs) "
            "VALUES (:ws, 'Decision', 'Problem', 'Keep', 'Cost') RETURNING id"
        ), {"ws": workspace}).scalar_one()
        legacy_ref = connection.execute(text(
            "INSERT INTO source_refs (decision_id, artifact_id, quote) "
            "VALUES (:decision, :artifact, 'Legacy reviewed quote') RETURNING id"
        ), {"decision": decision, "artifact": artifact_a}).scalar_one()

    command.upgrade(cfg, "head")
    with engine.begin() as connection:
        assert connection.scalar(text(
            "SELECT version_num FROM alembic_version"
        )) == "0013_artifact_revisions"
        assert connection.scalar(text(
            "SELECT COUNT(*) FROM source_refs WHERE id=:id "
            "AND artifact_revision_id IS NULL AND quote='Legacy reviewed quote'"
        ), {"id": legacy_ref}) == 1
        assert connection.scalar(text("SELECT COUNT(*) FROM artifact_revisions")) == 0
        pointer_columns = {c["name"]: c for c in inspect(connection).get_columns("artifact_current_revisions")}
        assert pointer_columns["generation"]["nullable"] is False
        assert "BIGINT" in str(pointer_columns["generation"]["type"]).upper()

        revision_a = _create_revision(connection, artifact_a, 1, "Revision A")
        revision_b = _create_revision(connection, artifact_a, 2, "Revision B")
        connection.execute(text(
            "INSERT INTO artifact_current_revisions (artifact_id, revision_id) "
            "VALUES (:artifact, :revision)"
        ), {"artifact": artifact_a, "revision": revision_a})
        assert connection.scalar(text(
            "SELECT generation FROM artifact_current_revisions WHERE artifact_id=:artifact"
        ), {"artifact": artifact_a}) == 1

    # A revision belonging to artifact A must never be referenced by B.
    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(text(
                "INSERT INTO artifact_current_revisions (artifact_id, revision_id) "
                "VALUES (:other, :revision)"
            ), {"other": artifact_b, "revision": revision_a})
    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(text(
                "INSERT INTO source_refs (decision_id, artifact_id, artifact_revision_id, quote) "
                "VALUES (:decision, :other, :revision, 'Invalid cross-artifact')"
            ), {"decision": decision, "other": artifact_b, "revision": revision_a})
    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(text(
                "UPDATE artifact_current_revisions SET generation=0 WHERE artifact_id=:artifact"
            ), {"artifact": artifact_a})

    # A -> B -> A must change generation even though the revision ID returns to A.
    with engine.begin() as connection:
        to_b = connection.execute(text(
            "UPDATE artifact_current_revisions SET revision_id=:new, generation=generation+1 "
            "WHERE artifact_id=:artifact AND revision_id=:old AND generation=1"
        ), {"artifact": artifact_a, "old": revision_a, "new": revision_b})
        assert to_b.rowcount == 1
        to_a = connection.execute(text(
            "UPDATE artifact_current_revisions SET revision_id=:new, generation=generation+1 "
            "WHERE artifact_id=:artifact AND revision_id=:old AND generation=2"
        ), {"artifact": artifact_a, "old": revision_b, "new": revision_a})
        assert to_a.rowcount == 1
        stale = connection.execute(text(
            "UPDATE artifact_current_revisions SET revision_id=:new, generation=generation+1 "
            "WHERE artifact_id=:artifact AND revision_id=:old AND generation=1"
        ), {"artifact": artifact_a, "old": revision_a, "new": revision_b})
        assert stale.rowcount == 0
        assert connection.scalar(text(
            "SELECT generation FROM artifact_current_revisions WHERE artifact_id=:artifact"
        ), {"artifact": artifact_a}) == 3
    engine.dispose()


def test_postgres_restored_dump_retains_legacy_and_revision_rows() -> None:
    url = _postgres_url("DECISIONATLAS_SCHEMA_PG_RESTORED_URL")
    engine = create_engine(url)
    with engine.connect() as connection:
        assert connection.scalar(text("SHOW server_version_num")) >= "170000"
        assert connection.scalar(text(
            "SELECT extversion FROM pg_extension WHERE extname='vector'"
        )) is not None
        assert connection.scalar(text(
            "SELECT version_num FROM alembic_version"
        )) == "0013_artifact_revisions"
        assert connection.scalar(text(
            "SELECT COUNT(*) FROM source_refs "
            "WHERE artifact_revision_id IS NULL AND quote='Legacy reviewed quote'"
        )) == 1
        assert connection.scalar(text("SELECT COUNT(*) FROM artifact_revisions")) == 2
        assert connection.scalar(text(
            "SELECT COUNT(*) FROM artifact_current_revisions WHERE generation=3"
        )) == 1
        assert connection.scalar(text(
            "SELECT COUNT(*) FROM artifacts WHERE content='Legacy reviewed quote'"
        )) == 1
        assert inspect(connection).has_table("artifact_extraction_runs")
    engine.dispose()
