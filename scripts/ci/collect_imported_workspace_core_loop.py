from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
from pathlib import Path
import subprocess
import sys
from typing import Any
from urllib import error, request
from urllib.parse import urlencode


SCHEMA_VERSION = 1
PASS_STATUSES = {"pass", "passed", "ok", "continue", "clean"}
WARNING_STATUSES = {
    "warning",
    "caution",
    "limited_support",
    "evidence_limited",
    "review_required",
    "operator_guided",
    "not_provided",
    "provider_failure",
    "local_stack_failure",
    "unknown",
}
BLOCKING_STATUSES = {"blocked", "blocking", "failed", "failure", "error", "pause"}


def _read_json(path: Path) -> dict[str, Any]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected JSON object at {path}")
    return loaded


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_markdown(path: Path, markdown: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def _json_request(
    *,
    base_url: str,
    path: str,
    method: str = "GET",
    body: dict[str, Any] | None = None,
    session_token: str | None = None,
    timeout: int = 30,
) -> tuple[dict[str, Any] | list[Any] | None, dict[str, Any] | None]:
    encoded_body = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Content-Type": "application/json"}
    if session_token:
        headers["x-decisionatlas-session-token"] = session_token
    http_request = request.Request(
        f"{base_url.rstrip('/')}{path}",
        data=encoded_body,
        headers=headers,
        method=method,
    )
    try:
        with request.urlopen(http_request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8")), None
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        return None, {"type": "http_error", "status": exc.code, "detail": detail}
    except error.URLError as exc:
        return None, {"type": "url_error", "detail": str(exc)}
    except TimeoutError as exc:
        return None, {"type": "timeout", "detail": str(exc)}


def _classify_request_error(error_payload: dict[str, Any] | None) -> str:
    if not error_payload:
        return "operator_guided"
    error_type = error_payload.get("type")
    if error_type in {"url_error", "timeout"}:
        return "local_stack_failure"
    status = error_payload.get("status")
    if status in {401, 403}:
        return "operator_guided"
    if status == 404:
        return "not_provided"
    detail = str(error_payload.get("detail") or "").lower()
    if "github" in detail or "provider" in detail or "network" in detail:
        return "provider_failure"
    return "warning"


def _status_rank(status: str) -> int:
    normalized = str(status or "unknown").lower()
    if normalized in BLOCKING_STATUSES or normalized in {"local_stack_failure", "provider_failure"}:
        return 2
    if normalized in WARNING_STATUSES:
        return 1
    if normalized in PASS_STATUSES:
        return 0
    return 1


def _overall_status(lanes: dict[str, dict[str, Any]]) -> str:
    ranks = [_status_rank(str(lane.get("status") or "unknown")) for lane in lanes.values()]
    if any(rank >= 2 for rank in ranks):
        return "blocking"
    if any(rank == 1 for rank in ranks):
        return "warning"
    return "pass"


def _lane(status: str, *, summary: str, next_action: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "status": status,
        "summary": summary,
        "next_action": next_action,
        "details": details or {},
    }


def _bounded_grounding(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _bounded_grounding(item) for key, item in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, list):
        return [_bounded_grounding(item) for item in value[:10]]
    if isinstance(value, str):
        text = value.strip()
        return text if len(text) <= 240 else text[:239].rstrip() + "..."
    return value


def _baseline_status(accepted_count: int, candidate_count: int, *, unavailable: bool = False) -> str:
    if unavailable:
        return "unavailable"
    if accepted_count > 0:
        return "present"
    if candidate_count > 0:
        return "empty"
    return "absent"


def _baseline_strength(accepted_count: int) -> str:
    if accepted_count >= 2:
        return "established"
    if accepted_count == 1:
        return "thin"
    return "none"


def _accepted_baseline_summary(
    *,
    candidate_count: int,
    candidate_sample_titles: list[str],
    accepted_payload: list[Any] | None,
    error_payload: dict[str, Any] | None,
) -> dict[str, Any]:
    if error_payload is not None or not isinstance(accepted_payload, list):
        return {
            "status": _baseline_status(0, candidate_count, unavailable=True),
            "strength": "unknown",
            "candidate_count": candidate_count,
            "accepted_count": 0,
            "candidate_sample_titles": candidate_sample_titles[:3],
            "accepted_sample_titles": [],
            "next_action": "inspect_accepted_decision_api_or_permissions",
            "error": error_payload,
        }
    accepted_sample_titles = [str(item.get("title")) for item in accepted_payload[:3] if isinstance(item, dict)]
    accepted_count = len(accepted_payload)
    status = _baseline_status(accepted_count, candidate_count)
    next_action = (
        "accepted_baseline_ready"
        if status == "present"
        else "review_candidates_into_accepted_baseline"
        if status == "empty"
        else "import_or_review_decision_candidates"
    )
    return {
        "status": status,
        "strength": _baseline_strength(accepted_count),
        "candidate_count": candidate_count,
        "accepted_count": accepted_count,
        "candidate_sample_titles": candidate_sample_titles[:3],
        "accepted_sample_titles": accepted_sample_titles,
        "next_action": next_action,
    }


def _why_grounding_reason(lane: dict[str, Any], accepted_baseline: dict[str, Any]) -> dict[str, Any] | None:
    status = str(lane.get("status") or "unknown")
    if _status_rank(status) != 1 or lane.get("action_category") != "product_controlled":
        return None
    details = lane.get("details") if isinstance(lane.get("details"), dict) else {}
    answer_status = str(details.get("answer_status") or "unknown")
    citation_count = int(details.get("citation_count") or 0)
    primary_decision = details.get("primary_decision")
    baseline_status = str(accepted_baseline.get("status") or "unknown")
    accepted_count = int(accepted_baseline.get("accepted_count") or 0)
    if citation_count <= 0 and not primary_decision and accepted_count <= 0:
        code = "missing_accepted_decision_evidence"
        summary = "Why-search has no citations or primary decision to ground the answer."
    elif answer_status in {"evidence_limited", "limited_support", "unknown"} or citation_count <= 0:
        code = "weak_why_support"
        summary = "Why-search returned weak support or insufficient citations."
    else:
        code = "unknown_grounding_gap"
        summary = "Why-search is warning but no specific supported reason was detected."
    return {
        "lane": "why_search",
        "code": code,
        "summary": summary,
        "next_action": lane.get("next_action"),
        "evidence": _bounded_grounding(
            {
                "answer_status": answer_status,
                "citation_count": citation_count,
                "primary_decision_present": bool(primary_decision),
                "workspace_mode": details.get("workspace_mode"),
                "accepted_baseline_status": baseline_status,
                "accepted_decision_count": accepted_count,
            }
        ),
    }


def _drift_grounding_reason(lane: dict[str, Any], accepted_baseline: dict[str, Any]) -> dict[str, Any] | None:
    status = str(lane.get("status") or "unknown")
    if _status_rank(status) != 1 or lane.get("action_category") != "product_controlled":
        return None
    details = lane.get("details") if isinstance(lane.get("details"), dict) else {}
    drift_state = str(details.get("drift_state") or "unknown")
    alert_count = int(details.get("alert_count") or 0)
    evaluation = details.get("evaluation") if isinstance(details.get("evaluation"), dict) else {}
    baseline_status = str(accepted_baseline.get("status") or "unknown")
    accepted_count = int(accepted_baseline.get("accepted_count") or 0)
    if alert_count > 0:
        code = "unresolved_drift_followup"
        summary = "Drift lane has unresolved alerts that need human follow-up."
    elif drift_state in {"stale", "superseded"} or evaluation.get("stale") or evaluation.get("superseded"):
        code = "stale_or_superseded_evidence"
        summary = "Drift evidence appears stale or superseded and needs refresh."
    elif accepted_count <= 0:
        code = "missing_accepted_decision_evidence"
        summary = "Drift warning may be caused by insufficient accepted-decision baseline evidence."
    elif drift_state in {"unknown", "unevaluated"}:
        code = "unknown_grounding_gap"
        summary = "Drift lane lacks a clean evaluated state or actionable alert evidence."
    else:
        code = "unknown_grounding_gap"
        summary = "Drift lane is warning but accepted baseline is present; inspect drift details."
    return {
        "lane": "drift",
        "code": code,
        "summary": summary,
        "next_action": lane.get("next_action"),
        "evidence": _bounded_grounding(
            {
                "drift_state": drift_state,
                "alert_count": alert_count,
                "evaluation_state": evaluation.get("state"),
                "evaluation_request_status": details.get("evaluation_request_status"),
                "accepted_baseline_status": baseline_status,
                "accepted_decision_count": accepted_count,
            }
        ),
    }


def _apply_grounding_metadata(
    lanes: dict[str, dict[str, Any]],
    *,
    accepted_baseline: dict[str, Any],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    lane_reasons: dict[str, list[dict[str, Any]]] = {}
    reason_builders = {
        "why_search": _why_grounding_reason,
        "drift": _drift_grounding_reason,
    }
    for lane_name, builder in reason_builders.items():
        lane = lanes.get(lane_name)
        if not isinstance(lane, dict):
            continue
        reason = builder(lane, accepted_baseline)
        if reason is None:
            continue
        lane.setdefault("grounding", {})["reasons"] = [reason]
        lane_reasons[lane_name] = [reason]
    codes = sorted({reason["code"] for reasons in lane_reasons.values() for reason in reasons})
    return lane_reasons, {
        "warning_lanes_with_grounding": len(lane_reasons),
        "reason_codes": codes,
    }


def _action_category(lane_name: str, lane: dict[str, Any], *, setup_waiting: bool) -> str:
    status = str(lane.get("status") or "unknown")
    if _status_rank(status) == 0:
        return "pass"
    if _status_rank(status) >= 2:
        return "blocking"
    if status == "not_provided":
        return "not_provided"
    if status in {"provider_failure", "local_stack_failure"}:
        return "external_dependency"
    next_action = str(lane.get("next_action") or "")
    if setup_waiting and lane_name in {"review", "why_search", "drift"}:
        return "operator_setup"
    if next_action in {"run_public_import_rehearsal", "wait_for_import"}:
        return "operator_setup"
    if lane_name in {"review", "why_search", "drift", "guardrail"}:
        return "product_controlled"
    return "operator_setup"


def _apply_action_categories(lanes: dict[str, dict[str, Any]], *, setup_waiting: bool) -> dict[str, int]:
    counts = {
        "product_controlled": 0,
        "operator_setup": 0,
        "external_dependency": 0,
        "not_provided": 0,
        "blocking": 0,
    }
    for lane_name, lane in lanes.items():
        category = _action_category(lane_name, lane, setup_waiting=setup_waiting)
        lane["action_category"] = category
        if category in counts:
            counts[category] += 1
    return counts


def _derive_workspace_and_repo(
    *,
    workspace_slug: str | None,
    repo: str | None,
    import_rehearsal: dict[str, Any] | None,
) -> tuple[str | None, str | None, dict[str, Any]]:
    setup: dict[str, Any] = {"source": "explicit"}
    if import_rehearsal:
        setup = dict(import_rehearsal.get("setup") or {})
        repository = import_rehearsal.get("repository") if isinstance(import_rehearsal.get("repository"), dict) else {}
        workspace_slug = workspace_slug or repository.get("workspace_slug")
        repo = repo or repository.get("repo")
        setup["source"] = "public_import_rehearsal"
    return workspace_slug, repo, setup


def _probe_dashboard(*, base_url: str, workspace_slug: str, session_token: str | None) -> dict[str, Any]:
    query = urlencode({"workspace_slug": workspace_slug})
    payload, error_payload = _json_request(
        base_url=base_url,
        path=f"/dashboard/summary?{query}",
        session_token=session_token,
    )
    if error_payload is not None or not isinstance(payload, dict):
        status = _classify_request_error(error_payload)
        return _lane(status, summary="Dashboard summary unavailable.", next_action="inspect_workspace_or_stack", details={"error": error_payload})
    decision_counts = payload.get("decision_counts") if isinstance(payload.get("decision_counts"), dict) else {}
    return _lane(
        "pass",
        summary="Dashboard summary loaded for imported workspace.",
        next_action="review_candidates_or_ask_why",
        details={
            "workspace_slug": payload.get("workspace_slug"),
            "github_repo": payload.get("github_repo"),
            "workspace_mode": payload.get("workspace_mode"),
            "import_status": payload.get("import_status"),
            "candidate_decisions": decision_counts.get("candidate", 0),
            "accepted_decisions": decision_counts.get("accepted", 0),
            "drift_state": (payload.get("drift_status") or {}).get("state") if isinstance(payload.get("drift_status"), dict) else None,
            "readiness_state": (payload.get("workspace_readiness") or {}).get("state") if isinstance(payload.get("workspace_readiness"), dict) else None,
        },
    )


def _probe_review(*, base_url: str, workspace_slug: str, session_token: str | None) -> tuple[dict[str, Any], dict[str, Any]]:
    candidate_query = urlencode({"workspace_slug": workspace_slug, "review_state": "candidate"})
    candidate_payload, candidate_error = _json_request(base_url=base_url, path=f"/decisions?{candidate_query}", session_token=session_token)
    if candidate_error is not None or not isinstance(candidate_payload, list):
        baseline = _accepted_baseline_summary(
            candidate_count=0,
            candidate_sample_titles=[],
            accepted_payload=None,
            error_payload=candidate_error,
        )
        status = _classify_request_error(candidate_error)
        return (
            _lane(status, summary="Review queue unavailable.", next_action="inspect_review_api_or_permissions", details={"error": candidate_error}),
            baseline,
        )
    count = len(candidate_payload)
    candidate_sample_titles = [str(item.get("title")) for item in candidate_payload[:3] if isinstance(item, dict)]
    accepted_query = urlencode({"workspace_slug": workspace_slug, "review_state": "accepted"})
    accepted_payload, accepted_error = _json_request(base_url=base_url, path=f"/decisions?{accepted_query}", session_token=session_token)
    baseline = _accepted_baseline_summary(
        candidate_count=count,
        candidate_sample_titles=candidate_sample_titles,
        accepted_payload=accepted_payload if isinstance(accepted_payload, list) else None,
        error_payload=accepted_error,
    )
    status = "pass" if count > 0 else "warning"
    return (
        _lane(
            status,
            summary="Review queue has candidate decisions." if count else "Review queue is empty; accepted baseline may be missing or already reviewed.",
            next_action="review_candidates" if count else "inspect_import_quality_or_existing_decisions",
            details={
                "candidate_count": count,
                "sample_titles": candidate_sample_titles,
                "accepted_baseline": baseline,
            },
        ),
        baseline,
    )


def _probe_why(*, base_url: str, workspace_slug: str, question: str, session_token: str | None) -> dict[str, Any]:
    payload, error_payload = _json_request(
        base_url=base_url,
        path="/query/why",
        method="POST",
        body={"workspace_slug": workspace_slug, "question": question},
        session_token=session_token,
    )
    if error_payload is not None or not isinstance(payload, dict):
        status = _classify_request_error(error_payload)
        return _lane(status, summary="Why-search unavailable.", next_action="inspect_query_api_or_workspace_evidence", details={"error": error_payload})
    answer_status = str(payload.get("status") or "unknown")
    lane_status = "pass" if answer_status == "ok" else "warning"
    citations = payload.get("citations") if isinstance(payload.get("citations"), list) else []
    return _lane(
        lane_status,
        summary=f"Why-search returned `{answer_status}`.",
        next_action="inspect_citations" if citations else "improve_accepted_decision_evidence",
        details={
            "answer_status": answer_status,
            "question": payload.get("question") or question,
            "citation_count": len(citations),
            "workspace_mode": (payload.get("answer_context") or {}).get("workspace_mode") if isinstance(payload.get("answer_context"), dict) else None,
            "primary_decision": payload.get("primary_decision"),
        },
    )


def _probe_drift(*, base_url: str, workspace_slug: str, session_token: str | None, evaluate: bool) -> dict[str, Any]:
    evaluation_payload = None
    evaluation_error = None
    if evaluate:
        evaluation_payload, evaluation_error = _json_request(
            base_url=base_url,
            path="/drift/evaluate",
            method="POST",
            body={"workspace_slug": workspace_slug},
            session_token=session_token,
        )
    query = urlencode({"workspace_slug": workspace_slug})
    payload, error_payload = _json_request(base_url=base_url, path=f"/drift?{query}", session_token=session_token)
    if error_payload is not None or not isinstance(payload, dict):
        status = _classify_request_error(error_payload)
        return _lane(status, summary="Drift evidence unavailable.", next_action="inspect_drift_api_or_evaluate", details={"error": error_payload, "evaluation_error": evaluation_error})
    alerts = payload.get("alerts") if isinstance(payload.get("alerts"), list) else []
    evaluation = payload.get("evaluation") if isinstance(payload.get("evaluation"), dict) else None
    drift_state = (evaluation or {}).get("state") or ("alerts_present" if alerts else "unknown")
    status = "pass" if drift_state in {"clean", "alerts_present", "unevaluated", "stale"} else "warning"
    return _lane(
        status,
        summary=f"Drift lane returned `{drift_state}` with {len(alerts)} alert(s).",
        next_action="inspect_alerts" if alerts else "evaluate_or_monitor_drift",
        details={
            "drift_state": drift_state,
            "alert_count": len(alerts),
            "evaluation": evaluation,
            "evaluation_request_status": (evaluation_payload or {}).get("status") if isinstance(evaluation_payload, dict) else None,
            "evaluation_error": evaluation_error,
        },
    )


def _parse_guardrail_summary(text: str) -> dict[str, Any]:
    guardrail: dict[str, Any] = {
        "agent_status": "unknown",
        "diff_status": None,
        "drift_status": None,
        "required_tests": [],
        "findings": [],
    }
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("Agent status:"):
            guardrail["agent_status"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("Diff check:"):
            guardrail["diff_status"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("Drift report:"):
            guardrail["drift_status"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("- "):
            guardrail["findings"].append(stripped[2:].strip())
    return {"guardrail": guardrail}


def _run_guardrail(root: Path) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    command = [sys.executable, "scripts/governance/agent_guardrail.py", "--summary"]
    try:
        result = subprocess.run(command, cwd=root, check=False, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError, TimeoutError) as exc:
        return None, {"type": "subprocess_error", "detail": str(exc)}
    if result.returncode != 0:
        return None, {"type": "subprocess_failed", "status": result.returncode, "detail": result.stderr or result.stdout}
    return _parse_guardrail_summary(result.stdout), None


def _probe_guardrail(*, root: Path, guardrail_json: Path | None, run_guardrail: bool) -> dict[str, Any]:
    payload = None
    error_payload = None
    if guardrail_json is not None:
        try:
            payload = _read_json(guardrail_json)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            error_payload = {"type": "invalid_guardrail_json", "detail": str(exc)}
    elif run_guardrail:
        payload, error_payload = _run_guardrail(root)
    else:
        return _lane("not_provided", summary="Guardrail evidence was not provided.", next_action="run_agent_guardrail", details={})

    if error_payload is not None or not isinstance(payload, dict):
        return _lane("warning", summary="Guardrail evidence unavailable or invalid.", next_action="run_agent_guardrail", details={"error": error_payload})
    guardrail = payload.get("guardrail") if isinstance(payload.get("guardrail"), dict) else payload
    agent_status = str(guardrail.get("agent_status") or guardrail.get("status") or "unknown")
    status = "pass" if agent_status == "continue" else "warning" if agent_status == "caution" else "blocking" if agent_status == "pause" else "warning"
    return _lane(
        status,
        summary=f"Guardrail returned `{agent_status}`.",
        next_action="continue_with_targeted_validation" if status == "pass" else "inspect_guardrail_findings",
        details={
            "agent_status": agent_status,
            "diff_status": guardrail.get("diff_status"),
            "drift_status": guardrail.get("drift_status"),
            "required_tests_count": len(guardrail.get("required_tests") or []),
            "findings_count": len(guardrail.get("findings") or []),
        },
    )


def build_report(
    *,
    root: Path,
    base_url: str,
    repo: str | None,
    workspace_slug: str | None,
    import_rehearsal_json: Path | None,
    guardrail_json: Path | None,
    run_guardrail: bool,
    session_token: str | None,
    why_question: str,
    evaluate_drift: bool,
    generated_at: str | None = None,
) -> dict[str, Any]:
    import_rehearsal = _read_json(import_rehearsal_json) if import_rehearsal_json else None
    workspace_slug, repo, setup = _derive_workspace_and_repo(
        workspace_slug=workspace_slug,
        repo=repo,
        import_rehearsal=import_rehearsal,
    )
    lanes: dict[str, dict[str, Any]] = {}
    setup_outcome = str(setup.get("outcome") or ("provided" if workspace_slug else "not_provided"))
    setup_waiting = bool(setup.get("next_action") == "wait_for_import" or setup.get("benchmark_ready") is False)
    setup_status = "pass" if setup_outcome in {"created", "reused", "provided"} and workspace_slug else "warning"
    if setup_outcome in {"provider_failure", "local_stack_failure"}:
        setup_status = setup_outcome
    lanes["setup"] = _lane(
        setup_status,
        summary=f"Workspace setup source `{setup.get('source', 'explicit')}` reported `{setup_outcome}`.",
        next_action="probe_core_loop" if workspace_slug else "run_public_import_rehearsal",
        details={"workspace_slug": workspace_slug, "repo": repo, "setup": setup},
    )

    if workspace_slug:
        lanes["dashboard"] = _probe_dashboard(base_url=base_url, workspace_slug=workspace_slug, session_token=session_token)
        lanes["review"], accepted_baseline = _probe_review(base_url=base_url, workspace_slug=workspace_slug, session_token=session_token)
        lanes["why_search"] = _probe_why(base_url=base_url, workspace_slug=workspace_slug, question=why_question, session_token=session_token)
        lanes["drift"] = _probe_drift(base_url=base_url, workspace_slug=workspace_slug, session_token=session_token, evaluate=evaluate_drift)
    else:
        accepted_baseline = {
            "status": "not_provided",
            "strength": "unknown",
            "candidate_count": 0,
            "accepted_count": 0,
            "candidate_sample_titles": [],
            "accepted_sample_titles": [],
            "next_action": "run_public_import_rehearsal",
        }
        for lane_name in ("dashboard", "review", "why_search", "drift"):
            lanes[lane_name] = _lane("not_provided", summary="Workspace slug missing.", next_action="run_public_import_rehearsal")
    lanes["guardrail"] = _probe_guardrail(root=root, guardrail_json=guardrail_json, run_guardrail=run_guardrail)
    action_summary = _apply_action_categories(lanes, setup_waiting=setup_waiting)
    lane_reasons, grounding_summary = _apply_grounding_metadata(lanes, accepted_baseline=accepted_baseline)

    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at or datetime.now(UTC).isoformat(),
        "evidence_type": "imported-workspace-core-loop-rehearsal",
        "status": _overall_status(lanes),
        "base_url": base_url,
        "repository": {"repo": repo, "workspace_slug": workspace_slug},
        "accepted_baseline": accepted_baseline,
        "lanes": lanes,
        "lane_reasons": lane_reasons,
        "summary": {
            "pass_lanes": sum(1 for lane in lanes.values() if _status_rank(str(lane.get("status"))) == 0),
            "warning_lanes": sum(1 for lane in lanes.values() if _status_rank(str(lane.get("status"))) == 1),
            "blocking_lanes": sum(1 for lane in lanes.values() if _status_rank(str(lane.get("status"))) >= 2),
            "action_categories": action_summary,
            "accepted_baseline": accepted_baseline,
            "grounding_summary": grounding_summary,
            "setup_waiting": setup_waiting,
        },
        "recommended_next_actions": sorted({str(lane.get("next_action")) for lane in lanes.values() if lane.get("next_action")}),
        "sensitive_material_note": "This report stores compact statuses/counts only. Do not include tokens, raw private source, or raw model output.",
    }
    return report


def _markdown_cell(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value).replace("|", "\\|").replace("\n", "<br>") or "-"


def render_markdown(report: dict[str, Any]) -> str:
    repository = report.get("repository") if isinstance(report.get("repository"), dict) else {}
    lanes = report.get("lanes") if isinstance(report.get("lanes"), dict) else {}
    lines = [
        "# Imported Workspace Core Loop Rehearsal",
        "",
        f"- Generated at: `{report.get('generated_at')}`",
        f"- Status: `{report.get('status')}`",
        f"- Repository: `{repository.get('repo', '-')}`",
        f"- Workspace slug: `{repository.get('workspace_slug', '-')}`",
        f"- Base URL: `{report.get('base_url')}`",
        f"- Accepted baseline: `{(report.get('accepted_baseline') or {}).get('status', '-')}`",
        "",
        "## Accepted Baseline",
        "",
        f"- Summary: `{_markdown_cell(report.get('accepted_baseline'))}`",
        "",
        "## Lanes",
        "",
        "| Lane | Status | Action category | Grounding | Summary | Next action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for name, lane in lanes.items():
        if not isinstance(lane, dict):
            continue
        lines.append(
            f"| {_markdown_cell(name)} | {_markdown_cell(lane.get('status'))} | {_markdown_cell(lane.get('action_category'))} | {_markdown_cell(lane.get('grounding'))} | {_markdown_cell(lane.get('summary'))} | {_markdown_cell(lane.get('next_action'))} |"
        )
    lines.extend(["", "## Recommended Next Actions", ""])
    for action in report.get("recommended_next_actions") or []:
        lines.append(f"- `{action}`")
    lines.extend(["", "## Evidence Boundary", "", f"- {report.get('sensitive_material_note')}", ""])
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect imported workspace core-loop rehearsal evidence.")
    parser.add_argument("--base-url", default="http://127.0.0.1:3001")
    parser.add_argument("--repo")
    parser.add_argument("--workspace-slug")
    parser.add_argument("--import-rehearsal-json")
    parser.add_argument("--guardrail-json")
    parser.add_argument("--run-guardrail", action="store_true")
    parser.add_argument("--session-token")
    parser.add_argument("--why-question", default="why was this architecture decision made")
    parser.add_argument("--evaluate-drift", action="store_true")
    parser.add_argument("--generated-at")
    parser.add_argument("--output-json", default=".tmp/imported-workspace-core-loop-rehearsal.json")
    parser.add_argument("--output-markdown", default=".tmp/imported-workspace-core-loop-rehearsal.md")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    try:
        report = build_report(
            root=root,
            base_url=args.base_url,
            repo=args.repo,
            workspace_slug=args.workspace_slug,
            import_rehearsal_json=(root / args.import_rehearsal_json) if args.import_rehearsal_json else None,
            guardrail_json=(root / args.guardrail_json) if args.guardrail_json else None,
            run_guardrail=args.run_guardrail,
            session_token=args.session_token,
            why_question=args.why_question,
            evaluate_drift=args.evaluate_drift,
            generated_at=args.generated_at,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Failed to collect imported workspace core loop evidence: {exc}", file=sys.stderr)
        return 1
    _write_json(root / args.output_json, report)
    _write_markdown(root / args.output_markdown, render_markdown(report))
    print(f"Imported workspace core loop JSON written to {root / args.output_json}")
    print(f"Imported workspace core loop Markdown written to {root / args.output_markdown}")
    print(f"Status: {report['status']}")
    return 1 if report["status"] == "blocking" else 0


if __name__ == "__main__":
    raise SystemExit(main())
