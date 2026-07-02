from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
from pathlib import Path
import re
import sys
from typing import Any


SCHEMA_VERSION = 1
STATUS_PASS = "pass"
STATUS_WARNING = "warning"
STATUS_BLOCKING = "blocking"
STATUS_NOT_PROVIDED = "not_provided"
STATUS_UNKNOWN = "unknown"
NON_CLEAN_STATUSES = {
    "blocking",
    "caution",
    "failed",
    "failure",
    "incomplete",
    "known_limitation",
    "missing",
    "not_provided",
    "operator_guided",
    "pause",
    "unknown",
    "warning",
}
BLOCKING_STATUSES = {"blocking", "failed", "failure", "error"}
SECRET_KEY_PATTERN = re.compile(r"(token|secret|password|credential|api[_-]?key|private[_-]?key)", re.IGNORECASE)
RAW_SECRET_VALUE_PATTERN = re.compile(
    r"(ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|glpat-[A-Za-z0-9_-]+|sk-[A-Za-z0-9_-]+|xox[baprs]-[A-Za-z0-9-]+)",
    re.IGNORECASE,
)
LOCAL_PATH_PATTERN = re.compile(r"([a-zA-Z]:\\|/Users/|/home/|/var/|/tmp/|\\\\)")


def _resolve_path(path: str | None, root: Path) -> Path | None:
    if not path:
        return None
    candidate = Path(path)
    return candidate if candidate.is_absolute() else root / candidate


def _display_path(path: Path | None, root: Path) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name


def _bounded_text(value: Any, limit: int = 500) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if len(text) > limit:
        return text[: limit - 1].rstrip() + "..."
    return text


def sanitize(value: Any, *, key: str | None = None) -> Any:
    if key and SECRET_KEY_PATTERN.search(key):
        return "[redacted]"
    if isinstance(value, dict):
        return {str(k): sanitize(v, key=str(k)) for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, list):
        return [sanitize(item) for item in value[:20]]
    if isinstance(value, str):
        if RAW_SECRET_VALUE_PATTERN.search(value):
            return "[redacted]"
        if LOCAL_PATH_PATTERN.search(value):
            return "[local_path_redacted]"
        return _bounded_text(value)
    return value


def _status(value: Any, default: str = STATUS_UNKNOWN) -> str:
    if value is None:
        return default
    normalized = str(value).strip().lower().replace(" ", "_").replace("-", "_")
    if normalized in {"passed", "success", "succeeded", "ok", "clean", "continue"}:
        return STATUS_PASS
    if normalized in {"warn", "warnings", "caution", "needs_review"}:
        return STATUS_WARNING
    if normalized in {"failed", "failure", "error", "blocked"}:
        return STATUS_BLOCKING
    return normalized or default


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return None, f"Failed to read {path}: {exc}"
    except json.JSONDecodeError as exc:
        return None, f"Failed to parse JSON from {path}: {exc}"
    if not isinstance(data, dict):
        return None, f"Expected JSON object in {path}."
    return data, None


def _load_source(source_id: str, label: str, path_text: str | None, root: Path) -> tuple[dict[str, Any], dict[str, Any] | None]:
    path = _resolve_path(path_text, root)
    source = {
        "id": source_id,
        "label": label,
        "source_path": _display_path(path, root),
        "status": STATUS_NOT_PROVIDED,
        "warnings": [],
    }
    if path is None:
        source["warnings"] = ["source_not_provided"]
        return source, None
    if not path.exists():
        source["status"] = STATUS_WARNING
        source["warnings"] = [f"source_missing:{_display_path(path, root)}"]
        return source, None
    data, error = _read_json(path)
    if error:
        source["status"] = STATUS_WARNING
        source["warnings"] = [error]
        return source, None
    source["status"] = STATUS_PASS
    return source, data


def summarize_release(data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"status": STATUS_NOT_PROVIDED}
    required = data.get("required_gates") if isinstance(data.get("required_gates"), list) else []
    advisory = data.get("advisory_signals") if isinstance(data.get("advisory_signals"), list) else []
    missing = data.get("missing_inputs") if isinstance(data.get("missing_inputs"), list) else []
    return {
        "status": _status(data.get("overall_status")),
        "required_gates": [{"id": item.get("id"), "status": _status(item.get("status"))} for item in required if isinstance(item, dict)],
        "advisory_signals": [{"id": item.get("id"), "status": _status(item.get("status"))} for item in advisory if isinstance(item, dict)],
        "missing_input_count": len(missing),
    }


