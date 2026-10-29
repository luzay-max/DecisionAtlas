"""expand-only versioned Artifact evidence schema (no writer/backfill)

Revision ID: 0013_artifact_revisions
Revises: 0012_review_audit_events
Create Date: 2026-10-29
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0013_artifact_revisions"
down_revision = "0012_review_audit_events"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # All tables are initially empty; legacy artifacts and refs are untouched.
    op.create_table(
        "artifact_revisions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("artifact_id", sa.Integer(), sa.ForeignKey("artifacts.id"), nullable=False),
        sa.Column("revision_number", sa.Integer(), nullable=False),
        sa.Column("capture_fingerprint", sa.String(length=64), nullable=False),
        sa.Column("content_sha256", sa.String(length=64), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=True),
        sa.Column("url", sa.String(length=512), nullable=True),
        sa.Column("source_metadata_json", sa.JSON(), nullable=True),
        sa.Column("capture_method", sa.String(length=50), nullable=False),
        sa.Column("source_git_blob_sha", sa.String(length=40), nullable=True),
        sa.Column("verification_state", sa.String(length=32), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("artifact_id", "revision_number", name="uq_artifact_revisions_number"),
        sa.UniqueConstraint("artifact_id", "capture_fingerprint", name="uq_artifact_revisions_fingerprint"),
        sa.UniqueConstraint("artifact_id", "id", name="uq_artifact_revisions_artifact_id"),
        sa.CheckConstraint("revision_number >= 1", name="ck_artifact_revisions_number_positive"),
    )
    op.create_index(
        "ix_artifact_revisions_artifact_captured",
        "artifact_revisions", ["artifact_id", "captured_at"],
    )

    # Composite FK prevents pointing an artifact at another artifact's revision.
    op.create_table(
        "artifact_current_revisions",
        sa.Column("artifact_id", sa.Integer(), sa.ForeignKey("artifacts.id"), primary_key=True),
        sa.Column("revision_id", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["artifact_id", "revision_id"],
            ["artifact_revisions.artifact_id", "artifact_revisions.id"],
            name="fk_artifact_current_revision_same_artifact",
        ),
    )

    op.create_table(
        "artifact_extraction_runs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("artifact_revision_id", sa.Integer(), sa.ForeignKey("artifact_revisions.id"), nullable=False),
        sa.Column("extractor_fingerprint", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("candidate_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failure_code", sa.String(length=128), nullable=True),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint(
            "artifact_revision_id", "extractor_fingerprint",
            name="uq_artifact_extraction_revision_extractor",
        ),
    )

    # SQLite does not support adding an FK constraint to an existing table
    # with ordinary ALTER TABLE. Alembic batch mode recreates source_refs on
    # SQLite while preserving existing legacy refs (and runs native ALTER on
    # other supported backends).
    with op.batch_alter_table("source_refs") as batch:
        batch.add_column(sa.Column("artifact_revision_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_source_refs_artifact_revision_same_artifact",
            "artifact_revisions",
            ["artifact_id", "artifact_revision_id"],
            ["artifact_id", "id"],
        )
    op.create_index("ix_source_refs_artifact_revision", "source_refs", ["artifact_revision_id"])


def downgrade() -> None:
    # Deliberately block accidental deletion of captured evidence. A schema-only
    # revert is possible only while no new revision rows have been written.
    connection = op.get_bind()
    has_snapshots = connection.execute(
        sa.text("SELECT COUNT(*) FROM artifact_revisions")
    ).scalar_one()
    if has_snapshots:
        raise RuntimeError(
            "Refusing destructive downgrade: artifact revisions exist; "
            "use a reviewed forward migration and an audited backup/restore plan."
        )

    op.drop_index("ix_source_refs_artifact_revision", table_name="source_refs")
    with op.batch_alter_table("source_refs") as batch:
        batch.drop_constraint("fk_source_refs_artifact_revision_same_artifact", type_="foreignkey")
        batch.drop_column("artifact_revision_id")
    op.drop_table("artifact_extraction_runs")
    op.drop_table("artifact_current_revisions")
    op.drop_index("ix_artifact_revisions_artifact_captured", table_name="artifact_revisions")
    op.drop_table("artifact_revisions")
