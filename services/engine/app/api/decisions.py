from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select

from app.auth import AuthContext, require_actor, require_workspace_role
from app.db.session import get_db_session
from app.db.models import Workspace
from app.provenance import get_workspace_provenance
from app.repositories.artifacts import ArtifactRepository
from app.repositories.decisions import DecisionRepository
from app.repositories.review_audit import ReviewAuditRepository, serialize_review_audit_event
from app.repositories.source_refs import SourceRefRepository
from app.repositories.workspaces import WorkspaceRepository

router = APIRouter(prefix="/decisions", tags=["decisions"])


class ReviewDecisionRequest(BaseModel):
    review_state: str
    review_rationale: str | None = None


def _serialize_source_ref(source_ref) -> dict:
    return {
        "id": source_ref.id,
        "artifact_id": source_ref.artifact_id,
        "span_start": source_ref.span_start,
        "span_end": source_ref.span_end,
        "quote": source_ref.quote,
        "url": source_ref.url,
        "relevance_score": source_ref.relevance_score,
    }


def _serialize_artifact_summary(artifact) -> dict | None:
    if artifact is None:
        return None
    return {
        "id": artifact.id,
        "type": artifact.type,
        "title": artifact.title,
        "repo": artifact.repo,
        "url": artifact.url,
    }


def _review_evidence_state(source_ref_count: int) -> str:
    if source_ref_count >= 2:
        return "grounded"
    if source_ref_count == 1:
        return "thin"
    return "missing"


def _confidence_bucket(confidence: float) -> str:
    if confidence >= 0.8:
        return "high"
    if confidence >= 0.6:
        return "medium"
    return "low"


def _candidate_quality(
    *,
    decision,
    source_refs: list,
    primary_artifact,
) -> dict:
    source_ref_count = len(source_refs)
    previewable_source_ref_count = len([source_ref for source_ref in source_refs if str(source_ref.quote or "").strip()])
    has_primary_artifact = primary_artifact is not None
    has_source_url = any(source_ref.url for source_ref in source_refs) or bool(getattr(primary_artifact, "url", None))
    confidence_bucket = _confidence_bucket(float(decision.confidence or 0.0))

    reasons: list[str] = []
    if source_ref_count >= 2:
        reasons.append("multiple_source_refs")
    elif source_ref_count == 1:
        reasons.append("single_source_ref")
    else:
        reasons.append("missing_source_refs")
    if previewable_source_ref_count > 0:
        reasons.append("previewable_quote")
    else:
        reasons.append("missing_previewable_quote")
    reasons.append("artifact_provenance" if has_primary_artifact else "missing_artifact_provenance")
    reasons.append("source_url_available" if has_source_url else "missing_source_url")
    reasons.append(f"{confidence_bucket}_confidence")

    if (
        source_ref_count >= 2
        and previewable_source_ref_count >= 1
        and has_primary_artifact
        and has_source_url
        and confidence_bucket != "low"
    ):
        label = "strong"
        summary = "Multiple grounded refs with previewable evidence, provenance, and source URL support."
    elif source_ref_count >= 1 and (previewable_source_ref_count >= 1 or has_primary_artifact or has_source_url):
        label = "partial"
        summary = "Some grounding is available, but missing support keeps this below a strong baseline candidate."
    else:
        label = "thin"
        summary = "Thin grounding or missing provenance; keep as diagnosable review input, not a strong baseline."

    return {
        "label": label,
        "summary": summary,
        "source_ref_count": source_ref_count,
        "previewable_source_ref_count": previewable_source_ref_count,
        "has_primary_artifact": has_primary_artifact,
        "has_source_url": has_source_url,
        "confidence_bucket": confidence_bucket,
        "reasons": reasons,
    }


def _serialize_decision(
    decision,
    *,
    source_refs: list | None = None,
    artifacts: ArtifactRepository | None = None,
    workspace_mode: str | None = None,
    source_summary: str | None = None,
) -> dict:
    payload = {
        "id": decision.id,
        "workspace_id": decision.workspace_id,
        "title": decision.title,
        "status": decision.status,
        "review_state": decision.review_state,
        "problem": decision.problem,
        "context": decision.context,
        "constraints": decision.constraints,
        "chosen_option": decision.chosen_option,
        "tradeoffs": decision.tradeoffs,
        "confidence": decision.confidence,
    }
    if workspace_mode is not None:
        payload["workspace_mode"] = workspace_mode
    if source_summary is not None:
        payload["source_summary"] = source_summary
    if source_refs is not None:
        source_ref_count = len(source_refs)
        primary_artifact = artifacts.get_by_id(source_refs[0].artifact_id) if artifacts is not None and source_refs else None
        payload["review_evidence"] = {
            "state": _review_evidence_state(source_ref_count),
            "source_ref_count": source_ref_count,
            "source_ref_preview": [_serialize_source_ref(source_ref) for source_ref in source_refs[:2]],
            "primary_artifact": _serialize_artifact_summary(primary_artifact),
        }
        payload["candidate_quality"] = _candidate_quality(
            decision=decision,
            source_refs=source_refs,
            primary_artifact=primary_artifact,
        )
    return payload


