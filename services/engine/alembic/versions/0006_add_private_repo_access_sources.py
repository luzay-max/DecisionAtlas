"""add private repo access sources

Revision ID: 0006_private_repo_access_sources
Revises: 0005_add_github_app_sync_models
Create Date: 2026-04-14 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0006_private_repo_access_sources"
down_revision = "0005_add_github_app_sync_models"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "github_token_access_sources",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("owner_scope", sa.String(length=120), nullable=False),
        sa.Column("source_ref", sa.String(length=255), nullable=False),
        sa.Column("display_label", sa.String(length=255), nullable=False),
        sa.Column("repo_identity", sa.String(length=255), nullable=False),
        sa.Column("token_secret", sa.Text(), nullable=False),
        sa.Column("authorization_status", sa.String(length=50), nullable=False, server_default="authorized"),
        sa.Column("last_validated_at", sa.DateTime(), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("owner_scope", "source_ref", name="uq_github_token_access_sources_scope_ref"),
    )


def downgrade() -> None:
    op.drop_table("github_token_access_sources")
