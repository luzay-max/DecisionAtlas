from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class DecisionContractModel(BaseModel):
    """Strict response DTOs for the existing Decisions API."""

    model_config = ConfigDict(extra="forbid")


class DecisionCoreResponse(DecisionContractModel):
    id: int
    workspace_id: int
    title: str
    status: str
    review_state: str
    problem: str
    context: str | None
    constraints: str | None
    chosen_option: str
    tradeoffs: str
    confidence: float


class DecisionSourceRefResponse(DecisionContractModel):
    id: int
    artifact_id: int
    span_start: int | None
    span_end: int | None
    quote: str
    url: str | None
    relevance_score: float | None
    current_quote_match: bool | None


class DecisionArtifactSummaryResponse(DecisionContractModel):
    id: int
    type: str
    title: str | None
    repo: str | None
    url: str | None


class DecisionQuoteIntegrityResponse(DecisionContractModel):
    status: Literal[
        "no_refs",
        "current_quote_missing",
        "unverifiable",
        "current_quotes_found",
    ]
    found_count: int
    missing_count: int
    unverifiable_count: int


class DecisionReviewEvidenceResponse(DecisionContractModel):
    state: Literal["grounded", "thin", "missing"]
    source_ref_count: int
    source_ref_preview: list[DecisionSourceRefResponse]
    primary_artifact: DecisionArtifactSummaryResponse | None
    current_quote_integrity: DecisionQuoteIntegrityResponse


class DecisionCandidateQualityResponse(DecisionContractModel):
    label: Literal["strong", "partial", "thin"]
    summary: str
    source_ref_count: int
    previewable_source_ref_count: int
    has_primary_artifact: bool
    has_source_url: bool
    confidence_bucket: Literal["high", "medium", "low"]
    reasons: list[str]


class DecisionAuditEventResponse(DecisionContractModel):
    id: int
    owner_scope: str
    workspace_id: int | None
    actor_id: int | None
    actor_username: str
    actor_role: str
    target_type: str
    target_id: int
    action: str
    previous_state: dict[str, Any] | None
    new_state: dict[str, Any] | None
    rationale: str | None
    metadata: dict[str, Any] | None
    created_at: datetime | None


class DecisionListItemResponse(DecisionCoreResponse):
    workspace_mode: Literal["demo", "imported", "mixed"]
    source_summary: str
    review_evidence: DecisionReviewEvidenceResponse
    candidate_quality: DecisionCandidateQualityResponse


class DecisionDetailResponse(DecisionListItemResponse):
    source_refs: list[DecisionSourceRefResponse]
    review_history: list[DecisionAuditEventResponse]


class DecisionReviewResponse(DecisionCoreResponse):
    audit_event: DecisionAuditEventResponse
    review_history: list[DecisionAuditEventResponse]
