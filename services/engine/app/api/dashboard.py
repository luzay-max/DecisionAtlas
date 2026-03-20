from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.config import get_settings
from app.db.session import get_db_session
from app.provenance import get_workspace_provenance
from app.repositories.artifacts import ArtifactRepository
from app.repositories.decisions import DecisionRepository
from app.repositories.drift_alerts import DriftAlertRepository
from app.repositories.import_jobs import ImportJobRepository
from app.repositories.workspaces import WorkspaceRepository

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def get_dashboard_summary(workspace_slug: str = Query(...)) -> dict:
    session = get_db_session()
    try:
        settings = get_settings()
        workspace = WorkspaceRepository(session).get_by_slug(workspace_slug)
        if workspace is None:
            raise HTTPException(status_code=404, detail=f"Workspace not found: {workspace_slug}")
        artifacts = ArtifactRepository(session)
        decisions = DecisionRepository(session)
        alerts = DriftAlertRepository(session)
        jobs = ImportJobRepository(session)
        decision_counts = decisions.counts_by_review_state(workspace.id)
        workspace_artifacts = artifacts.list_by_workspace(workspace.id)
        provenance = get_workspace_provenance(session=session, workspace=workspace, artifacts=workspace_artifacts)
        recent_alerts = alerts.list_recent_by_workspace(workspace.id)
        latest_job = jobs.latest_for_workspace(workspace.id)
        return {
            "workspace_slug": workspace.slug,
            "repo_url": workspace.repo_url,
            "github_repo": _repo_ref(workspace.repo_url) or settings.demo_repo,
            "workspace_mode": provenance.workspace_mode,
            "source_summary": provenance.source_summary,
            "import_status": latest_job.status if latest_job is not None else "ready",
            "latest_import": (
                {
                    "job_id": latest_job.job_id,
                    "mode": latest_job.mode,
                    "status": latest_job.status,
                    "imported_count": latest_job.imported_count,
                    "summary": latest_job.summary_json,
                    "error_message": latest_job.error_message,
                    "started_at": latest_job.started_at.isoformat() if latest_job.started_at else None,
                    "finished_at": latest_job.finished_at.isoformat() if latest_job.finished_at else None,
                }
                if latest_job is not None
                else None
            ),
            "artifact_count": len(workspace_artifacts),
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


def _repo_ref(repo_url: str | None) -> str | None:
    if not repo_url or "github.com/" not in repo_url:
        return None
    normalized = repo_url.rstrip("/")
    if normalized.endswith(".git"):
        normalized = normalized[:-4]
    return normalized.split("github.com/", 1)[1]
