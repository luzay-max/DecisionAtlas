"""add artifact chunk metadata

Revision ID: 0004_add_artifact_chunk_metadata
Revises: 0003_add_import_job_summary
Create Date: 2026-04-09
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0004_add_artifact_chunk_metadata"
down_revision = "0003_add_import_job_summary"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("artifact_chunks", sa.Column("metadata_json", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("artifact_chunks", "metadata_json")