def summarize_hosted(data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"status": STATUS_NOT_PROVIDED}
    lanes = data.get("lanes") if isinstance(data.get("lanes"), list) else []
    return {
        "status": _status(data.get("overall_status") or data.get("status")),
        "public_walkthrough_status": _status(data.get("public_walkthrough_status"), STATUS_NOT_PROVIDED),
        "operator_guided_count": sum(1 for lane in lanes if isinstance(lane, dict) and _status(lane.get("status")) == "operator_guided"),
        "known_limitation_count": sum(1 for lane in lanes if isinstance(lane, dict) and _status(lane.get("status")) == "known_limitation"),
    }


def summarize_benchmark_trend(data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"status": STATUS_NOT_PROVIDED}
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    return {
        "status": _status(data.get("status")),
        "repositories": int(summary.get("repositories") or summary.get("pool_repositories") or 0),
        "covered_repositories": int(summary.get("covered_repositories") or 0),
        "missing_repositories": int(summary.get("missing_repositories") or 0),
        "regressed": int(summary.get("regressed") or 0),
        "operationally_blocked": int(summary.get("operationally_blocked") or 0),
        "recommended_follow_up": sanitize(data.get("recommended_follow_up") or []),
    }


def summarize_handoff(data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"status": STATUS_NOT_PROVIDED}
    workspace = data.get("workspace") if isinstance(data.get("workspace"), dict) else {}
    repo = data.get("repository_scope") if isinstance(data.get("repository_scope"), dict) else {}
    sections = data.get("sections") if isinstance(data.get("sections"), dict) else {}
    return {
        "status": _status(data.get("overall_status")),
        "workspace": sanitize(workspace),
        "repository_scope": sanitize(repo),
        "section_statuses": {key: _status(value.get("status")) for key, value in sections.items() if isinstance(value, dict)},
    }


def summarize_external_install(data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"status": STATUS_NOT_PROVIDED}
    lanes = data.get("lanes") if isinstance(data.get("lanes"), list) else []
    host = data.get("external_host") if isinstance(data.get("external_host"), dict) else {}
    package = data.get("package_identity") if isinstance(data.get("package_identity"), dict) else {}
    return {
        "status": _status(data.get("status")),
        "generated_at": data.get("generated_at"),
        "host_class": sanitize(host.get("host_class")),
        "customer_controlled": host.get("is_customer_controlled"),
        "package_label": package.get("package_label"),
        "version_label": package.get("version_label"),
        "lane_statuses": {
            str(lane.get("id")): _status(lane.get("status"))
            for lane in lanes
            if isinstance(lane, dict) and lane.get("id")
        },
        "redaction_finding_count": len(data.get("redaction_findings") if isinstance(data.get("redaction_findings"), list) else []),
    }


def summarize_real_continuity(data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"status": STATUS_NOT_PROVIDED}
    lanes = data.get("continuity_lanes") if isinstance(data.get("continuity_lanes"), list) else []
    scope = data.get("scratch_scope") if isinstance(data.get("scratch_scope"), dict) else {}
    integrity = data.get("integrity") if isinstance(data.get("integrity"), dict) else {}
    return {
        "status": _status(data.get("status")),
        "generated_at": data.get("generated_at"),
        "scratch_only": scope.get("scratch_only"),
        "restore_matches_source": integrity.get("restore_matches_source"),
        "source_record_count": integrity.get("source_record_count"),
        "restored_record_count": integrity.get("restored_record_count"),
        "lane_statuses": {
            str(lane.get("id")): _status(lane.get("status"))
            for lane in lanes
            if isinstance(lane, dict) and lane.get("id")
        },
        "blocker_count": len(data.get("blockers") if isinstance(data.get("blockers"), list) else []),
        "redaction_finding_count": len(data.get("redaction_findings") if isinstance(data.get("redaction_findings"), list) else []),
    }


def summarize_license(data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"status": STATUS_NOT_PROVIDED}
    tier = data.get("tier")
    return {
        "status": STATUS_PASS if tier else STATUS_WARNING,
        "tier": tier,
        "customer_label": sanitize(data.get("customer_label")),
        "deployment_scope": sanitize(data.get("deployment_scope") if isinstance(data.get("deployment_scope"), dict) else {}),
        "support": sanitize(data.get("support") if isinstance(data.get("support"), dict) else {}),
        "runtime_enforcement": sanitize(data.get("runtime_enforcement") if isinstance(data.get("runtime_enforcement"), dict) else {}),
    }


