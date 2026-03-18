from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.db.session import get_db_session
from app.repositories.decisions import DecisionRepository
from app.repositories.source_refs import SourceRefRepository
from app.repositories.workspaces import WorkspaceRepository

router = APIRouter(prefix="/decisions", tags=["decisions"])


class ReviewDecisionRequest(BaseModel):
    review_state: str


def _serialize_decision(decision) -> dict:
    return {
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


@router.get("")
def list_decisions(
    workspace_slug: str = Query(...),
    review_state: str | None = Query(default=None),
) -> list[dict]:
    session = get_db_session()
    try:
        workspace = WorkspaceRepository(session).get_by_slug(workspace_slug)
        if workspace is None:
            raise HTTPException(status_code=404, detail=f"Workspace not found: {workspace_slug}")
        decisions = DecisionRepository(session).list_by_review_state(workspace.id, review_state)
        return [_serialize_decision(decision) for decision in decisions]
    finally:
        session.close()


@router.get("/{decision_id}")
def get_decision(decision_id: int) -> dict:
    session = get_db_session()
    try:
        decisions = DecisionRepository(session)
        source_refs = SourceRefRepository(session)
        decision = decisions.get_by_id(decision_id)
        if decision is None:
            raise HTTPException(status_code=404, detail=f"Decision not found: {decision_id}")
        return {
            **_serialize_decision(decision),
            "source_refs": [
                {
                    "id": source_ref.id,
                    "artifact_id": source_ref.artifact_id,
                    "span_start": source_ref.span_start,
                    "span_end": source_ref.span_end,
                    "quote": source_ref.quote,
                    "url": source_ref.url,
                    "relevance_score": source_ref.relevance_score,
                }
                for source_ref in source_refs.list_by_decision(decision.id)
            ],
        }
    finally:
        session.close()


@router.post("/{decision_id}/review")
def review_decision(decision_id: int, request: ReviewDecisionRequest) -> dict:
    valid_states = {"accepted", "rejected", "superseded", "candidate"}
    if request.review_state not in valid_states:
        raise HTTPException(status_code=400, detail="Invalid review_state")

    session = get_db_session()
    try:
        decisions = DecisionRepository(session)
        decision = decisions.update_review_state(decision_id, request.review_state)
        if decision is None:
            raise HTTPException(status_code=404, detail=f"Decision not found: {decision_id}")
        session.commit()
        return _serialize_decision(decision)
    finally:
        session.close()
