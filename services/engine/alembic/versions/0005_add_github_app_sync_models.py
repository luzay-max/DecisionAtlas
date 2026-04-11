"""add github app sync models

Revision ID: 0005_add_github_app_sync_models
Revises: 0004_add_artifact_chunk_metadata
Create Date: 2026-04-11
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from urllib.parse import urlparse


revision = "0005_add_github_app_sync_models"
down_revision = "0004_add_artifact_chunk_metadata"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "workspaces",
        sa.Column("owner_scope", sa.String(length=120), nullable=False, server_default="local-default"),
    )
    op.add_column("workspaces", sa.Column("repo_identity", sa.String(length=255), nullable=True))
    op.add_column(
        "workspaces",
        sa.Column("access_source_type", sa.String(length=50), nullable=False, server_default="public"),
    )
    op.add_column("workspaces", sa.Column("access_source_ref", sa.String(length=255), nullable=True))

    op.create_table(
        "github_app_installations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("owner_scope", sa.String(length=120), nullable=False),
        sa.Column("installation_id", sa.String(length=255), nullable=False),
        sa.Column("account_login", sa.String(length=255), nullable=True),
        sa.Column("account_type", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.add_column(
        "import_jobs",
        sa.Column("sync_origin", sa.String(length=50), nullable=False, server_default="manual"),
    )
    op.add_column("import_jobs", sa.Column("trigger_event", sa.String(length=100), nullable=True))
    op.add_column("import_jobs", sa.Column("trigger_delivery_id", sa.String(length=255), nullable=True))

    connection = op.get_bind()
    rows = connection.execute(sa.text("SELECT id, repo_url FROM workspaces")).fetchall()
    for row in rows:
        repo_identity = _repo_identity(row.repo_url)
        connection.execute(
            sa.text("UPDATE workspaces SET repo_identity = :repo_identity WHERE id = :workspace_id"),
            {"repo_identity": repo_identity, "workspace_id": row.id},
        )


def downgrade() -> None:
    op.drop_column("import_jobs", "trigger_delivery_id")
    op.drop_column("import_jobs", "trigger_event")
    op.drop_column("import_jobs", "sync_origin")
    op.drop_table("github_app_installations")
    op.drop_column("workspaces", "access_source_ref")
    op.drop_column("workspaces", "access_source_type")
    op.drop_column("workspaces", "repo_identity")
    op.drop_column("workspaces", "owner_scope")


def _repo_identity(repo_url: str | None) -> str | None:
    if not repo_url:
        return None
    normalized = repo_url.rstrip("/")
    if normalized.endswith(".git"):
        normalized = normalized[:-4]
    parsed = urlparse(normalized)
    if parsed.netloc not in {"github.com", "www.github.com"}:
        return None
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        return None
    return f"{parts[0]}/{parts[1]}"
