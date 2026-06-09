from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
STATUS_PASS = "pass"
STATUS_WARNING = "warning"
STATUS_BLOCKING = "blocking"
STATUS_NOT_PROVIDED = "not_provided"
STATUS_OPERATOR_GUIDED = "operator_guided"
STATUS_KNOWN_LIMITATION = "known_limitation"
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
LOCAL_PATH_PATTERN = re.compile(r"(^[a-zA-Z]:\\|^/Users/|^/home/|^/var/|^/tmp/|\\\\)")


def _git_commit(root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


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


def _bounded_text(value: Any, limit: int = 240) -> str | None:
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
        return _bounded_text(value, 500)
    return value


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


def summarize_release(data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"status": STATUS_NOT_PROVIDED}
    required = data.get("required_gates") if isinstance(data.get("required_gates"), list) else []
    advisory = data.get("advisory_signals") if isinstance(data.get("advisory_signals"), list) else []
    missing = data.get("missing_inputs") if isinstance(data.get("missing_inputs"), list) else []
    warnings = data.get("warnings") if isinstance(data.get("warnings"), list) else []
    return {
        "status": _status(data.get("overall_status")),
        "generated_at": data.get("generated_at"),
        "required_gates": [
            {"id": item.get("id"), "label": item.get("label"), "status": _status(item.get("status"))}
            for item in required
            if isinstance(item, dict)
        ],
        "advisory_signals": [
            {"id": item.get("id"), "label": item.get("label"), "status": _status(item.get("status"))}
            for item in advisory
            if isinstance(item, dict)
        ],
        "warning_count": len(warnings),
        "missing_input_count": len(missing),
    }


def summarize_hosted(data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"status": STATUS_NOT_PROVIDED, "public_walkthrough_status": STATUS_NOT_PROVIDED}
    lanes = data.get("lanes") if isinstance(data.get("lanes"), list) else []
    blockers = data.get("blockers") if isinstance(data.get("blockers"), list) else []
    warnings = data.get("warnings") if isinstance(data.get("warnings"), list) else []
    return {
        "status": _status(data.get("overall_status") or data.get("status")),
        "generated_at": data.get("generated_at"),
        "public_walkthrough_status": _status(data.get("public_walkthrough_status"), STATUS_NOT_PROVIDED),
        "lane_statuses": {
            str(lane.get("id")): _status(lane.get("status"))
            for lane in lanes
            if isinstance(lane, dict) and lane.get("id")
        },
        "warning_count": len(warnings),
        "blocker_count": len(blockers),
        "operator_guided_count": sum(1 for lane in lanes if isinstance(lane, dict) and _status(lane.get("status")) == STATUS_OPERATOR_GUIDED),
        "known_limitation_count": sum(1 for lane in lanes if isinstance(lane, dict) and _status(lane.get("status")) == STATUS_KNOWN_LIMITATION),
    }


def summarize_benchmark(data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"status": STATUS_NOT_PROVIDED}
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    regressed = int(summary.get("regressed") or 0)
    operationally_blocked = int(summary.get("operationally_blocked") or 0)
    return {
        "status": STATUS_WARNING if regressed or operationally_blocked else STATUS_PASS,
        "generated_at": data.get("generated_at"),
        "comparison_type": data.get("comparison_type"),
        "repositories": int(summary.get("repositories") or 0),
        "improved": int(summary.get("improved") or 0),
        "regressed": regressed,
        "operationally_blocked": operationally_blocked,
        "release_evidence_ready": summary.get("release_evidence_ready"),
    }


def summarize_benchmark_trend(data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"status": STATUS_NOT_PROVIDED}
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    return {
        "status": _status(data.get("status")),
        "generated_at": data.get("generated_at"),
        "label": data.get("label"),
        "repositories": int(summary.get("repositories") or 0),
        "covered_repositories": int(summary.get("covered_repositories") or 0),
        "missing_repositories": int(summary.get("missing_repositories") or 0),
        "not_provided_repositories": int(summary.get("not_provided_repositories") or 0),
        "operator_guided_repositories": int(summary.get("operator_guided_repositories") or 0),
        "regressed": int(summary.get("regressed") or 0),
        "improved": int(summary.get("improved") or 0),
        "operationally_blocked": int(summary.get("operationally_blocked") or 0),
        "missing_from_current": int(summary.get("missing_from_current") or 0),
        "recommended_follow_up": sanitize(data.get("recommended_follow_up") or []),
    }


def summarize_readiness_history(data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"status": STATUS_NOT_PROVIDED}
    entries = data.get("entries") if isinstance(data.get("entries"), list) else []
    latest = entries[-1] if entries and isinstance(entries[-1], dict) else {}
    return {
        "status": _status(latest.get("status"), STATUS_NOT_PROVIDED) if latest else STATUS_NOT_PROVIDED,
        "entry_count": len(entries),
        "latest_entry_id": latest.get("entry_id"),
        "latest_label": latest.get("label"),
        "latest_counts": sanitize(latest.get("counts") or {}),
        "latest_family_statuses": sanitize(latest.get("family_statuses") or {}),
    }


def summarize_package(data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"status": STATUS_NOT_PROVIDED}
    lanes = data.get("non_pass_lanes") if isinstance(data.get("non_pass_lanes"), list) else []
    return {
        "status": _status(data.get("status")),
        "generated_at": data.get("generated_at"),
        "package_label": data.get("package_label"),
        "version_label": data.get("version_label"),
        "checked_file_count": data.get("checked_file_count"),
        "blocker_count": len(data.get("blockers") if isinstance(data.get("blockers"), list) else []),
        "non_pass_lanes": [
            {"id": lane.get("id"), "label": lane.get("label"), "status": _status(lane.get("status")), "reason": _bounded_text(lane.get("reason"))}
            for lane in lanes
            if isinstance(lane, dict)
        ],
    }


def summarize_license_support(data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"status": STATUS_NOT_PROVIDED}
    support = data.get("support") if isinstance(data.get("support"), dict) else {}
    deployment = data.get("deployment_scope") if isinstance(data.get("deployment_scope"), dict) else {}
    upgrade = data.get("upgrade") if isinstance(data.get("upgrade"), dict) else {}
    runtime = data.get("runtime_enforcement") if isinstance(data.get("runtime_enforcement"), dict) else {}
    tier = data.get("tier")
    return {
        "status": STATUS_PASS if tier else STATUS_WARNING,
        "schema_version": data.get("schema_version"),
        "customer_label": data.get("customer_label"),
        "tier": tier,
        "deployment_scope": sanitize(deployment),
        "support_start": support.get("support_start"),
        "support_end": support.get("support_end"),
        "support_channel": support.get("support_channel"),
        "upgrade_channel": upgrade.get("upgrade_channel"),
        "runtime_enforcement_enabled": runtime.get("enabled"),
        "boundary": "documented_non_enforced",
    }


def summarize_public_import(data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"status": STATUS_NOT_PROVIDED}
    repository = data.get("repository") if isinstance(data.get("repository"), dict) else {}
    setup = data.get("setup") if isinstance(data.get("setup"), dict) else {}
    import_job = data.get("import_job") if isinstance(data.get("import_job"), dict) else {}
    extraction = import_job.get("summary", {}).get("extraction_summary", {}) if isinstance(import_job.get("summary"), dict) else {}
    return {
        "status": STATUS_PASS if setup.get("benchmark_ready") is True else _status(import_job.get("status") or setup.get("outcome") or data.get("status") or data.get("result")),
        "repository": repository.get("repo") or data.get("repo") or data.get("repo_full_name"),
        "workspace": import_job.get("workspace_slug") or repository.get("workspace_slug") or data.get("workspace_slug"),
        "setup_outcome": setup.get("outcome"),
        "import_status": import_job.get("status"),
        "benchmark_ready": setup.get("benchmark_ready"),
        "imported_count": import_job.get("imported_count"),
        "full_extraction_requests": extraction.get("full_extraction_requests"),
        "created_candidates": extraction.get("created_candidates"),
    }


def summarize_clean_install(data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"status": STATUS_NOT_PROVIDED}
    evidence = data.get("source_evidence") if isinstance(data.get("source_evidence"), list) else []
    blockers = data.get("blockers") if isinstance(data.get("blockers"), list) else []
    return {
        "status": _status(data.get("status")),
        "generated_at": data.get("generated_at"),
        "label": data.get("label"),
        "package_path": sanitize(data.get("package_path")),
        "clean_workspace_path": sanitize(data.get("clean_workspace_path")),
        "clean_package_path": sanitize(data.get("clean_package_path")),
        "warning_count": data.get("warning_count"),
        "blocker_count": len(blockers),
        "evidence_family_statuses": {
            str(item.get("id")): _status(item.get("status"))
            for item in evidence
            if isinstance(item, dict) and item.get("id")
        },
        "recommended_next_actions": sanitize(data.get("recommended_next_actions") or []),
    }


def summarize_audit(data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"status": STATUS_NOT_PROVIDED, "events": []}
    raw_events = data.get("events") if isinstance(data.get("events"), list) else data.get("audit_history")
    events = raw_events if isinstance(raw_events, list) else []
    compact = []
    for event in events[:10]:
        if not isinstance(event, dict):
            continue
        compact.append(
            {
                "actor": event.get("actor_username") or event.get("actor") or event.get("username"),
                "role": event.get("actor_role") or event.get("role"),
                "target_type": event.get("target_type"),
                "action": event.get("action"),
                "previous_state": event.get("previous_state"),
                "new_state": event.get("new_state"),
                "rationale": _bounded_text(event.get("rationale")),
                "timestamp": event.get("timestamp") or event.get("created_at"),
            }
        )
    return {"status": STATUS_PASS if compact else STATUS_NOT_PROVIDED, "event_count": len(events), "events": sanitize(compact)}


def _section_status(summary: dict[str, Any]) -> str:
    return _status(summary.get("status"), STATUS_NOT_PROVIDED)


def _overall_status(sections: dict[str, dict[str, Any]]) -> str:
    statuses = {_section_status(section) for section in sections.values()}
    if statuses & BLOCKING_STATUSES:
        return STATUS_BLOCKING
    if statuses & NON_CLEAN_STATUSES:
        return STATUS_WARNING
    return STATUS_PASS


def build_report(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    source_specs = [
        ("release_evidence", "Release evidence", args.release_evidence_json, summarize_release),
        ("hosted_readiness", "Hosted/operator readiness", args.hosted_readiness_json, summarize_hosted),
        ("benchmark_comparison", "Benchmark comparison", args.benchmark_comparison_json, summarize_benchmark),
        ("benchmark_trend", "Benchmark trend evidence", args.benchmark_trend_json, summarize_benchmark_trend),
        ("readiness_history", "Readiness evidence history", args.readiness_history_index_json, summarize_readiness_history),
        ("self_hosted_package", "Self-hosted package verification", args.package_verification_json, summarize_package),
        ("clean_install_rehearsal", "Clean self-hosted install rehearsal", args.clean_install_rehearsal_json, summarize_clean_install),
        ("license_support", "License and support boundary", args.license_support_json, summarize_license_support),
        ("public_github_import", "Public GitHub import rehearsal", args.public_github_import_json, summarize_public_import),
        ("review_audit", "Review audit history", args.audit_history_json, summarize_audit),
    ]
    sources: dict[str, dict[str, Any]] = {}
    sections: dict[str, dict[str, Any]] = {}
    for source_id, label, source_path, summarizer in source_specs:
        source, data = _load_source(source_id, label, source_path, root)
        sources[source_id] = source
        sections[source_id] = sanitize(summarizer(data))

    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": args.generated_at or datetime.now(UTC).isoformat(),
        "label": args.label,
        "version_label": args.version_label,
        "commit": args.commit or _git_commit(root) or "unknown",
        "audience": args.audience,
        "workspace": {
            "id": args.workspace_id,
            "slug": args.workspace_slug,
            "label": args.workspace_label,
        },
        "repository_scope": {
            "provider": args.repository_provider,
            "access_mode": args.repository_access_mode,
            "repository": args.repository,
            "authorization_status": args.repository_authorization_status,
        },
        "overall_status": _overall_status(sections),
        "sources": sources,
        "sections": sections,
        "limitations": [
            "This report is a bounded handoff snapshot, not a live dashboard.",
            "Missing, operator-guided, known-limitation, warning, and blocking states are preserved.",
            "Secrets, raw tokens, private repository dumps, and unbounded local-only paths are excluded.",
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
    workspace = report.get("workspace") if isinstance(report.get("workspace"), dict) else {}
    repo = report.get("repository_scope") if isinstance(report.get("repository_scope"), dict) else {}
    lines = [
        "# DecisionAtlas Team Handoff Report",
        "",
        f"- Label: `{report.get('label')}`",
        f"- Generated at: `{report.get('generated_at')}`",
        f"- Version: `{report.get('version_label') or '-'}`",
        f"- Commit: `{report.get('commit')}`",
        f"- Audience: `{report.get('audience')}`",
        f"- Overall status: `{report.get('overall_status')}`",
        "",
        "## Workspace and Repository Scope",
        "",
        f"- Workspace: `{workspace.get('slug') or workspace.get('id') or workspace.get('label') or 'not_provided'}`",
        f"- Repository: `{repo.get('repository') or 'not_provided'}`",
        f"- Provider: `{repo.get('provider') or 'not_provided'}`",
        f"- Access mode: `{repo.get('access_mode') or 'not_provided'}`",
        f"- Authorization status: `{repo.get('authorization_status') or 'not_provided'}`",
        "",
        "## Evidence Status",
        "",
        "| Evidence | Status | Summary |",
        "| --- | --- | --- |",
    ]
    sections = report.get("sections") if isinstance(report.get("sections"), dict) else {}
    for key in sorted(sections):
        summary = sections[key] if isinstance(sections[key], dict) else {}
        compact = {k: v for k, v in summary.items() if k != "events"}
        lines.append(f"| {_markdown_cell(key)} | {_markdown_cell(summary.get('status'))} | {_markdown_cell(compact)} |")

    audit = sections.get("review_audit") if isinstance(sections.get("review_audit"), dict) else {}
    events = audit.get("events") if isinstance(audit.get("events"), list) else []
    lines.extend(["", "## Review and Audit Activity", ""])
    if events:
        lines.extend(["| Actor | Role | Target | Action | State | Rationale | Time |", "| --- | --- | --- | --- | --- | --- | --- |"])
        for event in events:
            if not isinstance(event, dict):
                continue
            state = f"{event.get('previous_state') or '-'} -> {event.get('new_state') or '-'}"
            lines.append(
                "| "
                + " | ".join(
                    _markdown_cell(value)
                    for value in (
                        event.get("actor"),
                        event.get("role"),
                        event.get("target_type"),
                        event.get("action"),
                        state,
                        event.get("rationale"),
                        event.get("timestamp"),
                    )
                )
                + " |"
            )
    else:
        lines.append("- No audit history source was provided.")

    lines.extend(["", "## Source Evidence", "", "| Source | Status | Path | Warnings |", "| --- | --- | --- | --- |"])
    sources = report.get("sources") if isinstance(report.get("sources"), dict) else {}
    for key in sorted(sources):
        source = sources[key] if isinstance(sources[key], dict) else {}
        lines.append(
            f"| {_markdown_cell(source.get('label') or key)} | {_markdown_cell(source.get('status'))} | "
            f"{_markdown_cell(source.get('source_path'))} | {_markdown_cell(source.get('warnings'))} |"
        )

    lines.extend(["", "## Limitations and Next Actions", ""])
    for item in report.get("limitations") or []:
        lines.append(f"- {item}")
    if report.get("overall_status") != STATUS_PASS:
        lines.append("- Resolve or explicitly accept non-clean evidence states before using this as a clean customer handoff.")
    else:
        lines.append("- Current supplied evidence is clean for this bounded handoff snapshot.")
    lines.append("")
    return "\n".join(lines)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_markdown(path: Path, markdown: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate DecisionAtlas team handoff JSON and Markdown reports.")
    parser.add_argument("--output-json", default=".tmp/team-handoff-report.json")
    parser.add_argument("--output-markdown", default=".tmp/team-handoff-report.md")
    parser.add_argument("--generated-at")
    parser.add_argument("--label", default="team-handoff")
    parser.add_argument("--version-label")
    parser.add_argument("--commit")
    parser.add_argument("--audience", default="operator")
    parser.add_argument("--workspace-id")
    parser.add_argument("--workspace-slug")
    parser.add_argument("--workspace-label")
    parser.add_argument("--repository-provider")
    parser.add_argument("--repository-access-mode")
    parser.add_argument("--repository")
    parser.add_argument("--repository-authorization-status")
    parser.add_argument("--release-evidence-json")
    parser.add_argument("--hosted-readiness-json")
    parser.add_argument("--benchmark-comparison-json")
    parser.add_argument("--benchmark-trend-json")
    parser.add_argument("--readiness-history-index-json")
    parser.add_argument("--package-verification-json")
    parser.add_argument("--clean-install-rehearsal-json")
    parser.add_argument("--license-support-json")
    parser.add_argument("--public-github-import-json")
    parser.add_argument("--audit-history-json")
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
    print(f"Team handoff JSON written to {output_json}")
    print(f"Team handoff Markdown written to {output_markdown}")
    print(f"Overall status: {report['overall_status']}")
    return 1 if report["overall_status"] == STATUS_BLOCKING else 0


if __name__ == "__main__":
    sys.exit(main())
