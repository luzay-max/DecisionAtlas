"""Wire models for the existing Why endpoint; OpenAPI is the TS source of truth."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

RetrievalMode = Literal["not_run", "hybrid", "lexical_only", "lexical_fallback"]
WhyAnswerStatus = Literal[
    "ok", "limited_support", "insufficient_evidence", "review_required",
    "evidence_limited", "analysis_failed",
]


class WireModel(BaseModel):
    # Fail on producer drift instead of silently dropping new evidence fields.
    model_config = ConfigDict(extra="forbid", strict=True)


class RecentSync(WireModel):
    job_id: str
    status: str
    mode: str
    sync_origin: str | None = None
    trigger_event: str | None = None
    started_at: str | None = None
    finished_at: str | None = None


class WorkspaceReadiness(WireModel):
    state: str
    next_action: str
    review_state: str
    why_state: str
    drift_state: str
    recommended_actions: list[str]
    accepted_baseline_established: bool = False
    accepted_decision_count: int = 0
    candidate_decision_count: int = 0
    access_source_type: str = "public"
    access_source_label: str = ""
    access_source_status: str | None = None
    access_source_status_detail: str | None = None
    latest_sync_origin: str | None = None
    latest_sync_at: str | None = None
    active_sync_origin: str | None = None
    active_import_job_id: str | None = None
    active_import_status: str | None = None
    active_import_mode: str | None = None
    recent_syncs: list[RecentSync] = Field(default_factory=list)


class WhyRetrievalDiagnostics(WireModel):
    support_reasons: list[str]
    decision_overlap: int = 0
    source_ref_overlap: int = 0
    structural_fit: float = 0
    raw_score: float = 0


class WhyAnswerContext(WireModel):
    workspace_mode: Literal["demo", "imported", "mixed"]
    source_summary: str
    workspace_readiness: WorkspaceReadiness | None = None
    retrieval_mode: RetrievalMode = "not_run"
    retrieval: WhyRetrievalDiagnostics | None = None


class WhyPrimaryDecision(WireModel):
    decision_id: int
    title: str


class WhySupportingContext(WhyPrimaryDecision):
    answer: str


class WhyCitation(WireModel):
    decision_id: int | None = None
    source_ref_id: int | None = None
    quote: str
    url: str | None


class WhyAnswerResponse(WireModel):
    status: WhyAnswerStatus
    question: str
    answer: str
    retrieval_mode: RetrievalMode = "not_run"
    primary_decision: WhyPrimaryDecision | None = None
    supporting_context: list[WhySupportingContext] = Field(default_factory=list)
    answer_context: WhyAnswerContext
    citations: list[WhyCitation]


class WhyHTTPError(WireModel):
    """Existing HTTPException envelope; validation errors retain FastAPI's 422 model."""
    detail: str
