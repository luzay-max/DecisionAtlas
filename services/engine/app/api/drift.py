from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.auth import AuthContext, require_actor, require_workspace_role
from app.db.session import get_db_session
from app.drift.evaluator import DriftEvaluator
from app.llm.base import ProviderConfigurationError, ProviderError
from app.llm.provider_factory import build_runtime_providers
from app.outcomes.real_workspaces import build_imported_drift_status
from app.provenance import get_workspace_provenance
from app.repositories.artifacts import ArtifactRepository
from app.repositories.decisions import DecisionRepository
from app.repositories.drift_alerts import DriftAlertRepository
from app.repositories.import_jobs import ImportJobRepository
from app.repositories.review_audit import bounded_rationale, ReviewAuditRepository, serialize_review_audit_event
from app.repositories.workspaces import WorkspaceRepository

router = APIRouter(prefix="/drift", tags=["drift"])

DRIFT_DISPOSITION_STATUSES = {"open", "acknowledged", "resolved", "false_positive"}


class DriftDispositionRequest(BaseModel):
    status: str
    rationale: str | None = None


@router.get("")
def list_drift_alerts(
    workspace_slug: str = Query(...),
    auth: AuthContext = Depends(require_actor),
) -> dict:
    session = get_db_session()
    try:
        workspace = require_workspace_role(session, auth, workspace_slug=workspace_slug, required_role="viewer")

        alerts = DriftAlertRepository(session).list_by_workspace(workspace.id)
        artifacts = ArtifactRepository(session)
        workspace_artifacts = artifacts.list_by_workspace(workspace.id)
        provenance = get_workspace_provenance(session=session, workspace=workspace, artifacts=workspace_artifacts)
        decisions = DecisionRepository(session)
        accepted_decisions = decisions.list_by_review_state(workspace.id, "accepted")
        latest_job = ImportJobRepository(session).latest_for_workspace(workspace.id)
        drift_status = build_imported_drift_status(
            candidate_count=decisions.counts_by_review_state(workspace.id).get("candidate", 0),
            accepted_count=len(accepted_decisions),
            latest_import_finished_at=latest_job.finished_at if latest_job is not None else None,
            latest_accepted_change_at=max((decision.updated_at for decision in accepted_decisions), default=None),
            latest_import_summary=latest_job.summary_json if latest_job is not None else None,
            alert_count=len(alerts),
        )

        return {
            "workspace_mode": provenance.workspace_mode,
            "source_summary": provenance.source_summary,
            "evaluation": drift_status if provenance.workspace_mode != "demo" else None,
            "alerts": [
                _serialize_alert(
                    session=session,
                    alert=alert,
                    owner_scope=workspace.owner_scope,
                    artifacts=artifacts,
                    decisions=decisions,
                )
                for alert in alerts
            ],
        }
    finally:
        session.close()


@router.post("/evaluate")
def evaluate_drift(
    payload: dict,
    auth: AuthContext = Depends(require_actor),
) -> dict:
    workspace_slug = payload.get("workspace_slug")
    if not workspace_slug:
        raise HTTPException(status_code=400, detail="workspace_slug is required")

    session = get_db_session()
    try:
        require_workspace_role(session, auth, workspace_slug=workspace_slug, required_role="reviewer")
        try:
            runtime = build_runtime_providers()
            evaluator = DriftEvaluator(session, embedder=runtime.embedder)
            result = evaluator.evaluate_workspace(workspace_slug)
        except ValueError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        except ProviderConfigurationError as error:
            raise HTTPException(status_code=503, detail=str(error)) from error
        except ProviderError as error:
            raise HTTPException(status_code=502, detail=str(error)) from error
        workspace = WorkspaceRepository(session).get_by_slug(workspace_slug)
        if workspace is None:
            raise HTTPException(status_code=404, detail=f"Workspace not found: {workspace_slug}")
        jobs = ImportJobRepository(session)
        latest_job = jobs.latest_for_workspace(workspace.id)
        if latest_job is not None:
            jobs.merge_summary(
                latest_job.job_id,
                summary_json={
                    "drift_evaluation": {
                        "evaluated_at": datetime.now(UTC).isoformat(),
                        "evaluated_rules": result.evaluated_rules,
                        "created_alerts": result.created_alerts,
                    }
                },
            )
            session.commit()
            latest_job = jobs.latest_for_workspace(workspace.id)
        alerts = DriftAlertRepository(session).list_by_workspace(workspace.id)
        accepted_decisions = DecisionRepository(session).list_by_review_state(workspace.id, "accepted")
        drift_status = build_imported_drift_status(
            candidate_count=DecisionRepository(session).counts_by_review_state(workspace.id).get("candidate", 0),
            accepted_count=len(accepted_decisions),
            latest_import_finished_at=latest_job.finished_at if latest_job is not None else None,
            latest_accepted_change_at=max((decision.updated_at for decision in accepted_decisions), default=None),
            latest_import_summary=latest_job.summary_json if latest_job is not None else None,
            alert_count=len(alerts),
        )
        return {
            "status": "ok",
            "workspace_slug": result.workspace_slug,
            "evaluated_rules": result.evaluated_rules,
            "created_alerts": result.created_alerts,
            "evaluation": drift_status,
        }
    finally:
        session.close()


