"""add team account status and workspace memberships

Revision ID: 0011_team_accounts_workspaces
Revises: 0010_rule_lifecycle_rationale
Create Date: 2026-05-20 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0011_team_accounts_workspaces"
down_revision = "0010_rule_lifecycle_rationale"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("actors", sa.Column("status", sa.String(length=50), nullable=False, server_default="active"))
    op.add_column("actors", sa.Column("disabled_at", sa.DateTime(), nullable=True))

    op.create_table(
        "workspace_memberships",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("workspace_id", sa.Integer(), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("actors.id"), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False, server_default="viewer"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("workspace_id", "actor_id", name="uq_workspace_memberships_workspace_actor"),
    )


def downgrade() -> None:
    op.drop_table("workspace_memberships")
    op.drop_column("actors", "disabled_at")
    op.drop_column("actors", "status")
