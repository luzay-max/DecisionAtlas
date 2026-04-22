"""add auth sessions and owner memberships

Revision ID: 0007_auth_sessions_roles
Revises: 0006_private_repo_access_sources
Create Date: 2026-04-14 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0007_auth_sessions_roles"
down_revision = "0006_private_repo_access_sources"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "actors",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(length=120), nullable=False, unique=True),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("is_bootstrap", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "owner_scopes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("scope_key", sa.String(length=120), nullable=False, unique=True),
        sa.Column("scope_type", sa.String(length=50), nullable=False, server_default="local"),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "owner_scope_memberships",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("actors.id"), nullable=False),
        sa.Column("owner_scope_id", sa.Integer(), sa.ForeignKey("owner_scopes.id"), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False, server_default="viewer"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("actor_id", "owner_scope_id", name="uq_owner_scope_memberships_actor_scope"),
    )

    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("session_token", sa.String(length=128), nullable=False, unique=True),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("actors.id"), nullable=False),
        sa.Column("current_owner_scope_id", sa.Integer(), sa.ForeignKey("owner_scopes.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("last_seen_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("auth_sessions")
    op.drop_table("owner_scope_memberships")
    op.drop_table("owner_scopes")
    op.drop_table("actors")