@router.post("/alerts/{alert_id}/disposition")
def update_drift_alert_disposition(
    alert_id: int,
    request: DriftDispositionRequest,
    auth: AuthContext = Depends(require_actor),
) -> dict:
    if request.status not in DRIFT_DISPOSITION_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid drift alert disposition status")

    session = get_db_session()
    try:
        alerts = DriftAlertRepository(session)
        alert = alerts.get_by_id(alert_id)
        if alert is None:
            raise HTTPException(status_code=404, detail=f"Drift alert not found: {alert_id}")
        workspace = WorkspaceRepository(session).get_by_id(alert.workspace_id)
        if workspace is None:
            raise HTTPException(status_code=404, detail=f"Workspace not found for drift alert: {alert_id}")
        require_workspace_role(session, auth, workspace_slug=workspace.slug, required_role="reviewer", hide_not_found=True)

        previous_state = {"status": alert.status}
        updated = alerts.update_disposition(
            alert,
            status=request.status,
            handled_by=auth.username,
            handled_at=datetime.now(UTC),
            disposition_rationale=bounded_rationale(request.rationale),
        )
        event = ReviewAuditRepository(session).create_event(
            owner_scope=workspace.owner_scope,
            workspace_id=workspace.id,
            actor_id=auth.actor_id,
            actor_username=auth.username,
            actor_role=auth.role,
            target_type="drift_alert",
            target_id=updated.id,
            action=f"drift_alert_disposition_{request.status}",
            previous_state=previous_state,
            new_state={"status": updated.status},
            rationale=request.rationale,
        )
        artifacts = ArtifactRepository(session)
        decisions = DecisionRepository(session)
        session.commit()
        return {
            "alert": _serialize_alert(
                session=session,
                alert=updated,
                owner_scope=workspace.owner_scope,
                artifacts=artifacts,
                decisions=decisions,
            ),
            "audit_event": serialize_review_audit_event(event),
        }
    finally:
        session.close()


def _serialize_alert(*, session, alert, owner_scope: str, artifacts: ArtifactRepository, decisions: DecisionRepository) -> dict:
    return {
        "id": alert.id,
        "alert_type": alert.alert_type,
        "summary": alert.summary,
        "status": alert.status,
        "confidence_label": _confidence_label(alert.alert_type),
        "created_at": alert.created_at.isoformat() if alert.created_at else None,
        "handled_by": alert.handled_by,
        "handled_at": alert.handled_at.isoformat() if alert.handled_at else None,
        "disposition_rationale": alert.disposition_rationale,
        "artifact": _serialize_artifact(artifacts.get_by_id(alert.artifact_id) if alert.artifact_id else None),
        "decision": _serialize_decision(decisions.get_by_id(alert.decision_id) if alert.decision_id else None),
        "audit_history": [
            serialize_review_audit_event(event)
            for event in ReviewAuditRepository(session).list_for_target(
                owner_scope=owner_scope,
                target_type="drift_alert",
                target_id=alert.id,
            )
        ],
    }


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