def _overall_status(sections: dict[str, dict[str, Any]], source_warnings: list[str]) -> str:
    statuses = {_status(section.get("status"), STATUS_NOT_PROVIDED) for section in sections.values()}
    if statuses & BLOCKING_STATUSES:
        return STATUS_BLOCKING
    if source_warnings or statuses & NON_CLEAN_STATUSES:
        return STATUS_WARNING
    return STATUS_PASS


def build_report(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    source_specs = [
        ("release_evidence", "Release evidence", args.release_evidence_json, summarize_release),
        ("hosted_readiness", "Hosted/operator readiness", args.hosted_readiness_json, summarize_hosted),
        ("benchmark_trend", "Benchmark trend", args.benchmark_trend_json, summarize_benchmark_trend),
        ("coverage_rehearsal", "Benchmark coverage rehearsal", args.coverage_rehearsal_json, summarize_benchmark_trend),
        ("team_handoff", "Team handoff", args.team_handoff_json, summarize_handoff),
        ("external_install_evidence", "External self-hosted install evidence", args.external_install_evidence_json, summarize_external_install),
        ("real_continuity_rehearsal", "Real backup/restore/upgrade rehearsal", args.real_continuity_rehearsal_json, summarize_real_continuity),
        ("readiness_history", "Readiness history", args.readiness_history_index_json, lambda data: {"status": _status((data.get("entries") or [{}])[-1].get("status"), STATUS_NOT_PROVIDED), "entry_count": len(data.get("entries") or [])} if data else {"status": STATUS_NOT_PROVIDED}),
        ("license_support", "License/support boundary", args.license_support_json, summarize_license),
    ]
    sources: dict[str, dict[str, Any]] = {}
    sections: dict[str, dict[str, Any]] = {}
    source_warnings: list[str] = []
    for source_id, label, path_text, summarizer in source_specs:
        source, data = _load_source(source_id, label, path_text, root)
        sources[source_id] = source
        if source.get("warnings"):
            source_warnings.extend(f"{source_id}:{warning}" for warning in source["warnings"])
        sections[source_id] = sanitize(summarizer(data))

    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": args.generated_at or datetime.now(UTC).isoformat(),
        "label": args.label,
        "customer": args.customer,
        "repository": args.repository,
        "workspace": args.workspace,
        "deployment_mode": args.deployment_mode,
        "recommended_tier": args.recommended_tier,
        "tier_rationale": args.tier_rationale,
        "open_commercial_questions": [item for item in args.open_commercial_question],
        "overall_status": _overall_status(sections, source_warnings),
        "sources": sources,
        "sections": sections,
        "limitations": [
            "This report summarizes bounded DecisionAtlas evidence; it is not a general security audit.",
            "Warnings, operator-guided lanes, known limitations, and omitted optional evidence are preserved.",
            "External/customer-host readiness is only claimed when sanitized external install evidence is supplied.",
            "Tested backup/restore/upgrade readiness is only claimed when real scratch continuity rehearsal evidence is supplied.",
            "Do not attach secrets, raw private repository contents, raw model output, or unbounded local logs.",
        ],
    }
    return sanitize(report)


