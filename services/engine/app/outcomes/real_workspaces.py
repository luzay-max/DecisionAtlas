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
    decision_counts: dict[str, int],
    drift_status: dict,
) -> dict:
    candidate_count = decision_counts.get("candidate", 0)
    accepted_count = decision_counts.get("accepted", 0)
    summary = dict(latest_import_summary or {})
    outcome = summary.get("outcome")

    if latest_import_status == "failed":
        state = "analysis_failed"
        next_action = "retry_import"
        why_state = "analysis_failed"
    elif candidate_count > 0:
        state = "review_ready"
        next_action = "review_candidates"
        why_state = "review_required"
    elif accepted_count > 0:
        state = "why_ready"
        next_action = "ask_why"
        why_state = "ready"
    elif outcome == "insufficient_evidence":
        state = "evidence_limited"
        next_action = "inspect_import_summary"
        why_state = "evidence_limited"
    else:
        state = "import_complete"
        next_action = "inspect_import_summary"
        why_state = "review_required"

    return {
        "state": state,
        "next_action": next_action,
        "why_state": why_state,
        "drift_state": drift_status["state"],
    }


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
