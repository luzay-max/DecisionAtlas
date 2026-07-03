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


def _probe_review(*, base_url: str, workspace_slug: str, session_token: str | None) -> dict[str, Any]:
    query = urlencode({"workspace_slug": workspace_slug, "review_state": "candidate"})
    payload, error_payload = _json_request(base_url=base_url, path=f"/decisions?{query}", session_token=session_token)
    if error_payload is not None or not isinstance(payload, list):
        status = _classify_request_error(error_payload)
        return _lane(status, summary="Review queue unavailable.", next_action="inspect_review_api_or_permissions", details={"error": error_payload})
    count = len(payload)
    status = "pass" if count > 0 else "warning"
    return _lane(
        status,
        summary="Review queue has candidate decisions." if count else "Review queue is empty; accepted baseline may be missing or already reviewed.",
        next_action="review_candidates" if count else "inspect_import_quality_or_existing_decisions",
        details={
            "candidate_count": count,
            "sample_titles": [str(item.get("title")) for item in payload[:3] if isinstance(item, dict)],
        },
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


def _run_guardrail(root: Path) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    command = [sys.executable, "scripts/governance/agent_guardrail.py", "--summary", "--json"]
    try:
        result = subprocess.run(command, cwd=root, check=False, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError, TimeoutError) as exc:
        return None, {"type": "subprocess_error", "detail": str(exc)}
    if result.returncode != 0:
        return None, {"type": "subprocess_failed", "status": result.returncode, "detail": result.stderr or result.stdout}
    try:
        return json.loads(result.stdout), None
    except json.JSONDecodeError as exc:
        return None, {"type": "invalid_json", "detail": str(exc)}


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
        lanes["review"] = _probe_review(base_url=base_url, workspace_slug=workspace_slug, session_token=session_token)
        lanes["why_search"] = _probe_why(base_url=base_url, workspace_slug=workspace_slug, question=why_question, session_token=session_token)
        lanes["drift"] = _probe_drift(base_url=base_url, workspace_slug=workspace_slug, session_token=session_token, evaluate=evaluate_drift)
    else:
        for lane_name in ("dashboard", "review", "why_search", "drift"):
            lanes[lane_name] = _lane("not_provided", summary="Workspace slug missing.", next_action="run_public_import_rehearsal")
    lanes["guardrail"] = _probe_guardrail(root=root, guardrail_json=guardrail_json, run_guardrail=run_guardrail)

    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at or datetime.now(UTC).isoformat(),
        "evidence_type": "imported-workspace-core-loop-rehearsal",
        "status": _overall_status(lanes),
        "base_url": base_url,
        "repository": {"repo": repo, "workspace_slug": workspace_slug},
        "lanes": lanes,
        "summary": {
            "pass_lanes": sum(1 for lane in lanes.values() if _status_rank(str(lane.get("status"))) == 0),
            "warning_lanes": sum(1 for lane in lanes.values() if _status_rank(str(lane.get("status"))) == 1),
            "blocking_lanes": sum(1 for lane in lanes.values() if _status_rank(str(lane.get("status"))) >= 2),
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
        "",
        "## Lanes",
        "",
        "| Lane | Status | Summary | Next action |",
        "| --- | --- | --- | --- |",
    ]
    for name, lane in lanes.items():
        if not isinstance(lane, dict):
            continue
        lines.append(
            f"| {_markdown_cell(name)} | {_markdown_cell(lane.get('status'))} | {_markdown_cell(lane.get('summary'))} | {_markdown_cell(lane.get('next_action'))} |"
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
