"""add governance rule lifecycle rationale

Revision ID: 0010_rule_lifecycle_rationale
Revises: 0009_governance_rule_quality
Create Date: 2026-05-08 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0010_rule_lifecycle_rationale"
down_revision = "0009_governance_rule_quality"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("governance_rule_drafts", sa.Column("lifecycle_rationale", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("governance_rule_drafts", "lifecycle_rationale")
