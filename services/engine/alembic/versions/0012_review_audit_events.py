"""add review audit events

Revision ID: 0012_review_audit_events
Revises: 0011_team_accounts_workspaces
Create Date: 2026-06-08 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0012_review_audit_events"
down_revision = "0011_team_accounts_workspaces"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "review_audit_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("owner_scope", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.Integer(), sa.ForeignKey("workspaces.id"), nullable=True),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("actors.id"), nullable=True),
        sa.Column("actor_username", sa.String(length=120), nullable=False),
        sa.Column("actor_role", sa.String(length=50), nullable=False),
        sa.Column("target_type", sa.String(length=50), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("previous_state_json", sa.JSON(), nullable=True),
        sa.Column("new_state_json", sa.JSON(), nullable=True),
        sa.Column("rationale", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_review_audit_events_owner_target", "review_audit_events", ["owner_scope", "target_type", "target_id"])
    op.create_index("ix_review_audit_events_workspace", "review_audit_events", ["workspace_id"])

    op.add_column("drift_alerts", sa.Column("handled_by", sa.String(length=120), nullable=True))
    op.add_column("drift_alerts", sa.Column("handled_at", sa.DateTime(), nullable=True))
    op.add_column("drift_alerts", sa.Column("disposition_rationale", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("drift_alerts", "disposition_rationale")
    op.drop_column("drift_alerts", "handled_at")
    op.drop_column("drift_alerts", "handled_by")
    op.drop_index("ix_review_audit_events_workspace", table_name="review_audit_events")
    op.drop_index("ix_review_audit_events_owner_target", table_name="review_audit_events")
    op.drop_table("review_audit_events")