def _decision_state(decision) -> dict:
    return {
        "review_state": decision.review_state,
        "status": decision.status,
    }


@router.get("")
def list_decisions(
    workspace_slug: str = Query(...),
    review_state: str | None = Query(default=None),
    auth: AuthContext = Depends(require_actor),
) -> list[dict]:
    session = get_db_session()
    try:
        workspace = require_workspace_role(session, auth, workspace_slug=workspace_slug, required_role="viewer")
        decisions = DecisionRepository(session).list_by_review_state(workspace.id, review_state)
        source_refs = SourceRefRepository(session)
        artifacts = ArtifactRepository(session)
        provenance = get_workspace_provenance(session=session, workspace=workspace)
        return [
            _serialize_decision(
                decision,
                source_refs=source_refs.list_by_decision(decision.id),
                artifacts=artifacts,
                workspace_mode=provenance.workspace_mode,
                source_summary=provenance.source_summary,
            )
            for decision in decisions
        ]
    finally:
        session.close()


@router.get("/{decision_id}")
def get_decision(
    decision_id: int,
    auth: AuthContext = Depends(require_actor),
) -> dict:
    session = get_db_session()
    try:
        decisions = DecisionRepository(session)
        source_refs = SourceRefRepository(session)
        decision = decisions.get_by_id(decision_id)
        if decision is None:
            raise HTTPException(status_code=404, detail=f"Decision not found: {decision_id}")
        workspace = session.scalar(select(Workspace).where(Workspace.id == decision.workspace_id))
        if workspace is None:
            raise HTTPException(status_code=404, detail=f"Workspace not found for decision: {decision_id}")
        require_workspace_role(session, auth, workspace_slug=workspace.slug, required_role="viewer", hide_not_found=True)
        provenance = get_workspace_provenance(session=session, workspace=workspace)
        artifacts = ArtifactRepository(session)
        decision_source_refs = source_refs.list_by_decision(decision.id)
        return {
            **_serialize_decision(decision, source_refs=decision_source_refs, artifacts=artifacts),
            "workspace_mode": provenance.workspace_mode,
            "source_summary": provenance.source_summary,
            "source_refs": [_serialize_source_ref(source_ref) for source_ref in decision_source_refs],
            "review_history": [
                serialize_review_audit_event(event)
                for event in ReviewAuditRepository(session).list_for_target(
                    owner_scope=workspace.owner_scope,
                    target_type="decision",
                    target_id=decision.id,
                )
            ],
        }
    finally:
        session.close()


@router.post("/{decision_id}/review")
def review_decision(
    decision_id: int,
    request: ReviewDecisionRequest,
    auth: AuthContext = Depends(require_actor),
) -> dict:
    valid_states = {"accepted", "rejected", "superseded", "candidate"}
    if request.review_state not in valid_states:
        raise HTTPException(status_code=400, detail="Invalid review_state")

    session = get_db_session()
    try:
        decisions = DecisionRepository(session)
        existing = decisions.get_by_id(decision_id)
        if existing is None:
            raise HTTPException(status_code=404, detail=f"Decision not found: {decision_id}")
        workspace = session.scalar(select(Workspace).where(Workspace.id == existing.workspace_id))
        if workspace is None:
            raise HTTPException(status_code=404, detail=f"Workspace not found for decision: {decision_id}")
        require_workspace_role(session, auth, workspace_slug=workspace.slug, required_role="reviewer", hide_not_found=True)
        previous_state = _decision_state(existing)
        decision = decisions.update_review_state(decision_id, request.review_state)
        event = ReviewAuditRepository(session).create_event(
            owner_scope=workspace.owner_scope,
            workspace_id=workspace.id,
            actor_id=auth.actor_id,
            actor_username=auth.username,
            actor_role=auth.role,
            target_type="decision",
            target_id=decision.id,
            action=f"decision_review_{request.review_state}",
            previous_state=previous_state,
            new_state=_decision_state(decision),
            rationale=request.review_rationale,
        )
        session.commit()
        return {
            **_serialize_decision(decision),
            "audit_event": serialize_review_audit_event(event),
            "review_history": [
                serialize_review_audit_event(history_event)
                for history_event in ReviewAuditRepository(session).list_for_target(
                    owner_scope=workspace.owner_scope,
                    target_type="decision",
                    target_id=decision.id,
                )
            ],
        }
    finally:
        session.close()
