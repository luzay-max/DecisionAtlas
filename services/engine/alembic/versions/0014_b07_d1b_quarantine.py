"""add legacy history quarantine and webhook delivery ledger

Revision ID: 0014_b07_d1b_quarantine
Revises: 0013_import_job_lifecycle
Create Date: 2026-11-11
"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlsplit

from alembic import op
import sqlalchemy as sa


revision = "0014_b07_d1b_quarantine"
down_revision = "0013_import_job_lifecycle"
branch_labels = None
depends_on = None


_REPOSITORY_PART = re.compile(r"^[A-Za-z0-9_.-]+$")


def _canonical_repository(value: str | None) -> str | None:
    """Return a strict GitHub owner/repo key; never guess malformed identities."""
    if value is None:
        return None
    candidate = value.strip()
    if not candidate:
        return None

    if "://" in candidate:
        parsed = urlsplit(candidate)
        if (
            parsed.scheme.lower() != "https"
            or parsed.hostname is None
            or parsed.hostname.lower() != "github.com"
            or parsed.username is not None
            or parsed.password is not None
            or parsed.port is not None
            or parsed.query
            or parsed.fragment
        ):
            return None
        path = parsed.path
        if not path.startswith("/"):
            return None
        path = path[1:]
        if path.endswith("/"):
            path = path[:-1]
    else:
        path = candidate
        if path.startswith("/") or path.endswith("/"):
            return None

    if path.endswith(".git"):
        path = path[:-4]
    parts = path.split("/")
    if len(parts) != 2:
        return None
    owner, repository = parts
    if not owner or not repository:
        return None
    if owner in {".", ".."} or repository in {".", ".."}:
        return None
    if not _REPOSITORY_PART.fullmatch(owner) or not _REPOSITORY_PART.fullmatch(repository):
        return None
    return f"{owner.lower()}/{repository.lower()}"


def _preflight(bind: sa.Connection) -> list[dict[str, Any]]:
    invalid_installations = bind.execute(
        sa.text(
            "SELECT id FROM github_app_installations "
            "WHERE installation_id IS NULL OR length(trim(installation_id)) = 0"
        )
    ).scalars().all()
    if invalid_installations:
        raise RuntimeError(
            "B07-D1b migration blocked: GitHub installations have empty installation_id "
            f"values on rows: {', '.join(str(value) for value in invalid_installations)}"
        )

    duplicates = bind.execute(
        sa.text(
            "SELECT installation_id, COUNT(*) AS row_count "
            "FROM github_app_installations "
            "GROUP BY installation_id HAVING COUNT(*) > 1"
        )
    ).mappings().all()
    if duplicates:
        details = ", ".join(
            f"{row['installation_id']} ({row['row_count']} rows)" for row in duplicates
        )
        raise RuntimeError(
            "B07-D1b migration blocked: duplicate GitHub installation_id values "
            f"require operator resolution: {details}"
        )

    rows = bind.execute(
        sa.text(
            "SELECT j.job_id, j.repo AS job_repo, w.id AS workspace_id, "
            "w.owner_scope, w.repo_identity, w.repo_url "
            "FROM import_jobs AS j "
            "LEFT JOIN workspaces AS w ON w.id = j.workspace_id "
            "ORDER BY j.id"
        )
    ).mappings().all()

    unresolved = [
        str(row["job_id"])
        for row in rows
        if row["workspace_id"] is None
        or row["owner_scope"] is None
        or not str(row["owner_scope"]).strip()
    ]
    if unresolved:
        raise RuntimeError(
            "B07-D1b migration blocked: legacy jobs have unresolved workspace/owner scope: "
            + ", ".join(unresolved)
        )
    return [dict(row) for row in rows]


def upgrade() -> None:
    bind = op.get_bind()
    legacy_rows = _preflight(bind)

    op.create_table(
        "import_history_quarantines",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("owner_scope", sa.String(length=120), nullable=False),
        sa.Column("scope_kind", sa.String(length=20), nullable=False),
        sa.Column("canonical_repo_key", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("reason_code", sa.String(length=80), nullable=False),
        sa.Column("created_by", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("cleared_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cleared_by", sa.String(length=255), nullable=True),
        sa.Column("clearance_rationale", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "(scope_kind = 'repository' AND canonical_repo_key IS NOT NULL "
            "AND length(canonical_repo_key) > 0) OR "
            "(scope_kind = 'owner_scope' AND canonical_repo_key IS NULL)",
            name="ck_import_history_quarantine_scope_key",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'cleared')",
            name="ck_import_history_quarantine_status",
        ),
        sa.CheckConstraint(
            "(status = 'active' AND cleared_at IS NULL AND cleared_by IS NULL "
            "AND clearance_rationale IS NULL) OR "
            "(status = 'cleared' AND cleared_at IS NOT NULL "
            "AND cleared_by IS NOT NULL AND length(trim(cleared_by)) > 0 "
            "AND clearance_rationale IS NOT NULL "
            "AND length(trim(clearance_rationale)) > 0)",
            name="ck_import_history_quarantine_clearance",
        ),
    )
    op.create_index(
        "uq_import_history_quarantine_active_repo",
        "import_history_quarantines",
        ["owner_scope", "canonical_repo_key"],
        unique=True,
        sqlite_where=sa.text("status = 'active' AND scope_kind = 'repository'"),
        postgresql_where=sa.text("status = 'active' AND scope_kind = 'repository'"),
    )
    op.create_index(
        "uq_import_history_quarantine_active_scope",
        "import_history_quarantines",
        ["owner_scope"],
        unique=True,
        sqlite_where=sa.text("status = 'active' AND scope_kind = 'owner_scope'"),
        postgresql_where=sa.text("status = 'active' AND scope_kind = 'owner_scope'"),
    )
    op.create_index(
        "ix_import_history_quarantine_lookup",
        "import_history_quarantines",
        ["owner_scope", "scope_kind", "canonical_repo_key", "status"],
    )

    # Backfill every pre-existing job conservatively. Conflicting identity
    # evidence within one workspace escalates to owner-scope quarantine.
    by_workspace: dict[int, dict[str, Any]] = {}
    for row in legacy_rows:
        workspace_id = int(row["workspace_id"])
        state = by_workspace.setdefault(
            workspace_id,
            {
                "owner_scope": str(row["owner_scope"]),
                "keys": set(),
                "ambiguous": False,
            },
        )
        if state["owner_scope"] != str(row["owner_scope"]):
            raise RuntimeError(
                f"B07-D1b migration blocked: workspace {workspace_id} has conflicting owner scopes"
            )

        values = [
            row["repo_identity"],
            row["repo_url"],
            row["job_repo"],
        ]
        parsed: set[str] = set()
        malformed = False
        for value in values:
            if value is None or not str(value).strip():
                continue
            canonical = _canonical_repository(str(value))
            if canonical is None:
                malformed = True
            else:
                parsed.add(canonical)
        if malformed or len(parsed) != 1:
            state["ambiguous"] = True
        else:
            state["keys"].update(parsed)

    inserts: set[tuple[str, str, str | None]] = set()
    for state in by_workspace.values():
        owner_scope = str(state["owner_scope"])
        keys = state["keys"]
        if state["ambiguous"] or len(keys) != 1:
            inserts.add((owner_scope, "owner_scope", None))
        else:
            inserts.add((owner_scope, "repository", next(iter(keys))))

    # A scope-wide quarantine subsumes repository quarantines in that scope.
    scope_wide = {owner for owner, kind, _ in inserts if kind == "owner_scope"}
    inserts = {
        item for item in inserts
        if item[1] == "owner_scope" or item[0] not in scope_wide
    }
    if inserts:
        bind.execute(
            sa.text(
                "INSERT INTO import_history_quarantines "
                "(owner_scope, scope_kind, canonical_repo_key, status, reason_code) "
                "VALUES (:owner_scope, :scope_kind, :canonical_repo_key, 'active', "
                "'legacy_history_unverified')"
            ),
            [
                {
                    "owner_scope": owner,
                    "scope_kind": kind,
                    "canonical_repo_key": repo,
                }
                for owner, kind, repo in sorted(inserts)
            ],
        )

    # Installation IDs are platform-global identities. The preflight above
    # prevents arbitrary selection/merging before this unique constraint.
    op.create_index(
        "uq_github_app_installations_installation_id",
        "github_app_installations",
        ["installation_id"],
        unique=True,
    )

    op.create_table(
        "github_webhook_deliveries",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("installation_id", sa.String(length=255), nullable=False),
        sa.Column("delivery_id", sa.String(length=255), nullable=False),
        sa.Column("owner_scope", sa.String(length=120), nullable=True),
        sa.Column("event_name", sa.String(length=100), nullable=False),
        sa.Column("payload_sha256", sa.String(length=64), nullable=False),
        sa.Column("disposition", sa.String(length=40), nullable=False),
        sa.Column(
            "job_id",
            sa.String(length=64),
            sa.ForeignKey("import_jobs.job_id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "length(payload_sha256) = 64",
            name="ck_github_webhook_delivery_payload_sha256_length",
        ),
        sa.UniqueConstraint(
            "installation_id", "delivery_id",
            name="uq_github_webhook_delivery_installation_delivery",
        ),
    )
    op.create_index(
        "ix_github_webhook_deliveries_owner_received",
        "github_webhook_deliveries",
        ["owner_scope", "received_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_github_webhook_deliveries_owner_received", table_name="github_webhook_deliveries")
    op.drop_table("github_webhook_deliveries")
    op.drop_index(
        "uq_github_app_installations_installation_id",
        table_name="github_app_installations",
    )
    op.drop_index(
        "ix_import_history_quarantine_lookup",
        table_name="import_history_quarantines",
    )
    op.drop_index(
        "uq_import_history_quarantine_active_scope",
        table_name="import_history_quarantines",
    )
    op.drop_index(
        "uq_import_history_quarantine_active_repo",
        table_name="import_history_quarantines",
    )
    op.drop_table("import_history_quarantines")
