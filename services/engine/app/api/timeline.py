from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.db.session import get_db_session
from app.repositories.decisions import DecisionRepository
from app.repositories.workspaces import WorkspaceRepository

router = APIRouter(prefix="/timeline", tags=["timeline"])


@router.get("")
def get_timeline(workspace_slug: str = Query(...)) -> list[dict]:
    session = get_db_session()
    try:
        workspace = WorkspaceRepository(session).get_by_slug(workspace_slug)
        if workspace is None:
            raise HTTPException(status_code=404, detail=f"Workspace not found: {workspace_slug}")
        decisions = DecisionRepository(session).list_by_review_state(workspace.id, "accepted")
        return [
            {
                "id": decision.id,
                "title": decision.title,
                "review_state": decision.review_state,
                "status": decision.status,
                "problem": decision.problem,
                "chosen_option": decision.chosen_option,
                "tradeoffs": decision.tradeoffs,
                "created_at": decision.created_at.isoformat() if decision.created_at else None,
            }
            for decision in sorted(decisions, key=lambda item: (item.created_at or 0, item.id))
        ]
    finally:
        session.close()
