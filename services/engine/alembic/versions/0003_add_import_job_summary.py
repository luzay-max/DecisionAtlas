"""add import job summary

Revision ID: 0003_add_import_job_summary
Revises: 0002_add_import_jobs
Create Date: 2026-03-20
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0003_add_import_job_summary"
down_revision = "0002_add_import_jobs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("import_jobs", sa.Column("summary_json", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("import_jobs", "summary_json")
