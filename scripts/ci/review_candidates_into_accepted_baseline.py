from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
from pathlib import Path
import sys
from typing import Any
from urllib import error, request
from urllib.parse import urlencode


SCHEMA_VERSION = 1
MAX_ACCEPT_LIMIT = 10


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_markdown(path: Path, markdown: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def _bounded(value: Any, *, limit: int = 400) -> Any:
    if isinstance(value, dict):
        return {str(key): _bounded(item, limit=limit) for key, item in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, list):
        return [_bounded(item, limit=limit) for item in value[:20]]
    if isinstance(value, str):
        text = value.strip()
        return text if len(text) <= limit else text[: limit - 1].rstrip() + "..."
    return value


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
        return None, {"type": "http_error", "status": exc.code, "detail": _bounded(detail)}
    except error.URLError as exc:
        return None, {"type": "url_error", "detail": _bounded(str(exc))}
    except TimeoutError as exc:
        return None, {"type": "timeout", "detail": str(exc)}


def _decision_summary(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item.get("id"),
        "title": _bounded(item.get("title")),
        "review_state": item.get("review_state"),
        "confidence": item.get("confidence"),
        "candidate_quality": _bounded(item.get("candidate_quality") if isinstance(item.get("candidate_quality"), dict) else None),
    }


def _list_decisions(
    *,
    base_url: str,
    workspace_slug: str,
    review_state: str,
    session_token: str | None,
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    query = urlencode({"workspace_slug": workspace_slug, "review_state": review_state})
    payload, error_payload = _json_request(base_url=base_url, path=f"/decisions?{query}", session_token=session_token)
    if error_payload is not None or not isinstance(payload, list):
        return [], error_payload or {"type": "invalid_response", "detail": "Expected decision list."}
    return [item for item in payload if isinstance(item, dict)], None


def _review_decision(
    *,
    base_url: str,
    decision_id: int,
    review_state: str,
    review_rationale: str,
    session_token: str | None,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    return _json_request(
        base_url=base_url,
        path=f"/decisions/{decision_id}/review",
        method="POST",
        body={"review_state": review_state, "review_rationale": review_rationale},
        session_token=session_token,
    )


def _status(*, errors: list[dict[str, Any]], selected: list[dict[str, Any]], confirmed: bool, accepted: list[dict[str, Any]]) -> str:
    if any((error.get("status") in {401, 403, 404} or error.get("type") in {"url_error", "timeout"}) for error in errors):
        return "blocking"
    if errors:
        return "warning"
    if confirmed and selected and len(accepted) < len(selected):
        return "warning"
    return "pass"


def build_report(
    *,
    base_url: str,
    workspace_slug: str,
    max_accept: int,
    confirm_accept: bool,
    review_rationale: str | None,
    session_token: str | None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    if max_accept < 1 or max_accept > MAX_ACCEPT_LIMIT:
        raise ValueError(f"max_accept must be between 1 and {MAX_ACCEPT_LIMIT}.")
    rationale = (review_rationale or "").strip()
    if confirm_accept and not rationale:
        raise ValueError("--review-rationale is required when --confirm-accept is used.")

    candidates, candidate_error = _list_decisions(
        base_url=base_url,
        workspace_slug=workspace_slug,
        review_state="candidate",
        session_token=session_token,
    )
    accepted_before, accepted_before_error = _list_decisions(
        base_url=base_url,
        workspace_slug=workspace_slug,
        review_state="accepted",
        session_token=session_token,
    )
    selected = candidates[:max_accept]
    accepted_results: list[dict[str, Any]] = []
    errors = [error for error in (candidate_error, accepted_before_error) if error]

    if confirm_accept and not errors:
        for candidate in selected:
            decision_id = candidate.get("id")
            if not isinstance(decision_id, int):
                errors.append({"type": "invalid_candidate", "detail": f"Candidate missing integer id: {candidate.get('id')}"})
                continue
            payload, error_payload = _review_decision(
                base_url=base_url,
                decision_id=decision_id,
                review_state="accepted",
                review_rationale=rationale,
                session_token=session_token,
            )
            if error_payload is not None or not isinstance(payload, dict):
                errors.append({"decision_id": decision_id, **(error_payload or {"type": "invalid_response"})})
                continue
            accepted_results.append(_decision_summary(payload))

    accepted_after, accepted_after_error = _list_decisions(
        base_url=base_url,
        workspace_slug=workspace_slug,
        review_state="accepted",
        session_token=session_token,
    )
    if accepted_after_error:
        errors.append(accepted_after_error)

    mode = "confirmed_accept" if confirm_accept else "dry_run"
    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at or datetime.now(UTC).isoformat(),
        "evidence_type": "review-candidates-into-accepted-baseline",
        "mode": mode,
        "status": _status(errors=errors, selected=selected, confirmed=confirm_accept, accepted=accepted_results),
        "base_url": base_url,
        "workspace_slug": workspace_slug,
        "max_accept": max_accept,
        "review_rationale": _bounded(rationale) if rationale else None,
        "before": {
            "candidate_count": len(candidates),
            "accepted_count": len(accepted_before),
        },
        "after": {
            "candidate_count": max(0, len(candidates) - len(accepted_results)) if confirm_accept else len(candidates),
            "accepted_count": len(accepted_after),
        },
        "selected_candidates": [_decision_summary(item) for item in selected],
        "accepted_decisions": accepted_results,
        "errors": _bounded(errors),
        "next_action": (
            "rerun_core_loop_baseline_evidence"
            if confirm_accept and accepted_results
            else "rerun_with_confirm_accept_and_rationale"
            if selected and not confirm_accept
            else "inspect_review_api_or_candidates"
            if errors
            else "no_candidate_decisions_to_accept"
        ),
        "limitations": [
            "Dry-run mode does not mutate review state.",
            "Confirmed mode accepts only the bounded candidate prefix returned by the existing review API order.",
            "This evidence stores decision IDs/titles and bounded metadata only; do not include secrets or raw private source.",
        ],
    }
    return report


def _markdown_cell(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value).replace("|", "\\|").replace("\n", "<br>") or "-"


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Review Candidates Into Accepted Baseline",
        "",
        f"- Generated at: `{report.get('generated_at')}`",
        f"- Status: `{report.get('status')}`",
        f"- Mode: `{report.get('mode')}`",
        f"- Workspace: `{report.get('workspace_slug')}`",
        f"- Max accept: `{report.get('max_accept')}`",
        f"- Before: `{_markdown_cell(report.get('before'))}`",
        f"- After: `{_markdown_cell(report.get('after'))}`",
        f"- Next action: `{report.get('next_action')}`",
        "",
        "## Selected Candidates",
        "",
        "| ID | Title | Review state | Confidence |",
        "| --- | --- | --- | --- |",
    ]
    for item in report.get("selected_candidates") or []:
        lines.append(
            f"| {_markdown_cell(item.get('id'))} | {_markdown_cell(item.get('title'))} | {_markdown_cell(item.get('review_state'))} | {_markdown_cell(item.get('confidence'))} |"
        )
    lines.extend(["", "## Accepted Decisions", ""])
    accepted = report.get("accepted_decisions") or []
    if accepted:
        for item in accepted:
            lines.append(f"- `{item.get('id')}` {item.get('title')}")
    else:
        lines.append("- None")
    lines.extend(["", "## Errors", ""])
    errors = report.get("errors") or []
    if errors:
        for item in errors:
            lines.append(f"- `{_markdown_cell(item)}`")
    else:
        lines.append("- None")
    lines.extend(["", "## Limitations", ""])
    for item in report.get("limitations") or []:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Review selected candidate decisions into an accepted baseline.")
    parser.add_argument("--base-url", default="http://127.0.0.1:3001")
    parser.add_argument("--workspace-slug", required=True)
    parser.add_argument("--max-accept", type=int, default=1)
    parser.add_argument("--confirm-accept", action="store_true")
    parser.add_argument("--review-rationale")
    parser.add_argument("--session-token")
    parser.add_argument("--generated-at")
    parser.add_argument("--output-json", default=".tmp/review-candidates-into-accepted-baseline.json")
    parser.add_argument("--output-markdown", default=".tmp/review-candidates-into-accepted-baseline.md")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    try:
        report = build_report(
            base_url=args.base_url,
            workspace_slug=args.workspace_slug,
            max_accept=args.max_accept,
            confirm_accept=args.confirm_accept,
            review_rationale=args.review_rationale,
            session_token=args.session_token,
            generated_at=args.generated_at,
        )
    except ValueError as exc:
        print(f"Failed to review candidates into accepted baseline: {exc}", file=sys.stderr)
        return 2
    _write_json(root / args.output_json, report)
    _write_markdown(root / args.output_markdown, render_markdown(report))
    print(f"Review baseline JSON written to {root / args.output_json}")
    print(f"Review baseline Markdown written to {root / args.output_markdown}")
    print(f"Status: {report['status']}")
    return 2 if report["status"] == "blocking" else 0


if __name__ == "__main__":
    raise SystemExit(main())
