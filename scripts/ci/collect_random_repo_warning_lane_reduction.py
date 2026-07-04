from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
STATUS_PASS = "pass"
STATUS_WARNING = "warning"
STATUS_BLOCKING = "blocking"
STATUS_OPERATOR_GUIDED = "operator_guided"
STATUS_NOT_PROVIDED = "not_provided"
STATUS_UNKNOWN = "unknown"

PASS_STATUSES = {"pass", "passed", "ok", "success", "succeeded", "clean", "ready", "true"}
BLOCKING_STATUSES = {"blocking", "blocked", "failed", "failure", "error", "false", "provider_failure", "local_stack_failure"}
WARNING_STATUSES = {"warning", "warn", "caution", "known_limitation", "needs_review", "manual_check", "unknown"}

PRODUCT_TERMS = {
    "accepted_decision",
    "benchmark",
    "candidate",
    "decision",
    "drift",
    "evidence",
    "guardrail",
    "import",
    "review",
    "support",
    "why",
}
OPERATOR_TERMS = {
    "browser",
    "customer",
    "customer_host",
    "host",
    "hosted",
    "manual",
    "operator",
    "placeholder",
    "sample",
    "template",
    "walkthrough",
}
EXTERNAL_TERMS = {
    "github_api",
    "network",
    "provider",
    "provider_failure",
    "rate_limit",
    "timeout",
    "unavailable",
}


def normalize_status(value: Any, default: str = STATUS_UNKNOWN) -> str:
    if isinstance(value, bool):
        return STATUS_PASS if value else STATUS_BLOCKING
    if value is None:
        return default
    normalized = str(value).strip().lower().replace(" ", "_").replace("-", "_")
    if normalized in PASS_STATUSES:
        return STATUS_PASS
    if normalized in BLOCKING_STATUSES:
        return STATUS_BLOCKING
    if normalized in {"operator", "operator_guided", "manual", "manual_required"}:
        return STATUS_OPERATOR_GUIDED
    if normalized in {"missing", "omitted", "not_provided", "not_available"}:
        return STATUS_NOT_PROVIDED
    if normalized in WARNING_STATUSES:
        return STATUS_WARNING
    return normalized or default


def status_rank(status: Any) -> int:
    normalized = normalize_status(status)
    if normalized == STATUS_BLOCKING:
        return 2
    if normalized == STATUS_PASS:
        return 0
    return 1


def combined_status(statuses: list[str]) -> str:
    if any(status_rank(status) >= 2 for status in statuses):
        return STATUS_BLOCKING
    if any(status_rank(status) == 1 for status in statuses):
        return STATUS_WARNING
    return STATUS_PASS


def _resolve_path(path: str | Path | None, root: Path) -> Path | None:
    if path is None or str(path).strip() == "":
        return None
    candidate = Path(path)
    return candidate if candidate.is_absolute() else root / candidate


def _display_path(path: Path | None, root: Path) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return None, f"read_error:{exc}"
    except json.JSONDecodeError as exc:
        return None, f"json_error:{exc}"
    if not isinstance(data, dict):
        return None, "json_not_object"
    return data, None


def _bounded(value: Any, *, limit: int = 600) -> Any:
    if isinstance(value, dict):
        return {str(key): _bounded(item, limit=limit) for key, item in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, list):
        return [_bounded(item, limit=limit) for item in value[:30]]
    if isinstance(value, str):
        text = value.strip()
        return text if len(text) <= limit else text[: limit - 1].rstrip() + "..."
    return value


def _source_status(data: dict[str, Any] | None) -> str:
    if data is None:
        return STATUS_NOT_PROVIDED
    for key in ("status", "overall_status", "public_walkthrough_status", "agent_status", "result", "outcome"):
        if key in data:
            return normalize_status(data.get(key))
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    if "status" in summary:
        return normalize_status(summary.get("status"))
    return STATUS_UNKNOWN


def _collect_selected_repo_ids(sources: list[dict[str, Any]]) -> list[str]:
    ids: list[str] = []
    for source in sources:
        data = source.get("data")
        if not isinstance(data, dict):
            continue
        candidates = data.get("selected_repo_ids") or data.get("repo_ids")
        if not isinstance(candidates, list):
            continue
        for repo_id in candidates:
            text = str(repo_id)
            if text not in ids:
                ids.append(text)
    return ids


def _text_blob(*values: Any) -> str:
    return json.dumps(values, ensure_ascii=False, sort_keys=True).lower()


