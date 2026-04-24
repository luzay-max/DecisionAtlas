from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select

from app.auth import AuthContext, require_actor, require_scope_role, require_workspace_role
from app.db.session import get_db_session
from app.db.models import Workspace
from app.provenance import get_workspace_provenance
from app.repositories.artifacts import ArtifactRepository
from app.repositories.decisions import DecisionRepository
from app.repositories.source_refs import SourceRefRepository
from app.repositories.workspaces import WorkspaceRepository

router = APIRouter(prefix="/decisions", tags=["decisions"])


class ReviewDecisionRequest(BaseModel):
    review_state: str


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
    return payload


@router.get("")
def list_decisions(
    workspace_slug: str = Query(...),
    review_state: str | None = Query(default=None),
    auth: AuthContext = Depends(require_actor),
) -> list[dict]:
    session = get_db_session()
    try:
        required_role = "reviewer" if review_state in {None, "candidate"} else "viewer"
        workspace = require_workspace_role(session, auth, workspace_slug=workspace_slug, required_role=required_role)
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
        require_scope_role(auth, owner_scope=workspace.owner_scope, required_role="viewer", hide_not_found=True)
        provenance = get_workspace_provenance(session=session, workspace=workspace)
        return {
            **_serialize_decision(decision),
            "workspace_mode": provenance.workspace_mode,
            "source_summary": provenance.source_summary,
            "source_refs": [_serialize_source_ref(source_ref) for source_ref in source_refs.list_by_decision(decision.id)],
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
        require_scope_role(auth, owner_scope=workspace.owner_scope, required_role="reviewer", hide_not_found=True)
        decision = decisions.update_review_state(decision_id, request.review_state)
        session.commit()
        return _serialize_decision(decision)
    finally:
        session.close()
