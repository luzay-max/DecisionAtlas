from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth import AuthContext, require_actor, require_workspace_role
from app.config import get_settings
from app.db.session import get_db_session
from app.outcomes.real_workspaces import build_imported_drift_status, build_imported_workspace_readiness
from app.provenance import get_workspace_provenance
from app.repository_access import access_source_summary
from app.repositories.artifacts import ArtifactRepository
from app.repositories.decisions import DecisionRepository
from app.repositories.drift_alerts import DriftAlertRepository
from app.repositories.import_jobs import ImportJobRepository
from app.repositories.workspaces import WorkspaceRepository

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def get_dashboard_summary(
    workspace_slug: str = Query(...),
    auth: AuthContext = Depends(require_actor),
) -> dict:
    session = get_db_session()
    try:
        settings = get_settings()
        workspace = require_workspace_role(session, auth, workspace_slug=workspace_slug, required_role="viewer")
        artifacts = ArtifactRepository(session)
        decisions = DecisionRepository(session)
        alerts = DriftAlertRepository(session)
        jobs = ImportJobRepository(session)
        decision_counts = decisions.counts_by_review_state(workspace.id)
        workspace_artifacts = artifacts.list_by_workspace(workspace.id)
        provenance = get_workspace_provenance(session=session, workspace=workspace, artifacts=workspace_artifacts)
        recent_alerts = alerts.list_recent_by_workspace(workspace.id)
        latest_job = jobs.latest_for_workspace(workspace.id)
        recent_sync_jobs = jobs.list_recent_for_workspace(workspace.id, limit=5)
        source_summary = access_source_summary(
            session=session,
            owner_scope=workspace.owner_scope,
            access_source_type=workspace.access_source_type,
            access_source_ref=workspace.access_source_ref,
        )
        drift_status = build_imported_drift_status(
            candidate_count=decision_counts.get("candidate", 0),
            accepted_count=decision_counts.get("accepted", 0),
            latest_import_finished_at=latest_job.finished_at if latest_job is not None else None,
            latest_accepted_change_at=max(
                (decision.updated_at for decision in decisions.list_by_review_state(workspace.id, "accepted")),
                default=None,
            ),
            latest_import_summary=latest_job.summary_json if latest_job is not None else None,
            alert_count=len(recent_alerts),
        )
        workspace_readiness = (
            build_imported_workspace_readiness(
                latest_import_status=latest_job.status if latest_job is not None else None,
                latest_import_summary=latest_job.summary_json if latest_job is not None else None,
                latest_import=latest_job,
                recent_sync_jobs=recent_sync_jobs,
                decision_counts=decision_counts,
                drift_status=drift_status,
                access_source_type=workspace.access_source_type,
                access_source_ref=workspace.access_source_ref,
                access_source_label=str(source_summary["access_source_label"]) if source_summary["access_source_label"] else None,
                access_source_status=str(source_summary["access_source_status"]) if source_summary["access_source_status"] else None,
                access_source_status_detail=(
                    str(source_summary["access_source_status_detail"])
                    if source_summary["access_source_status_detail"]
                    else None
                ),
            )
            if provenance.workspace_mode != "demo"
            else None
        )
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
                    "sync_origin": latest_job.sync_origin,
                    "trigger_event": latest_job.trigger_event,
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
            "workspace_readiness": workspace_readiness,
            "drift_status": drift_status if provenance.workspace_mode != "demo" else None,
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