def _classify_lane(lane: dict[str, Any]) -> tuple[str, str]:
    status = normalize_status(lane.get("status"))
    text = _text_blob(lane.get("id"), lane.get("source_id"), lane.get("label"), lane.get("summary"), lane.get("warnings"))
    if status == STATUS_BLOCKING:
        return "blocking", "source lane is blocking"
    if status == STATUS_NOT_PROVIDED:
        return "not_provided", "source evidence is absent or explicitly not provided"
    if status == STATUS_OPERATOR_GUIDED:
        return "operator_guided", "source lane requires operator/manual proof"
    if any(term in text for term in OPERATOR_TERMS):
        return "operator_guided", "warning appears tied to hosted/customer/operator proof"
    if any(term in text for term in PRODUCT_TERMS):
        return "product_controlled", "warning appears reducible through product evidence or workflow improvements"
    if any(term in text for term in EXTERNAL_TERMS):
        return "external_dependency", "warning appears tied to provider, GitHub API, network, or availability conditions"
    return "product_controlled", "warning is non-clean and not attributable to external or operator-only causes"


def _source_summary(data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"status": STATUS_NOT_PROVIDED}
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    return {
        "status": _source_status(data),
        "summary": _bounded(summary),
        "selected_repo_ids": data.get("selected_repo_ids") or [],
        "recommended_follow_up": _bounded(data.get("recommended_follow_up") or []),
    }


def _load_source(source_id: str, label: str, path_text: str | None, root: Path) -> dict[str, Any]:
    path = _resolve_path(path_text, root)
    source = {
        "id": source_id,
        "label": label,
        "source_path": _display_path(path, root),
        "status": STATUS_NOT_PROVIDED,
        "summary": {"status": STATUS_NOT_PROVIDED},
        "data": None,
        "warnings": [],
    }
    if path is None:
        source["warnings"] = ["source_not_provided"]
        return source
    if not path.exists():
        source["warnings"] = ["source_missing"]
        return source
    data, error = _read_json(path)
    if error:
        source["status"] = STATUS_WARNING
        source["summary"] = {"status": STATUS_WARNING, "error": error}
        source["warnings"] = [error]
        return source
    source["data"] = data
    source["status"] = _source_status(data)
    source["summary"] = _source_summary(data)
    return source


def _lane_from_item(source: dict[str, Any], item: dict[str, Any], index: int, kind: str) -> dict[str, Any]:
    lane_id = str(item.get("id") or item.get("repo_id") or item.get("name") or f"{kind}_{index + 1}")
    return {
        "id": f"{source['id']}:{lane_id}",
        "source_id": source["id"],
        "lane_id": lane_id,
        "label": item.get("label") or item.get("name") or item.get("repo_id") or lane_id,
        "status": normalize_status(item.get("status") or item.get("overall_status") or item.get("result") or item.get("outcome")),
        "summary": _bounded(item.get("summary") if isinstance(item.get("summary"), dict) else item),
        "warnings": _bounded(item.get("warnings") or []),
        "source_path": source.get("source_path"),
    }


def _extract_lanes(source: dict[str, Any]) -> list[dict[str, Any]]:
    data = source.get("data")
    lanes: list[dict[str, Any]] = []
    if isinstance(data, dict):
        for key in ("lanes", "repositories", "checks", "artifacts"):
            items = data.get(key)
            if isinstance(items, list):
                for index, item in enumerate(items):
                    if isinstance(item, dict):
                        lanes.append(_lane_from_item(source, item, index, key))
    if not lanes:
        lanes.append(
            {
                "id": f"{source['id']}:source",
                "source_id": source["id"],
                "lane_id": "source",
                "label": source["label"],
                "status": normalize_status(source.get("status")),
                "summary": _bounded(source.get("summary") or {}),
                "warnings": _bounded(source.get("warnings") or []),
                "source_path": source.get("source_path"),
            }
        )
    return lanes


def _recommended_actions(summary: dict[str, int], selected_repo_ids: list[str]) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    if summary.get("blocking", 0):
        actions.append(
            {
                "priority": "P0",
                "category": "blocking",
                "action": "Fix blocking source evidence before treating the release rehearsal as shippable.",
            }
        )
    if summary.get("product_controlled", 0):
        repo_text = f" for {', '.join(selected_repo_ids)}" if selected_repo_ids else ""
        actions.append(
            {
                "priority": "P0",
                "category": "product_controlled",
                "action": f"Reduce product-controlled import/review/why/drift/guardrail warning lanes{repo_text}.",
            }
        )
    if summary.get("operator_guided", 0):
        actions.append(
            {
                "priority": "P1",
                "category": "operator_guided",
                "action": "Replace template/manual host evidence with real operator observations or disclose it in release notes.",
            }
        )
    if summary.get("external_dependency", 0):
        actions.append(
            {
                "priority": "P1",
                "category": "external_dependency",
                "action": "Rerun provider/GitHub/network-sensitive lanes or disclose external dependency limits.",
            }
        )
    if summary.get("not_provided", 0):
        actions.append(
            {
                "priority": "P2",
                "category": "not_provided",
                "action": "Attach missing optional evidence inputs before archiving release readiness.",
            }
        )
    if not actions:
        actions.append({"priority": "P2", "category": "pass", "action": "No warning-lane reduction action required."})
    return actions


