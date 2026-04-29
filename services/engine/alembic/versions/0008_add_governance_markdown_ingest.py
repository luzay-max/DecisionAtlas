"""add governance markdown ingest

Revision ID: 0008_add_governance_markdown_ingest
Revises: 0007_auth_sessions_roles
Create Date: 2026-04-29
"""

from alembic import op
import sqlalchemy as sa


revision = "0008_add_governance_markdown_ingest"
down_revision = "0007_auth_sessions_roles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "governance_documents",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("owner_scope", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("document_type", sa.String(length=50), nullable=False),
        sa.Column("scope", sa.String(length=80), nullable=False, server_default="all"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
        sa.Column("source_path", sa.String(length=512), nullable=True),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_governance_documents_owner_scope", "governance_documents", ["owner_scope"])
    op.create_index(
        "ix_governance_documents_owner_type",
        "governance_documents",
        ["owner_scope", "document_type"],
    )

    op.create_table(
        "governance_rule_drafts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("owner_scope", sa.String(length=120), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(length=50), nullable=False, server_default="warning"),
        sa.Column("scope", sa.String(length=80), nullable=False, server_default="all"),
        sa.Column("rationale", sa.Text(), nullable=True),
        sa.Column("source_excerpt", sa.Text(), nullable=False),
        sa.Column("review_state", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="draft"),
        sa.Column("reviewed_by", sa.String(length=120), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["governance_documents.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_governance_rule_drafts_owner_scope", "governance_rule_drafts", ["owner_scope"])
    op.create_index(
        "ix_governance_rule_drafts_owner_review",
        "governance_rule_drafts",
        ["owner_scope", "review_state"],
    )


def downgrade() -> None:
    op.drop_index("ix_governance_rule_drafts_owner_review", table_name="governance_rule_drafts")
    op.drop_index("ix_governance_rule_drafts_owner_scope", table_name="governance_rule_drafts")
    op.drop_table("governance_rule_drafts")
    op.drop_index("ix_governance_documents_owner_type", table_name="governance_documents")
    op.drop_index("ix_governance_documents_owner_scope", table_name="governance_documents")
    op.drop_table("governance_documents")