def _markdown_cell(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, (dict, list)):
        text = json.dumps(value, sort_keys=True, ensure_ascii=False)
    else:
        text = str(value)
    return text.replace("|", "\\|").replace("\n", "<br>") or "-"


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Code Decision Audit Report",
        "",
        f"- Label: `{report.get('label')}`",
        f"- Generated at: `{report.get('generated_at')}`",
        f"- Customer / team: `{report.get('customer') or 'not_provided'}`",
        f"- Repository: `{report.get('repository') or 'not_provided'}`",
        f"- Workspace: `{report.get('workspace') or 'not_provided'}`",
        f"- Deployment mode: `{report.get('deployment_mode')}`",
        f"- Overall status: `{report.get('overall_status')}`",
        "",
        "## Evidence Summary",
        "",
        "| Evidence | Status | Summary |",
        "| --- | --- | --- |",
    ]
    sections = report.get("sections") if isinstance(report.get("sections"), dict) else {}
    for key in sorted(sections):
        section = sections[key] if isinstance(sections[key], dict) else {}
        compact = {k: v for k, v in section.items() if k != "recommended_follow_up"}
        lines.append(f"| {_markdown_cell(key)} | {_markdown_cell(section.get('status'))} | {_markdown_cell(compact)} |")

    lines.extend(["", "## Customer-Facing Findings", ""])
    trend = sections.get("benchmark_trend") if isinstance(sections.get("benchmark_trend"), dict) else {}
    coverage = sections.get("coverage_rehearsal") if isinstance(sections.get("coverage_rehearsal"), dict) else {}
    lines.extend(
        [
            f"- Benchmark coverage: `{coverage.get('covered_repositories', 0)}/{coverage.get('repositories', 0)}` repositories covered.",
            f"- Benchmark regressions: `{trend.get('regressed', 0)}` trend regressions, `{coverage.get('regressed', 0)}` coverage rehearsal regressions.",
            f"- Operational blockers: `{trend.get('operationally_blocked', 0)}` trend blockers, `{coverage.get('operationally_blocked', 0)}` coverage blockers.",
            f"- External install evidence: `{(sections.get('external_install_evidence') if isinstance(sections.get('external_install_evidence'), dict) else {}).get('status', STATUS_NOT_PROVIDED)}`.",
            f"- Real continuity evidence: `{(sections.get('real_continuity_rehearsal') if isinstance(sections.get('real_continuity_rehearsal'), dict) else {}).get('status', STATUS_NOT_PROVIDED)}`.",
            "- Non-clean states are disclosure items, not hidden passes.",
        ]
    )

    lines.extend(["", "## Recommended Next Actions", ""])
    follow_up: list[str] = []
    for key in ("benchmark_trend", "coverage_rehearsal"):
        section = sections.get(key) if isinstance(sections.get(key), dict) else {}
        follow_up.extend(str(item) for item in section.get("recommended_follow_up") or [])
    if report.get("overall_status") != STATUS_PASS:
        follow_up.append("Resolve or explicitly accept warning/operator-guided/not-provided evidence before claiming a clean customer handoff.")
    if not follow_up:
        follow_up.append("Current supplied evidence is clean for this bounded audit report.")
    for item in dict.fromkeys(follow_up):
        lines.append(f"- {item}")

    lines.extend(["", "## Commercial Fit", ""])
    lines.append(f"- Recommended tier: `{report.get('recommended_tier') or 'not_provided'}`")
    lines.append(f"- Rationale: {report.get('tier_rationale') or 'not_provided'}")
    questions = report.get("open_commercial_questions") or []
    if questions:
        lines.extend(["", "Open questions:"])
        for question in questions:
            lines.append(f"- {question}")

    lines.extend(["", "## Source Evidence", "", "| Source | Status | Path | Warnings |", "| --- | --- | --- | --- |"])
    for key, source in sorted((report.get("sources") or {}).items()):
        if isinstance(source, dict):
            lines.append(
                f"| {_markdown_cell(source.get('label') or key)} | {_markdown_cell(source.get('status'))} | "
                f"{_markdown_cell(source.get('source_path'))} | {_markdown_cell(source.get('warnings'))} |"
            )

    lines.extend(["", "## Limitations", ""])
    for item in report.get("limitations") or []:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_markdown(path: Path, markdown: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a customer-readable Code Decision Audit report.")
    parser.add_argument("--output-json", default=".tmp/code-decision-audit-report.json")
    parser.add_argument("--output-markdown", default=".tmp/code-decision-audit-report.md")
    parser.add_argument("--generated-at")
    parser.add_argument("--label", default="code-decision-audit")
    parser.add_argument("--customer")
    parser.add_argument("--repository")
    parser.add_argument("--workspace")
    parser.add_argument("--deployment-mode", default="Team Self-hosted evaluation")
    parser.add_argument("--recommended-tier", default="Team Self-hosted")
    parser.add_argument("--tier-rationale", default="Current evidence supports a bounded self-hosted pilot when warning states are disclosed.")
    parser.add_argument("--open-commercial-question", action="append", default=[])
    parser.add_argument("--release-evidence-json")
    parser.add_argument("--hosted-readiness-json")
    parser.add_argument("--benchmark-trend-json")
    parser.add_argument("--coverage-rehearsal-json")
    parser.add_argument("--team-handoff-json")
    parser.add_argument("--external-install-evidence-json")
    parser.add_argument("--real-continuity-rehearsal-json")
    parser.add_argument("--readiness-history-index-json")
    parser.add_argument("--license-support-json")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    report = build_report(args, root)
    output_json = _resolve_path(args.output_json, root)
    output_markdown = _resolve_path(args.output_markdown, root)
    assert output_json is not None
    assert output_markdown is not None
    _write_json(output_json, report)
    _write_markdown(output_markdown, render_markdown(report))
    print(f"Code Decision Audit JSON written to {output_json}")
    print(f"Code Decision Audit Markdown written to {output_markdown}")
    print(f"Overall status: {report['overall_status']}")
    return 1 if report["overall_status"] == STATUS_BLOCKING else 0


if __name__ == "__main__":
    sys.exit(main())