def build_report(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    sources = [
        _load_source("multi_repo_diagnosis", "Multi-repo live diagnosis", args.multi_repo_diagnosis_json, root),
        _load_source("full_chain_random_repo_release", "Full-chain random repo release", args.full_chain_json, root),
        _load_source("release_rehearsal", "Release rehearsal", args.release_rehearsal_json, root),
        _load_source("real_external_host_trial", "Real external host trial", args.real_external_host_trial_json, root),
    ]
    selected_repo_ids = _collect_selected_repo_ids(sources)
    extracted = [lane for source in sources for lane in _extract_lanes(source)]
    classified_lanes = []
    for lane in extracted:
        if status_rank(lane.get("status")) == 0:
            continue
        category, rationale = _classify_lane(lane)
        classified_lanes.append({**lane, "category": category, "rationale": rationale})

    categories = ["product_controlled", "external_dependency", "operator_guided", "not_provided", "blocking"]
    category_counts = {category: sum(1 for lane in classified_lanes if lane["category"] == category) for category in categories}
    source_statuses = [normalize_status(source.get("status")) for source in sources]
    lane_statuses = [normalize_status(lane.get("status")) for lane in classified_lanes]
    top_status = combined_status(source_statuses + lane_statuses)

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": args.generated_at or datetime.now(UTC).isoformat(),
        "evidence_type": "random-repo-warning-lane-reduction",
        "label": args.label,
        "version_label": args.version_label,
        "commit": args.commit,
        "status": top_status,
        "selected_repo_ids": selected_repo_ids,
        "summary": {
            "sources": len(sources),
            "classified_lanes": len(classified_lanes),
            "pass_sources": sum(1 for source in sources if status_rank(source.get("status")) == 0),
            "warning_sources": sum(1 for source in sources if status_rank(source.get("status")) == 1),
            "blocking_sources": sum(1 for source in sources if status_rank(source.get("status")) >= 2),
            "selected_repositories": len(selected_repo_ids),
            **category_counts,
        },
        "sources": [{key: value for key, value in source.items() if key != "data"} for source in sources],
        "classified_lanes": classified_lanes,
        "reduction_actions": _recommended_actions(category_counts, selected_repo_ids),
        "limitations": [
            "This reducer explains warning lanes but does not change source release evidence status.",
            "Classification is deterministic and based on bounded source evidence, not raw logs or private source.",
            "External-host and customer-host confidence depends on the supplied operator evidence.",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Random Repo Warning Lane Reduction",
        "",
        f"- Status: `{report['status']}`",
        f"- Label: `{report.get('label') or 'unlabeled'}`",
        f"- Generated: `{report['generated_at']}`",
        f"- Selected repositories: {', '.join(report.get('selected_repo_ids') or []) or 'none'}",
        "",
        "## Summary",
        "",
    ]
    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    for key in [
        "sources",
        "classified_lanes",
        "product_controlled",
        "operator_guided",
        "external_dependency",
        "not_provided",
        "blocking",
    ]:
        lines.append(f"- {key}: `{summary.get(key, 0)}`")
    lines.extend(["", "## Reduction Actions", ""])
    for action in report.get("reduction_actions") or []:
        lines.append(f"- `{action['priority']}` `{action['category']}`: {action['action']}")
    lines.extend(["", "## Classified Lanes", ""])
    for lane in report.get("classified_lanes") or []:
        lines.append(
            f"- `{lane['category']}` `{lane['status']}` {lane['id']}: {lane.get('rationale', '')}"
        )
    lines.extend(["", "## Sources", ""])
    for source in report.get("sources") or []:
        lines.append(f"- `{source['id']}` `{source['status']}` {source.get('source_path') or 'not provided'}")
    lines.extend(["", "## Limitations", ""])
    for limitation in report.get("limitations") or []:
        lines.append(f"- {limitation}")
    lines.append("")
    return "\n".join(lines)


def write_report(root: Path, report: dict[str, Any], output_json: str | None, output_markdown: str | None) -> tuple[Path | None, Path | None]:
    json_path = _resolve_path(output_json, root) if output_json else None
    markdown_path = _resolve_path(output_markdown, root) if output_markdown else None
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, markdown_path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Classify warning lanes from random repository release evidence.")
    parser.add_argument("--multi-repo-diagnosis-json")
    parser.add_argument("--full-chain-json")
    parser.add_argument("--release-rehearsal-json")
    parser.add_argument("--real-external-host-trial-json")
    parser.add_argument("--output-json")
    parser.add_argument("--output-markdown")
    parser.add_argument("--generated-at")
    parser.add_argument("--label", default="random-repo-warning-lane-reduction")
    parser.add_argument("--version-label")
    parser.add_argument("--commit")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path.cwd()
    report = build_report(args, root)
    write_report(root, report, args.output_json, args.output_markdown)
    print(json.dumps({"status": report["status"], "summary": report["summary"]}, sort_keys=True))
    return 0 if report["status"] != STATUS_BLOCKING else 2


if __name__ == "__main__":
    raise SystemExit(main())
