"""add durable import job lifecycle metadata

Revision ID: 0013_import_job_lifecycle
Revises: 0012_review_audit_events
Create Date: 2026-11-10
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0013_import_job_lifecycle"
down_revision = "0012_review_audit_events"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Existing rows are deliberately marked legacy. A queued status alone is
    # not evidence that an old BackgroundTasks job never executed.
    op.add_column(
        "import_jobs",
        sa.Column("protocol_version", sa.String(length=20), nullable=False, server_default="legacy"),
    )
    op.add_column("import_jobs", sa.Column("worker_id", sa.String(length=128), nullable=True))
    op.add_column("import_jobs", sa.Column("lease_token", sa.String(length=64), nullable=True))
    op.add_column(
        "import_jobs",
        sa.Column("lease_generation", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column("import_jobs", sa.Column("heartbeat_at", sa.DateTime(), nullable=True))
    op.add_column("import_jobs", sa.Column("lease_expires_at", sa.DateTime(), nullable=True))
    op.add_column(
        "import_jobs",
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column("import_jobs", sa.Column("available_at", sa.DateTime(), nullable=True))
    op.add_column(
        "import_jobs",
        sa.Column("checkpoint_version", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column("import_jobs", sa.Column("checkpoint_json", sa.JSON(), nullable=True))
    op.add_column("import_jobs", sa.Column("pause_requested_at", sa.DateTime(), nullable=True))
    op.add_column("import_jobs", sa.Column("last_failure_category", sa.String(length=80), nullable=True))

    op.create_index(
        "ix_import_jobs_claimable",
        "import_jobs",
        ["protocol_version", "status", "available_at", "created_at", "id"],
    )
    op.create_index(
        "ix_import_jobs_lease_expiry",
        "import_jobs",
        ["status", "lease_expires_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_import_jobs_lease_expiry", table_name="import_jobs")
    op.drop_index("ix_import_jobs_claimable", table_name="import_jobs")
    op.drop_column("import_jobs", "last_failure_category")
    op.drop_column("import_jobs", "pause_requested_at")
    op.drop_column("import_jobs", "checkpoint_json")
    op.drop_column("import_jobs", "checkpoint_version")
    op.drop_column("import_jobs", "available_at")
    op.drop_column("import_jobs", "attempt_count")
    op.drop_column("import_jobs", "lease_expires_at")
    op.drop_column("import_jobs", "heartbeat_at")
    op.drop_column("import_jobs", "lease_generation")
    op.drop_column("import_jobs", "lease_token")
    op.drop_column("import_jobs", "worker_id")
    op.drop_column("import_jobs", "protocol_version")
