from __future__ import annotations

from collections import Counter
from datetime import datetime


def build_imported_drift_status(
    *,
    candidate_count: int,
    accepted_count: int,
    latest_import_finished_at: datetime | None,
    latest_accepted_change_at: datetime | None,
    latest_import_summary: dict | None,
    alert_count: int,
) -> dict:
    summary = dict(latest_import_summary or {})
    drift_evaluation = dict(summary.get("drift_evaluation") or {})
    evaluated_at = _parse_iso_datetime(drift_evaluation.get("evaluated_at"))
    latest_change_at = _latest_datetime(latest_import_finished_at, latest_accepted_change_at)

    if accepted_count <= 0 and candidate_count > 0:
        state = "review_required"
        can_evaluate = False
        next_action = "review_candidates"
    elif accepted_count <= 0:
        state = "evidence_limited"
        can_evaluate = False
        next_action = "inspect_import_summary"
    elif evaluated_at is None:
        state = "unevaluated"
        can_evaluate = True
        next_action = "evaluate_drift"
    elif latest_change_at is not None and evaluated_at < latest_change_at:
        state = "stale"
        can_evaluate = True
        next_action = "evaluate_drift"
    elif alert_count > 0:
        state = "alerts_present"
        can_evaluate = True
        next_action = "inspect_alerts"
    else:
        state = "clean"
        can_evaluate = True
        next_action = "evaluate_drift"

    return {
        "state": state,
        "can_evaluate": can_evaluate,
        "next_action": next_action,
        "last_evaluated_at": drift_evaluation.get("evaluated_at"),
        "evaluated_rules": drift_evaluation.get("evaluated_rules"),
        "created_alerts": drift_evaluation.get("created_alerts"),
    }


def build_imported_workspace_readiness(
    *,
    latest_import_status: str | None,
    latest_import_summary: dict | None,
    latest_import,
    recent_sync_jobs: list,
    decision_counts: dict[str, int],
    drift_status: dict,
    access_source_type: str = "public",
    access_source_ref: str | None = None,
    access_source_label: str | None = None,
    access_source_status: str | None = None,
    access_source_status_detail: str | None = None,
) -> dict:
    candidate_count = decision_counts.get("candidate", 0)
    accepted_count = decision_counts.get("accepted", 0)
    summary = dict(latest_import_summary or {})
    outcome = summary.get("outcome")
    conversion_limited = _is_conversion_limited(summary, candidate_count=candidate_count, accepted_count=accepted_count)

    if latest_import_status == "failed":
        state = "analysis_failed"
        next_action = "retry_import"
        why_state = "analysis_failed"
        review_state = "review_unavailable"
    elif candidate_count > 0:
        state = "review_ready"
        next_action = "review_candidates"
        why_state = "review_required"
        review_state = "review_ready"
    elif accepted_count > 0:
        state = "why_ready"
        next_action = "ask_why"
        why_state = "ready"
        review_state = "review_complete"
    elif conversion_limited:
        state = "conversion_limited"
        next_action = "inspect_import_summary"
        why_state = "evidence_limited"
        review_state = "review_unavailable"
    elif outcome == "insufficient_evidence":
        state = "evidence_limited"
        next_action = "inspect_import_summary"
        why_state = "evidence_limited"
        review_state = "review_unavailable"
    else:
        state = "import_complete"
        next_action = "inspect_import_summary"
        why_state = "review_required"
        review_state = "review_unavailable"

    recommended_actions = _recommended_actions(
        next_action=next_action,
        why_state=why_state,
        drift_state=drift_status["state"],
        review_state=review_state,
    )

    return {
        "state": state,
        "next_action": next_action,
        "review_state": review_state,
        "why_state": why_state,
        "drift_state": drift_status["state"],
        "recommended_actions": recommended_actions,
        "access_source_type": access_source_type,
        "access_source_label": access_source_label or _access_source_label(access_source_type, access_source_ref),
        "access_source_status": access_source_status,
        "access_source_status_detail": access_source_status_detail,
        "latest_sync_origin": _sync_origin(latest_import),
        "latest_sync_at": _sync_timestamp(latest_import),
        "active_sync_origin": _active_sync_origin(latest_import),
        "recent_syncs": _recent_syncs(recent_sync_jobs),
    }


