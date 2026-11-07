from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


ImportJobMode = Literal["full", "since_last_sync"]
ImportJobStatus = Literal["queued", "running", "paused", "succeeded", "failed"]


class ImportContractModel(BaseModel):
    """Strict DTOs for the existing Imports API; credentials are never response fields."""

    model_config = ConfigDict(extra="forbid")


class ImportJobResponse(ImportContractModel):
    job_id: str
    workspace_slug: str | None
    repo: str
    mode: ImportJobMode
    status: ImportJobStatus
    sync_origin: str | None = None
    trigger_event: str | None = None
    imported_count: int
    summary: dict[str, Any] | None = None
    error_message: str | None = None
    started_at: str | None = None
    finished_at: str | None = None


class ImportTargetResponse(ImportContractModel):
    owner_scope: str
    provider: str
    access_mode: str
    repo: str
    repo_url: str | None
    workspace_exists: bool
    workspace_slug: str | None
    has_successful_import: bool
    can_incremental_sync: bool
    has_running_import: bool
    latest_import: ImportJobResponse | None
    active_import: ImportJobResponse | None
    access_source_type: str
    access_source_label: str
    repo_private: bool | None = None
    latest_sync_origin: str | None = None
    latest_sync_at: str | None = None
    last_import_summary: dict[str, Any] | None = None
    access_source_status: str | None = None
    access_source_status_detail: str | None = None
    access_requirement: str | None = None
    access_requirement_detail: str | None = None
    setup_outcome: str | None = None
    next_action: str | None = None


class ImportPauseResumeCapabilityResponse(ImportContractModel):
    enabled: bool
    reason_code: Literal["worker_lifecycle_unverified"] | None


class ImportCapabilitiesResponse(ImportContractModel):
    pause_resume: ImportPauseResumeCapabilityResponse


class GitHubWebhookResponse(ImportContractModel):
    event: str
    delivery_id: str | None
    action: str | None
    repo: str | None
    installation_id: str | None
    status: Literal["ignored", "queued"]
    reason: str | None = None
    workspace_slug: str | None = None
    owner_scope: str | None = None
    job_id: str | None = None
    sync_origin: str | None = None
    trigger_event: str | None = None
