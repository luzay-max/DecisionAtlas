from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import collect_readiness_evidence_history as readiness_history  # noqa: E402


SCHEMA_VERSION = 1
STATUS_PASS = "pass"
STATUS_WARNING = "warning"
STATUS_BLOCKING = "blocking"
STATUS_OPERATOR_GUIDED = "operator_guided"
STATUS_NOT_PROVIDED = "not_provided"
STATUS_UNKNOWN = "unknown"

PASS_STATUSES = {"pass", "passed", "ok", "success", "succeeded", "clean", "ready", "true"}
WARNING_STATUSES = {"warning", "warn", "caution", "known_limitation", "needs_review", "manual_check"}
BLOCKING_STATUSES = {"blocking", "blocked", "failed", "failure", "error", "false", "local_stack_failure"}
NON_PASS_STATUSES = {STATUS_WARNING, STATUS_BLOCKING, STATUS_OPERATOR_GUIDED, STATUS_NOT_PROVIDED, STATUS_UNKNOWN}

SECRET_VALUE_PATTERNS = [
    (
        "token_like_value",
        re.compile(
            r"(ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|glpat-[A-Za-z0-9_-]+|sk-[A-Za-z0-9_-]+|xox[baprs]-[A-Za-z0-9-]+)",
            re.IGNORECASE,
        ),
    ),
    (
        "env_secret_assignment",
        re.compile(
            r"\b[A-Z0-9_]*(TOKEN|SECRET|PASSWORD|API_KEY|PRIVATE_KEY|DATABASE_URL)[A-Z0-9_]*\s*=\s*[^\s\"']+",
            re.IGNORECASE,
        ),
    ),
    ("private_key_marker", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("raw_backup_marker", re.compile(r"(\bPGDMP\b|BEGIN DATABASE DUMP|COPY public\.|CREATE TABLE public\.)", re.IGNORECASE)),
    (
        "private_repo_snippet_marker",
        re.compile(
            r"(raw_private_repository|private_source_snippet|private_repo_snippet|BEGIN PRIVATE REPOSITORY CONTENT)",
            re.IGNORECASE,
        ),
    ),
]


def normalize_status(value: Any, default: str = STATUS_UNKNOWN) -> str:
    if isinstance(value, bool):
        return STATUS_PASS if value else STATUS_BLOCKING
    if value is None:
        return default
    normalized = str(value).strip().lower().replace(" ", "_").replace("-", "_")
    if normalized in PASS_STATUSES:
        return STATUS_PASS
    if normalized in WARNING_STATUSES:
        return STATUS_WARNING
    if normalized in BLOCKING_STATUSES:
        return STATUS_BLOCKING
    if normalized in {"operator", "operator_guided", "manual", "manual_required"}:
        return STATUS_OPERATOR_GUIDED
    if normalized in {"missing", "omitted", "not_provided", "not_available"}:
        return STATUS_NOT_PROVIDED
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
    if path is None or str(path) == "":
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


def _bounded(value: Any, limit: int = 500) -> Any:
    if isinstance(value, dict):
        return {str(key): _bounded(item, limit=limit) for key, item in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, list):
        return [_bounded(item, limit=limit) for item in value[:20]]
    if isinstance(value, str):
        text = value.strip()
        return text if len(text) <= limit else text[: limit - 1].rstrip() + "..."
    return value


def detect_sensitive_material(payload: Any) -> list[dict[str, Any]]:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    findings = []
    for finding_id, pattern in SECRET_VALUE_PATTERNS:
        if pattern.search(raw):
            findings.append({"id": finding_id, "status": STATUS_BLOCKING})
    return findings


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


def _source_summary(lane_id: str, label: str, path_text: str | None, root: Path) -> dict[str, Any]:
    path = _resolve_path(path_text, root)
    lane = {
        "id": lane_id,
        "label": label,
        "status": STATUS_NOT_PROVIDED,
        "source_path": _display_path(path, root),
        "summary": {"reason": "source_not_provided"},
        "warnings": [],
    }
    if path is None:
        return lane
    if not path.exists():
        lane["status"] = STATUS_WARNING
        lane["summary"] = {"reason": "source_missing"}
        lane["warnings"] = [f"source path does not exist: {_display_path(path, root)}"]
        return lane
    data, error = _read_json(path)
    if error or data is None:
        lane["status"] = STATUS_WARNING
        lane["summary"] = {"reason": "source_unreadable", "error": error}
        lane["warnings"] = [error or "source_unreadable"]
        return lane
    lane["status"] = _source_status(data)
    lane["summary"] = _compact_source_details(data)
    return lane


def _compact_source_details(data: dict[str, Any]) -> dict[str, Any]:
    details: dict[str, Any] = {}
    for key in (
        "generated_at",
        "label",
        "version_label",
        "commit",
        "status",
        "overall_status",
        "public_walkthrough_status",
        "package_label",
        "package_path",
        "evidence_type",
    ):
        if data.get(key) is not None:
            details[key] = data.get(key)
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    if summary:
        details["summary"] = {
            key: summary.get(key)
            for key in (
                "pass",
                "warning",
                "blocking",
                "missing_lanes",
                "operator_guided_lanes",
                "repositories",
                "regressed",
                "operationally_blocked",
            )
            if key in summary
        }
    blockers = data.get("blockers") if isinstance(data.get("blockers"), list) else []
    if blockers:
        details["blocker_count"] = len(blockers)
    return _bounded(details)


def _host_lane(host_input: dict[str, Any] | None, input_path: Path | None, root: Path) -> dict[str, Any]:
    if host_input is None:
        return {
            "id": "customer_host_template",
            "label": "Customer host template",
            "status": STATUS_OPERATOR_GUIDED,
            "source_path": _display_path(input_path, root),
            "summary": {"reason": "host_template_not_provided"},
            "warnings": ["customer host proof remains operator-guided"],
        }
    host_profile = host_input.get("host_profile") if isinstance(host_input.get("host_profile"), dict) else {}
    redaction = host_input.get("redaction_acknowledgement") if isinstance(host_input.get("redaction_acknowledgement"), dict) else {}
    is_customer_controlled = bool(host_profile.get("is_customer_controlled"))
    acknowledged = bool(redaction.get("acknowledged"))
    status = STATUS_PASS if is_customer_controlled and acknowledged else STATUS_WARNING
    warnings = []
    if not is_customer_controlled:
        warnings.append("host_not_customer_controlled")
    if not acknowledged:
        warnings.append("redaction_not_acknowledged")
    return {
        "id": "customer_host_template",
        "label": "Customer host template",
        "status": status,
        "source_path": _display_path(input_path, root),
        "summary": {
            "host_class": host_profile.get("host_class"),
            "os_family": host_profile.get("os_family"),
            "deployment_mode": host_profile.get("deployment_mode"),
            "is_customer_controlled": is_customer_controlled,
            "operator": host_profile.get("operator"),
            "redaction_acknowledged": acknowledged,
        },
        "warnings": warnings,
    }


def _browser_lane(host_input: dict[str, Any] | None, browser_smoke_path: str | None, root: Path) -> dict[str, Any]:
    source_lane = _source_summary("browser_smoke", "Browser smoke", browser_smoke_path, root)
    if browser_smoke_path:
        return source_lane
    browser_smoke = host_input.get("browser_smoke") if isinstance(host_input, dict) and isinstance(host_input.get("browser_smoke"), dict) else None
    if browser_smoke is None:
        return {
            "id": "browser_smoke",
            "label": "Browser smoke",
            "status": STATUS_OPERATOR_GUIDED,
            "source_path": None,
            "summary": {"reason": "browser_smoke_not_provided"},
            "warnings": ["run browser rehearsal or provide sanitized customer smoke result"],
        }
    return {
        "id": "browser_smoke",
        "label": "Browser smoke",
        "status": normalize_status(browser_smoke.get("status"), STATUS_WARNING),
        "source_path": None,
        "summary": _bounded(
            {
                "summary": browser_smoke.get("summary"),
                "pages": browser_smoke.get("pages"),
                "operator": browser_smoke.get("operator"),
            }
        ),
        "warnings": [],
    }


def build_report(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    host_input_path = _resolve_path(args.host_input_json, root)
    host_input: dict[str, Any] | None = None
    host_input_error: str | None = None
    if host_input_path is not None:
        host_input, host_input_error = _read_json(host_input_path)

    redaction_findings = detect_sensitive_material(host_input or {})
    lanes = [
        _host_lane(host_input, host_input_path, root),
        _source_summary("package_verification", "Package verification", args.package_verification_json, root),
        _source_summary("clean_install", "Clean install rehearsal", args.clean_install_json, root),
        _source_summary("external_install", "External install evidence", args.external_install_evidence_json, root),
        _browser_lane(host_input, args.browser_smoke_json, root),
        _source_summary("release_rehearsal", "Release rehearsal bundle", args.release_rehearsal_json, root),
        _source_summary("readiness_history", "Readiness history", args.readiness_history_json, root),
    ]
    if host_input_error:
        lanes[0]["status"] = STATUS_BLOCKING
        lanes[0]["warnings"] = [host_input_error]
    if redaction_findings:
        lanes.append(
            {
                "id": "redaction_review",
                "label": "Redaction review",
                "status": STATUS_BLOCKING,
                "source_path": _display_path(host_input_path, root),
                "summary": {"finding_count": len(redaction_findings)},
                "warnings": [finding["id"] for finding in redaction_findings],
            }
        )

    lane_statuses = [str(lane.get("status") or STATUS_UNKNOWN) for lane in lanes]
    status = combined_status(lane_statuses)
    blockers = [lane for lane in lanes if normalize_status(lane.get("status")) == STATUS_BLOCKING]
    non_pass = [lane for lane in lanes if status_rank(lane.get("status")) > 0]
    host_profile = host_input.get("host_profile") if isinstance(host_input, dict) and isinstance(host_input.get("host_profile"), dict) else {}
    package_identity = host_input.get("package_identity") if isinstance(host_input, dict) and isinstance(host_input.get("package_identity"), dict) else {}
    limitations = host_input.get("limitations") if isinstance(host_input, dict) and isinstance(host_input.get("limitations"), list) else []

    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": args.generated_at or datetime.now(UTC).isoformat(),
        "evidence_type": "external-customer-host-rehearsal-v2",
        "label": args.label,
        "status": status,
        "host_proof_level": _host_proof_level(host_input, lanes),
        "host_input_path": _display_path(host_input_path, root),
        "host_profile": _bounded(host_profile),
        "package_identity": _bounded(package_identity),
        "summary": {
            "lanes": len(lanes),
            "pass": sum(1 for lane in lanes if status_rank(lane.get("status")) == 0),
            "warning": sum(1 for lane in lanes if status_rank(lane.get("status")) == 1),
            "blocking": sum(1 for lane in lanes if status_rank(lane.get("status")) >= 2),
            "operator_guided": sum(1 for lane in lanes if normalize_status(lane.get("status")) == STATUS_OPERATOR_GUIDED),
            "not_provided": sum(1 for lane in lanes if normalize_status(lane.get("status")) == STATUS_NOT_PROVIDED),
        },
        "lanes": lanes,
        "blockers": blockers,
        "redaction_findings": redaction_findings,
        "limitations": _bounded(limitations),
        "recommended_next_actions": _recommended_next_actions(status, lanes, host_input),
        "sensitive_material_note": "Do not include tokens, .env files, private repository contents, raw database backups, or raw customer logs in this evidence.",
    }
    return report


def _host_proof_level(host_input: dict[str, Any] | None, lanes: list[dict[str, Any]]) -> str:
    if host_input is None:
        return "operator_guided"
    host_profile = host_input.get("host_profile") if isinstance(host_input.get("host_profile"), dict) else {}
    if not host_profile.get("is_customer_controlled"):
        return "external_template_not_customer_controlled"
    if any(lane["id"] == "browser_smoke" and normalize_status(lane.get("status")) == STATUS_PASS for lane in lanes):
        return "customer_controlled_with_browser_smoke"
    return "customer_controlled_template_only"


def _recommended_next_actions(status: str, lanes: list[dict[str, Any]], host_input: dict[str, Any] | None) -> list[str]:
    if status == STATUS_BLOCKING:
        blocking_ids = ", ".join(str(lane.get("id")) for lane in lanes if normalize_status(lane.get("status")) == STATUS_BLOCKING)
        return [f"Resolve blocking customer-host rehearsal lanes: {blocking_ids}."]
    non_pass = [str(lane.get("id")) for lane in lanes if status_rank(lane.get("status")) > 0]
    actions: list[str] = []
    if host_input is None:
        actions.append("Fill the sanitized customer-host v2 template on a non-developer or customer-controlled host.")
    if non_pass:
        actions.append(f"Rerun or explicitly disclose non-pass customer-host lanes: {', '.join(non_pass[:8])}.")
    actions.append("Archive customer-host v2 evidence into readiness history before customer handoff.")
    return actions


def _markdown_cell(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, (dict, list)):
        text = json.dumps(value, sort_keys=True, ensure_ascii=False)
    else:
        text = str(value)
    return text.replace("|", "\\|").replace("\n", "<br>") or "-"


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    lines = [
        "# External Customer Host Rehearsal v2",
        "",
        f"- Label: `{report.get('label')}`",
        f"- Generated at: `{report.get('generated_at')}`",
        f"- Status: `{report.get('status')}`",
        f"- Host proof level: `{report.get('host_proof_level')}`",
        f"- Host input: `{report.get('host_input_path') or '-'}`",
        f"- Pass lanes: `{summary.get('pass', 0)}`",
        f"- Warning lanes: `{summary.get('warning', 0)}`",
        f"- Blocking lanes: `{summary.get('blocking', 0)}`",
        f"- Operator-guided lanes: `{summary.get('operator_guided', 0)}`",
        f"- Not-provided lanes: `{summary.get('not_provided', 0)}`",
        "",
        "## Host Profile",
        "",
        f"`{json.dumps(report.get('host_profile') or {}, sort_keys=True, ensure_ascii=False)}`",
        "",
        "## Evidence Lanes",
        "",
        "| Lane | Status | Source | Summary | Warnings |",
        "| --- | --- | --- | --- | --- |",
    ]
    for lane in report.get("lanes") or []:
        lines.append(
            f"| {_markdown_cell(lane.get('label'))} | {_markdown_cell(lane.get('status'))} | "
            f"{_markdown_cell(lane.get('source_path'))} | {_markdown_cell(lane.get('summary'))} | "
            f"{_markdown_cell(lane.get('warnings'))} |"
        )
    lines.extend(["", "## Limitations", ""])
    for item in report.get("limitations") or []:
        lines.append(f"- {item}")
    if not report.get("limitations"):
        lines.append("- not_provided")
    lines.extend(["", "## Recommended Next Actions", ""])
    for action in report.get("recommended_next_actions") or []:
        lines.append(f"- {action}")
    lines.extend(["", "## Evidence Boundary", "", f"- {report.get('sensitive_material_note')}", ""])
    return "\n".join(lines)


def write_report(root: Path, report: dict[str, Any], output_json: str, output_markdown: str) -> tuple[Path, Path]:
    json_path = _resolve_path(output_json, root)
    markdown_path = _resolve_path(output_markdown, root)
    assert json_path is not None
    assert markdown_path is not None
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, markdown_path


def archive_report(root: Path, report: dict[str, Any], json_path: Path, markdown_path: Path, args: argparse.Namespace) -> dict[str, Any]:
    history_root = _resolve_path(args.history_root, root)
    assert history_root is not None
    entry = readiness_history.build_entry(
        sources=[
            readiness_history.EvidenceSource(
                readiness_history.FAMILY_EXTERNAL_CUSTOMER_HOST_V2,
                json_path,
                markdown_path,
            )
        ],
        root=root,
        history_root=history_root,
        label=args.archive_label or args.label,
        created_at=str(report.get("generated_at") or datetime.now(UTC).isoformat()),
        commit=args.commit,
        version_label=args.version_label,
    )
    index = readiness_history.build_index(history_root)
    (history_root / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (history_root / "index.md").write_text(readiness_history.render_index_markdown(index), encoding="utf-8")
    trend = readiness_history.render_trend_markdown(readiness_history._load_entries(history_root), args.trend_limit)
    (history_root / "trend.md").write_text(trend, encoding="utf-8")
    return {
        "entry_id": entry.get("entry_id"),
        "entry_path": _display_path(history_root / str(entry.get("entry_id")), root),
        "index_path": _display_path(history_root / "index.json", root),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect external/customer-host rehearsal v2 evidence.")
    parser.add_argument("--label", default="external-customer-host-rehearsal-v2")
    parser.add_argument("--generated-at")
    parser.add_argument("--version-label")
    parser.add_argument("--commit")
    parser.add_argument("--host-input-json", help="Sanitized customer-host v2 template JSON.")
    parser.add_argument("--package-verification-json")
    parser.add_argument("--clean-install-json")
    parser.add_argument("--external-install-evidence-json")
    parser.add_argument("--browser-smoke-json")
    parser.add_argument("--release-rehearsal-json")
    parser.add_argument("--readiness-history-json")
    parser.add_argument("--output-json", default=".tmp/external-customer-host-rehearsal-v2.json")
    parser.add_argument("--output-markdown", default=".tmp/external-customer-host-rehearsal-v2.md")
    parser.add_argument("--archive-history", action="store_true")
    parser.add_argument("--archive-label")
    parser.add_argument("--history-root", default="docs/evidence/readiness")
    parser.add_argument("--trend-limit", type=int, default=5)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    report = build_report(args, root)
    json_path, markdown_path = write_report(root, report, args.output_json, args.output_markdown)
    if args.archive_history:
        report["history_archive"] = archive_report(root, report, json_path, markdown_path, args)
        json_path, markdown_path = write_report(root, report, args.output_json, args.output_markdown)
    print(f"External customer-host v2 JSON written to {json_path}")
    print(f"External customer-host v2 Markdown written to {markdown_path}")
    if report.get("history_archive"):
        print(f"Archived to {report['history_archive']['entry_path']}")
    print(f"Status: {report['status']}")
    return 1 if report["status"] == STATUS_BLOCKING else 0


if __name__ == "__main__":
    raise SystemExit(main())