def _is_conversion_limited(summary: dict, *, candidate_count: int, accepted_count: int) -> bool:
    if candidate_count > 0 or accepted_count > 0:
        return False
    extraction_summary = dict(summary.get("extraction_summary") or {})
    screened_in = int(extraction_summary.get("screened_in_artifacts") or 0)
    full_requests = int(extraction_summary.get("full_extraction_requests") or 0)
    completed_extractions = int(extraction_summary.get("completed_full_extractions") or 0)
    created_candidates = int(extraction_summary.get("created_candidates") or 0)
    conversion_losses = sum(int(count) for count in dict(extraction_summary.get("conversion_loss_reasons") or {}).values())
    significant_attempts = max(screened_in, full_requests) >= 5
    attempts_exhausted = full_requests > 0 and completed_extractions >= full_requests
    return created_candidates == 0 and significant_attempts and attempts_exhausted and conversion_losses >= 3


def _recommended_actions(
    *,
    next_action: str,
    why_state: str,
    drift_state: str,
    review_state: str,
) -> list[str]:
    actions: list[str] = [next_action]
    if review_state == "review_ready":
        actions.append("inspect_import_summary")
    if why_state == "ready" and next_action != "ask_why":
        actions.append("ask_why")
    if drift_state in {"unevaluated", "stale", "clean"}:
        actions.append("evaluate_drift")
    elif drift_state == "alerts_present":
        actions.append("inspect_alerts")
    elif drift_state == "review_required" and review_state != "review_ready":
        actions.append("review_candidates")
    if next_action != "inspect_import_summary":
        actions.append("inspect_import_summary")

    deduped: list[str] = []
    for action in actions:
        if action not in deduped:
            deduped.append(action)
    return deduped


def _access_source_label(access_source_type: str, access_source_ref: str | None) -> str:
    if access_source_type == "github_app_installation":
        suffix = f" #{access_source_ref}" if access_source_ref else ""
        return f"GitHub App installation{suffix}"
    if access_source_type == "github_token":
        suffix = f" {access_source_ref}" if access_source_ref else ""
        return f"Private GitHub source{suffix}"
    return "Public GitHub access"


def _sync_origin(latest_import) -> str | None:
    if latest_import is None or not getattr(latest_import, "sync_origin", None):
        return None
    return str(latest_import.sync_origin)


def _active_sync_origin(latest_import) -> str | None:
    if latest_import is None or getattr(latest_import, "status", None) not in {"queued", "running"}:
        return None
    return _sync_origin(latest_import)


def _sync_timestamp(latest_import) -> str | None:
    if latest_import is None:
        return None
    finished_at = getattr(latest_import, "finished_at", None)
    started_at = getattr(latest_import, "started_at", None)
    created_at = getattr(latest_import, "created_at", None)
    timestamp = finished_at or started_at or created_at
    return timestamp.isoformat() if timestamp is not None else None


def _recent_syncs(recent_sync_jobs: list) -> list[dict[str, str | int | None]]:
    history: list[dict[str, str | int | None]] = []
    for job in recent_sync_jobs:
        history.append(
            {
                "job_id": job.job_id,
                "status": job.status,
                "mode": job.mode,
                "sync_origin": getattr(job, "sync_origin", None),
                "trigger_event": getattr(job, "trigger_event", None),
                "finished_at": job.finished_at.isoformat() if job.finished_at else None,
                "started_at": job.started_at.isoformat() if job.started_at else None,
            }
        )
    return history


def summarize_imported_evidence(artifacts: list, decisions: list, source_refs_by_decision: dict[int, list]) -> dict:
    reviewable_states = {"candidate", "accepted", "superseded"}
    reviewable_decisions = [decision for decision in decisions if decision.review_state in reviewable_states]
    artifact_lookup = {artifact.id: artifact for artifact in artifacts}
    source_type_counts: Counter[str] = Counter()
    contributing_doc_categories: Counter[str] = Counter()
    contributing_doc_paths: list[str] = []

    for decision in reviewable_decisions:
        for source_ref in source_refs_by_decision.get(decision.id, []):
            artifact = artifact_lookup.get(source_ref.artifact_id)
            if artifact is None:
                continue
            source_type_counts[artifact.type] += 1
            if artifact.type == "doc":
                metadata = artifact.metadata_json or {}
                contributing_doc_categories[str(metadata.get("signal_category") or "general")] += 1
                path = metadata.get("path")
                if isinstance(path, str) and path not in contributing_doc_paths:
                    contributing_doc_paths.append(path)

    return {
        "reviewable_decisions": len(reviewable_decisions),
        "decision_source_types": dict(source_type_counts),
        "contributing_doc_categories": dict(contributing_doc_categories),
        "contributing_doc_paths": contributing_doc_paths[:5],
    }


def _latest_datetime(*values: datetime | None) -> datetime | None:
    filtered = [value for value in values if value is not None]
    return max(filtered) if filtered else None


def _parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None
