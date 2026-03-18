from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.db.session import get_db_session
from app.drift.evaluator import DriftEvaluator
from app.repositories.artifacts import ArtifactRepository
from app.repositories.decisions import DecisionRepository
from app.repositories.drift_alerts import DriftAlertRepository
from app.repositories.workspaces import WorkspaceRepository

router = APIRouter(prefix="/drift", tags=["drift"])


@router.get("")
def list_drift_alerts(workspace_slug: str = Query(...)) -> list[dict]:
    session = get_db_session()
    try:
        workspace = WorkspaceRepository(session).get_by_slug(workspace_slug)
        if workspace is None:
            raise HTTPException(status_code=404, detail=f"Workspace not found: {workspace_slug}")

        alerts = DriftAlertRepository(session).list_by_workspace(workspace.id)
        artifacts = ArtifactRepository(session)
        decisions = DecisionRepository(session)

        return [
            {
                "id": alert.id,
                "alert_type": alert.alert_type,
                "summary": alert.summary,
                "status": alert.status,
                "confidence_label": _confidence_label(alert.alert_type),
                "created_at": alert.created_at.isoformat() if alert.created_at else None,
                "artifact": _serialize_artifact(artifacts.get_by_id(alert.artifact_id) if alert.artifact_id else None),
                "decision": _serialize_decision(decisions.get_by_id(alert.decision_id) if alert.decision_id else None),
            }
            for alert in alerts
        ]
    finally:
        session.close()


@router.post("/evaluate")
def evaluate_drift(payload: dict) -> dict:
    workspace_slug = payload.get("workspace_slug")
    if not workspace_slug:
        raise HTTPException(status_code=400, detail="workspace_slug is required")

    session = get_db_session()
    try:
        evaluator = DriftEvaluator(session)
        try:
            result = evaluator.evaluate_workspace(workspace_slug)
        except ValueError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        return {
            "status": "ok",
            "workspace_slug": result.workspace_slug,
            "evaluated_rules": result.evaluated_rules,
            "created_alerts": result.created_alerts,
        }
    finally:
        session.close()


def _serialize_artifact(artifact) -> dict | None:
    if artifact is None:
        return None
    return {
        "id": artifact.id,
        "type": artifact.type,
        "title": artifact.title,
        "url": artifact.url,
    }


def _serialize_decision(decision) -> dict | None:
    if decision is None:
        return None
    return {
        "id": decision.id,
        "title": decision.title,
        "review_state": decision.review_state,
        "chosen_option": decision.chosen_option,
    }


def _confidence_label(alert_type: str) -> str:
    if alert_type == "possible_supersession":
        return "medium"
    if alert_type == "needs_review":
        return "low"
    return "high"
