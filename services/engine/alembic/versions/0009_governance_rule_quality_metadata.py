"""add governance rule quality metadata

Revision ID: 0009_governance_rule_quality
Revises: 0008_governance_ingest
Create Date: 2026-05-07
"""

from alembic import op
import sqlalchemy as sa


revision = "0009_governance_rule_quality"
down_revision = "0008_governance_ingest"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "governance_rule_drafts",
        sa.Column("rule_type", sa.String(length=50), nullable=False, server_default="standard"),
    )
    op.add_column("governance_rule_drafts", sa.Column("extraction_reason", sa.Text(), nullable=True))
    op.add_column("governance_rule_drafts", sa.Column("review_rationale", sa.Text(), nullable=True))
    op.add_column(
        "governance_rule_drafts",
        sa.Column("lifecycle_status", sa.String(length=50), nullable=False, server_default="current"),
    )
    op.add_column("governance_rule_drafts", sa.Column("superseded_by_rule_id", sa.Integer(), nullable=True))
    op.create_index(
        "ix_governance_rule_drafts_owner_lifecycle",
        "governance_rule_drafts",
        ["owner_scope", "lifecycle_status"],
    )


def downgrade() -> None:
    op.drop_index("ix_governance_rule_drafts_owner_lifecycle", table_name="governance_rule_drafts")
    op.drop_column("governance_rule_drafts", "superseded_by_rule_id")
    op.drop_column("governance_rule_drafts", "lifecycle_status")
    op.drop_column("governance_rule_drafts", "review_rationale")
    op.drop_column("governance_rule_drafts", "extraction_reason")
    op.drop_column("governance_rule_drafts", "rule_type")
