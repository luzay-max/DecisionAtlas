from __future__ import annotations

from datetime import datetime

from sqlalchemy import (\n    CheckConstraint,\n    DateTime,\n    Float,\n    ForeignKey,\n    Index,\n    Integer,\n    JSON,\n    String,\n    Text,\n    UniqueConstraint,\n    func,\n    text,\n)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    repo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    owner_scope: Mapped[str] = mapped_column(String(120), nullable=False, default="local-default")
    repo_identity: Mapped[str | None] = mapped_column(String(255), nullable=True)
    access_source_type: Mapped[str] = mapped_column(String(50), nullable=False, default="public")
    access_source_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class Actor(Base):
    __tablename__ = "actors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    is_bootstrap: Mapped[bool] = mapped_column(default=False, nullable=False)
    disabled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class OwnerScope(Base):
    __tablename__ = "owner_scopes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scope_key: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    scope_type: Mapped[str] = mapped_column(String(50), nullable=False, default="local")
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class OwnerScopeMembership(Base):
    __tablename__ = "owner_scope_memberships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_id: Mapped[int] = mapped_column(ForeignKey("actors.id"), nullable=False)
    owner_scope_id: Mapped[int] = mapped_column(ForeignKey("owner_scopes.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="viewer")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class WorkspaceMembership(Base):
    __tablename__ = "workspace_memberships"
    __table_args__ = (
        UniqueConstraint("workspace_id", "actor_id", name="uq_workspace_memberships_workspace_actor"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), nullable=False)
    actor_id: Mapped[int] = mapped_column(ForeignKey("actors.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="viewer")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_token: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    actor_id: Mapped[int] = mapped_column(ForeignKey("actors.id"), nullable=False)
    current_owner_scope_id: Mapped[int] = mapped_column(ForeignKey("owner_scopes.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class GitHubAppInstallation(Base):
    __tablename__ = "github_app_installations"
    __table_args__ = (Index("uq_github_app_installations_installation_id", "installation_id", unique=True),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_scope: Mapped[str] = mapped_column(String(120), nullable=False)
    installation_id: Mapped[str] = mapped_column(String(255), nullable=False)
    account_login: Mapped[str | None] = mapped_column(String(255), nullable=True)
    account_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class GitHubTokenAccessSource(Base):
    __tablename__ = "github_token_access_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_scope: Mapped[str] = mapped_column(String(120), nullable=False)
    source_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    display_label: Mapped[str] = mapped_column(String(255), nullable=False)
    repo_identity: Mapped[str] = mapped_column(String(255), nullable=False)
    token_secret: Mapped[str] = mapped_column(Text, nullable=False)
    authorization_status: Mapped[str] = mapped_column(String(50), nullable=False, default="authorized")
    last_validated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class GovernanceDocument(Base):
    __tablename__ = "governance_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_scope: Mapped[str] = mapped_column(String(120), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    scope: Mapped[str] = mapped_column(String(80), nullable=False, default="all")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    source_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class GovernanceRuleDraft(Base):
    __tablename__ = "governance_rule_drafts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_scope: Mapped[str] = mapped_column(String(120), nullable=False)
    document_id: Mapped[int] = mapped_column(ForeignKey("governance_documents.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False, default="warning")
    scope: Mapped[str] = mapped_column(String(80), nullable=False, default="all")
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_excerpt: Mapped[str] = mapped_column(Text, nullable=False)
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False, default="standard")
    extraction_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    review_state: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    review_rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    lifecycle_status: Mapped[str] = mapped_column(String(50), nullable=False, default="current")
    superseded_by_rule_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    lifecycle_rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class Artifact(Base):
    __tablename__ = "artifacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    repo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    timestamp: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class ArtifactChunk(Base):
    __tablename__ = "artifact_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    artifact_id: Mapped[int] = mapped_column(ForeignKey("artifacts.id"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(JSON, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class Decision(Base):
    __tablename__ = "decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    review_state: Mapped[str] = mapped_column(String(50), default="candidate", nullable=False)
    problem: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[str | None] = mapped_column(Text, nullable=True)
    constraints: Mapped[str | None] = mapped_column(Text, nullable=True)
    chosen_option: Mapped[str] = mapped_column(Text, nullable=False)
    tradeoffs: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class SourceRef(Base):
    __tablename__ = "source_refs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    decision_id: Mapped[int] = mapped_column(ForeignKey("decisions.id"), nullable=False)
    artifact_id: Mapped[int] = mapped_column(ForeignKey("artifacts.id"), nullable=False)
    span_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    span_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    quote: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    relevance_score: Mapped[float | None] = mapped_column(Float, nullable=True)


class Relation(Base):
    __tablename__ = "relations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    from_type: Mapped[str] = mapped_column(String(50), nullable=False)
    from_id: Mapped[int] = mapped_column(Integer, nullable=False)
    to_type: Mapped[str] = mapped_column(String(50), nullable=False)
    to_id: Mapped[int] = mapped_column(Integer, nullable=False)
    relation_type: Mapped[str] = mapped_column(String(50), nullable=False)


class DriftAlert(Base):
    __tablename__ = "drift_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), nullable=False)
    artifact_id: Mapped[int | None] = mapped_column(ForeignKey("artifacts.id"), nullable=True)
    decision_id: Mapped[int | None] = mapped_column(ForeignKey("decisions.id"), nullable=True)
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="open", nullable=False)
    handled_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
    handled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    disposition_rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class ReviewAuditEvent(Base):
    __tablename__ = "review_audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_scope: Mapped[str] = mapped_column(String(120), nullable=False)
    workspace_id: Mapped[int | None] = mapped_column(ForeignKey("workspaces.id"), nullable=True)
    actor_id: Mapped[int | None] = mapped_column(ForeignKey("actors.id"), nullable=True)
    actor_username: Mapped[str] = mapped_column(String(120), nullable=False)
    actor_role: Mapped[str] = mapped_column(String(50), nullable=False)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_id: Mapped[int] = mapped_column(Integer, nullable=False)
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    previous_state_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_state_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class ImportJob(Base):
    __tablename__ = "import_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), nullable=False)
    repo: Mapped[str] = mapped_column(String(255), nullable=False)
    mode: Mapped[str] = mapped_column(String(50), nullable=False, default="full")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="queued")
    sync_origin: Mapped[str] = mapped_column(String(50), nullable=False, default="manual")
    trigger_event: Mapped[str | None] = mapped_column(String(100), nullable=True)
    trigger_delivery_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    imported_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    summary_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    # Legacy jobs are never implicitly eligible for the B07 worker.
    protocol_version: Mapped[str] = mapped_column(String(20), nullable=False, default="legacy", server_default="legacy")
    worker_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    lease_token: Mapped[str | None] = mapped_column(String(64), nullable=True)
    lease_generation: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    lease_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    available_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    checkpoint_version: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    checkpoint_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    pause_requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_failure_category: Mapped[str | None] = mapped_column(String(80), nullable=True)

class ImportHistoryQuarantine(Base):
    __tablename__ = "import_history_quarantines"
    __table_args__ = (
        CheckConstraint(
            "(scope_kind = 'repository' AND canonical_repo_key IS NOT NULL "
            "AND length(canonical_repo_key) > 0) OR "
            "(scope_kind = 'owner_scope' AND canonical_repo_key IS NULL)",
            name="ck_import_history_quarantine_scope_key",
        ),
        CheckConstraint(
            "status IN ('active', 'cleared')",
            name="ck_import_history_quarantine_status",
        ),
        CheckConstraint(
            "(status = 'active' AND cleared_at IS NULL AND cleared_by IS NULL "
            "AND clearance_rationale IS NULL) OR "
            "(status = 'cleared' AND cleared_at IS NOT NULL "
            "AND cleared_by IS NOT NULL AND length(trim(cleared_by)) > 0 "
            "AND clearance_rationale IS NOT NULL "
            "AND length(trim(clearance_rationale)) > 0)",
            name="ck_import_history_quarantine_clearance",
        ),
        Index(
            "uq_import_history_quarantine_active_repo",
            "owner_scope",
            "canonical_repo_key",
            unique=True,
            sqlite_where=text(
                "status = 'active' AND scope_kind = 'repository'"
            ),
            postgresql_where=text(
                "status = 'active' AND scope_kind = 'repository'"
            ),
        ),
        Index(
            "uq_import_history_quarantine_active_scope",
            "owner_scope",
            unique=True,
            sqlite_where=text(
                "status = 'active' AND scope_kind = 'owner_scope'"
            ),
            postgresql_where=text(
                "status = 'active' AND scope_kind = 'owner_scope'"
            ),
        ),
        Index(
            "ix_import_history_quarantine_lookup",
            "owner_scope",
            "scope_kind",
            "canonical_repo_key",
            "status",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_scope: Mapped[str] = mapped_column(String(120), nullable=False)
    scope_kind: Mapped[str] = mapped_column(String(20), nullable=False)
    canonical_repo_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active", server_default="active")
    reason_code: Mapped[str] = mapped_column(String(80), nullable=False)
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    cleared_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cleared_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    clearance_rationale: Mapped[str | None] = mapped_column(Text, nullable=True)


class GitHubWebhookDelivery(Base):
    __tablename__ = "github_webhook_deliveries"
    __table_args__ = (
        UniqueConstraint(
            "installation_id",
            "delivery_id",
            name="uq_github_webhook_delivery_installation_delivery",
        ),
        CheckConstraint(
            "length(payload_sha256) = 64",
            name="ck_github_webhook_delivery_payload_sha256_length",
        ),
        Index(
            "ix_github_webhook_deliveries_owner_received",
            "owner_scope",
            "received_at",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    installation_id: Mapped[str] = mapped_column(ForeignKey("github_app_installations.installation_id"), nullable=False)
    delivery_id: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_scope: Mapped[str | None] = mapped_column(String(120), nullable=True)
    event_name: Mapped[str] = mapped_column(String(100), nullable=False)
    payload_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    disposition: Mapped[str] = mapped_column(String(40), nullable=False)
    job_id: Mapped[str | None] = mapped_column(
        ForeignKey("import_jobs.job_id", ondelete="SET NULL"),
        nullable=True,
    )
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

