from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.db.session import get_db_session
from app.repositories.artifacts import ArtifactRepository
from app.repositories.decisions import DecisionRepository
from app.repositories.drift_alerts import DriftAlertRepository
from app.repositories.workspaces import WorkspaceRepository

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def get_dashboard_summary(workspace_slug: str = Query(...)) -> dict:
    session = get_db_session()
    try:
        workspace = WorkspaceRepository(session).get_by_slug(workspace_slug)
        if workspace is None:
            raise HTTPException(status_code=404, detail=f"Workspace not found: {workspace_slug}")
        artifacts = ArtifactRepository(session)
        decisions = DecisionRepository(session)
        alerts = DriftAlertRepository(session)
        decision_counts = decisions.counts_by_review_state(workspace.id)
        recent_alerts = alerts.list_recent_by_workspace(workspace.id)
        return {
            "workspace_slug": workspace.slug,
            "import_status": "ready",
            "artifact_count": artifacts.count_by_workspace(workspace.id),
            "decision_counts": {
                "candidate": decision_counts.get("candidate", 0),
                "accepted": decision_counts.get("accepted", 0),
                "rejected": decision_counts.get("rejected", 0),
                "superseded": decision_counts.get("superseded", 0),
            },
            "recent_alerts": [
                {
                    "id": alert.id,
                    "alert_type": alert.alert_type,
                    "summary": alert.summary,
                    "status": alert.status,
                }
                for alert in recent_alerts
            ],
        }
    finally:
        session.close()
