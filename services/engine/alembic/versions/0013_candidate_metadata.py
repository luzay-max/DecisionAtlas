"""add bounded candidate extraction metadata

Revision ID: 0013_candidate_metadata
Revises: 0012_review_audit_events
Create Date: 2026-07-15 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0013_candidate_metadata"
down_revision = "0012_review_audit_events"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("decisions", sa.Column("candidate_metadata_json", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("decisions", "candidate_metadata_json")
