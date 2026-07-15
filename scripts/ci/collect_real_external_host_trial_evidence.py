from __future__ import annotations

import argparse
import json
import re
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
STATUS_NOT_APPLICABLE = "not_applicable"

CORE_TRIAL_LANES = (
    "startup",
    "health",
    "admin_login",
    "team_workspace",
    "repository_import",
    "review",
    "why",
    "drift",
    "continuity",
    "browser_smoke",
)

CORE_TRIAL_LABELS = {
    "startup": "Stack startup",
    "health": "Service health",
    "admin_login": "Administrator login",
    "team_workspace": "Team and workspace setup",
    "repository_import": "Repository import",
    "review": "Candidate review",
    "why": "Why search",
    "drift": "Drift evaluation",
    "continuity": "Backup and recovery",
    "browser_smoke": "Browser smoke",
}

PASS_STATUSES = {"pass", "passed", "ok", "success", "succeeded", "clean", "ready", "true"}
WARNING_STATUSES = {"warning", "warn", "caution", "known_limitation", "needs_review", "manual_check"}
BLOCKING_STATUSES = {"blocking", "blocked", "failed", "failure", "error", "false", "local_stack_failure"}

PLACEHOLDER_PATTERNS = [
    ("fill_me", re.compile(r"\bfill[-_ ]?me\b", re.IGNORECASE)),
    ("customer_or_operator_name", re.compile(r"customer-or-operator-name", re.IGNORECASE)),
    ("replace_sample", re.compile(r"\breplace this sample\b|\bsample\b|\bexample\b|\btemplate\b", re.IGNORECASE)),
    ("optional_placeholder", re.compile(r"^optional$", re.IGNORECASE)),
    ("placeholder_marker", re.compile(r"\b(todo|tbd|placeholder)\b", re.IGNORECASE)),
]

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
    if normalized in {"not_applicable", "n_a", "na"}:
        return STATUS_NOT_APPLICABLE
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
        return "<external-path>"


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


def _sanitize_text(value: str) -> str:
    text = value.strip()
    text = re.sub(r"(?i)(?:[A-Za-z]:[\\/]|\\\\)[^\"\r\n|]+", "<external-path>", text)
    return text


def _bounded(value: Any, limit: int = 500) -> Any:
    if isinstance(value, dict):
        return {str(key): _bounded(item, limit=limit) for key, item in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, list):
        return [_bounded(item, limit=limit) for item in value[:25]]
    if isinstance(value, str):
        text = _sanitize_text(value)
        return text if len(text) <= limit else text[: limit - 1].rstrip() + "..."
    return value


def _iter_text(value: Any, path: str = "$"):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from _iter_text(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _iter_text(item, f"{path}[{index}]")
    elif isinstance(value, str):
        yield path, value


def detect_placeholder_material(payload: Any) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for path, value in _iter_text(payload):
        text = value.strip()
        for finding_id, pattern in PLACEHOLDER_PATTERNS:
            if pattern.search(text):
                findings.append({"id": finding_id, "status": STATUS_WARNING, "path": path})
                break
    return findings


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


def _source_data(path_text: str | None, root: Path) -> tuple[Path | None, dict[str, Any] | None, str | None]:
    path = _resolve_path(path_text, root)
    if path is None:
        return None, None, None
    if not path.exists():
        return path, None, "source_missing"
    data, error = _read_json(path)
    return path, data, error


def _customer_host_summary(data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"status": STATUS_NOT_PROVIDED, "host_proof_level": "not_provided"}
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    return {
        "status": _source_status(data),
        "host_proof_level": data.get("host_proof_level"),
        "pass": summary.get("pass"),
        "warning": summary.get("warning"),
        "blocking": summary.get("blocking"),
        "operator_guided": summary.get("operator_guided"),
        "not_provided": summary.get("not_provided"),
        "blocker_count": len(data.get("blockers") if isinstance(data.get("blockers"), list) else []),
        "limitations": _bounded(data.get("limitations") or []),
    }


def _full_chain_summary(data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"status": STATUS_NOT_PROVIDED, "selected_repo_ids": []}
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    return {
        "status": _source_status(data),
        "selected_repo_ids": data.get("selected_repo_ids") or [],
        "pass": summary.get("pass"),
        "warning": summary.get("warning"),
        "blocking": summary.get("blocking"),
        "operator_guided": summary.get("operator_guided"),
        "not_provided": summary.get("not_provided"),
        "blocker_count": len(data.get("blockers") if isinstance(data.get("blockers"), list) else []),
        "limitations": _bounded(data.get("limitations") or []),
    }


def _source_lane(lane_id: str, label: str, path_text: str | None, root: Path, summarizer) -> dict[str, Any]:
    path, data, error = _source_data(path_text, root)
    summary = summarizer(data)
    lane = {
        "id": lane_id,
        "label": label,
        "status": normalize_status(summary.get("status"), STATUS_NOT_PROVIDED),
        "source_path": _display_path(path, root),
        "summary": summary,
        "warnings": [],
    }
    if not path_text:
        lane["warnings"] = ["source_not_provided"]
    if path_text and error:
        lane["status"] = STATUS_WARNING
        lane["warnings"] = [error]
    return lane


def _required_host_findings(host_input: dict[str, Any] | None) -> list[dict[str, Any]]:
    if host_input is None:
        return [{"id": "host_input_missing", "status": STATUS_OPERATOR_GUIDED, "path": "$"}]
    host = host_input.get("host_profile") if isinstance(host_input.get("host_profile"), dict) else {}
    package = host_input.get("package_identity") if isinstance(host_input.get("package_identity"), dict) else {}
    redaction = host_input.get("redaction_acknowledgement") if isinstance(host_input.get("redaction_acknowledgement"), dict) else {}
    browser = host_input.get("browser_smoke") if isinstance(host_input.get("browser_smoke"), dict) else {}
    checks = [
        ("host_class_missing", "$.host_profile.host_class", bool(host.get("host_class"))),
        ("os_family_missing", "$.host_profile.os_family", bool(host.get("os_family"))),
        ("deployment_mode_missing", "$.host_profile.deployment_mode", bool(host.get("deployment_mode"))),
        ("operator_missing", "$.host_profile.operator", bool(host.get("operator"))),
        ("host_not_customer_controlled", "$.host_profile.is_customer_controlled", bool(host.get("is_customer_controlled"))),
        ("version_label_missing", "$.package_identity.version_label", bool(package.get("version_label"))),
        ("commit_missing", "$.package_identity.commit", bool(package.get("commit"))),
        ("redaction_not_acknowledged", "$.redaction_acknowledgement.acknowledged", bool(redaction.get("acknowledged"))),
        ("browser_smoke_not_pass", "$.browser_smoke.status", normalize_status(browser.get("status"), STATUS_NOT_PROVIDED) == STATUS_PASS),
    ]
    findings = [{"id": finding_id, "status": STATUS_WARNING, "path": path} for finding_id, path, ok in checks if not ok]
    for lane in _core_trial_lanes(host_input):
        if lane["status"] in {STATUS_NOT_PROVIDED, STATUS_UNKNOWN}:
            findings.append(
                {
                    "id": f"{lane['id']}_lane_missing",
                    "status": STATUS_WARNING,
                    "path": f"$.trial_lanes.{lane['id']}",
                }
            )
    return findings


def _legacy_lane_status(host_input: dict[str, Any], lane_id: str) -> tuple[str, Any]:
    if lane_id == "startup":
        records = host_input.get("commands_run") if isinstance(host_input.get("commands_run"), list) else []
        record = next((item for item in records if isinstance(item, dict) and item.get("id") in {"start_stack", "startup"}), None)
        return (normalize_status(record.get("status"), STATUS_NOT_PROVIDED), record.get("summary") if record else None) if record else (STATUS_NOT_PROVIDED, None)
    if lane_id == "health":
        records = host_input.get("health_checks") if isinstance(host_input.get("health_checks"), list) else []
        statuses = [normalize_status(item.get("status"), STATUS_NOT_PROVIDED) for item in records if isinstance(item, dict)]
        if statuses and all(status == STATUS_PASS for status in statuses):
            return STATUS_PASS, "All supplied service health checks passed."
        if statuses:
            return STATUS_WARNING, "One or more supplied service health checks were not clean."
    if lane_id == "browser_smoke":
        browser = host_input.get("browser_smoke") if isinstance(host_input.get("browser_smoke"), dict) else {}
        return normalize_status(browser.get("status"), STATUS_NOT_PROVIDED), browser.get("summary")
    return STATUS_NOT_PROVIDED, None


def _core_trial_lanes(host_input: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(host_input, dict):
        return [
            {
                "id": lane_id,
                "label": CORE_TRIAL_LABELS[lane_id],
                "status": STATUS_NOT_PROVIDED,
                "source_path": None,
                "summary": {"reason": "trial_lane_not_provided"},
                "warnings": ["trial_lane_not_provided"],
            }
            for lane_id in CORE_TRIAL_LANES
        ]
    supplied = host_input.get("trial_lanes")
    supplied = supplied if isinstance(supplied, dict) else {}
    lanes: list[dict[str, Any]] = []
    for lane_id in CORE_TRIAL_LANES:
        record = supplied.get(lane_id)
        if isinstance(record, dict):
            status = normalize_status(record.get("status"), STATUS_NOT_PROVIDED)
            summary = record.get("summary") or record.get("evidence") or {"reason": "summary_not_provided"}
            warnings = record.get("warnings") or ([] if status == STATUS_PASS else ["lane_not_clean"])
        else:
            status, legacy_summary = _legacy_lane_status(host_input, lane_id)
            summary = legacy_summary or {"reason": "trial_lane_not_provided"}
            warnings = [] if status == STATUS_PASS else ["trial_lane_not_provided"]
        lanes.append(
            {
                "id": lane_id,
                "label": CORE_TRIAL_LABELS[lane_id],
                "status": status,
                "source_path": None,
                "summary": _bounded(summary),
                "warnings": _bounded(warnings),
            }
        )
    return lanes


def _host_lane(host_input: dict[str, Any] | None, input_path: Path | None, root: Path) -> dict[str, Any]:
    if host_input is None:
        return {
            "id": "host_input",
            "label": "Sanitized host input",
            "status": STATUS_OPERATOR_GUIDED,
            "source_path": _display_path(input_path, root),
            "summary": {"reason": "host_input_not_provided"},
            "warnings": ["real external host input is required before external trial claims"],
        }
    host = host_input.get("host_profile") if isinstance(host_input.get("host_profile"), dict) else {}
    package = host_input.get("package_identity") if isinstance(host_input.get("package_identity"), dict) else {}
    browser = host_input.get("browser_smoke") if isinstance(host_input.get("browser_smoke"), dict) else {}
    required_findings = _required_host_findings(host_input)
    return {
        "id": "host_input",
        "label": "Sanitized host input",
        "status": STATUS_PASS if not required_findings else STATUS_WARNING,
        "source_path": _display_path(input_path, root),
        "summary": _bounded(
            {
                "host_class": host.get("host_class"),
                "os_family": host.get("os_family"),
                "deployment_mode": host.get("deployment_mode"),
                "is_customer_controlled": bool(host.get("is_customer_controlled")),
                "operator": host.get("operator"),
                "package_label": package.get("package_label"),
                "version_label": package.get("version_label"),
                "commit": package.get("commit"),
                "browser_smoke_status": normalize_status(browser.get("status"), STATUS_NOT_PROVIDED),
                "required_finding_count": len(required_findings),
            }
        ),
        "warnings": [finding["id"] for finding in required_findings],
    }


def _review_lane(lane_id: str, label: str, findings: list[dict[str, Any]], clean_status: str = STATUS_PASS) -> dict[str, Any]:
    status = STATUS_BLOCKING if any(normalize_status(finding.get("status")) == STATUS_BLOCKING for finding in findings) else (STATUS_WARNING if findings else clean_status)
    return {
        "id": lane_id,
        "label": label,
        "status": status,
        "source_path": None,
        "summary": {"finding_count": len(findings), "finding_ids": [finding.get("id") for finding in findings[:20]]},
        "warnings": [str(finding.get("id")) for finding in findings[:20]],
    }


def _host_proof_level(host_input: dict[str, Any] | None, lanes: list[dict[str, Any]], placeholders: list[dict[str, Any]]) -> str:
    if host_input is None:
        return "operator_guided"
    if placeholders:
        return "template_or_placeholder"
    host = host_input.get("host_profile") if isinstance(host_input.get("host_profile"), dict) else {}
    browser = host_input.get("browser_smoke") if isinstance(host_input.get("browser_smoke"), dict) else {}
    if not host.get("is_customer_controlled"):
        return "external_template_not_customer_controlled"
    if normalize_status(browser.get("status"), STATUS_NOT_PROVIDED) == STATUS_PASS and all(status_rank(lane.get("status")) == 0 for lane in lanes):
        return "real_external_customer_controlled"
    return "customer_controlled_with_non_clean_sources"


def _recommended_next_actions(status: str, lanes: list[dict[str, Any]], placeholders: list[dict[str, Any]], host_input: dict[str, Any] | None) -> list[str]:
    if status == STATUS_BLOCKING:
        blocking_ids = ", ".join(str(lane.get("id")) for lane in lanes if normalize_status(lane.get("status")) == STATUS_BLOCKING)
        return [f"Remove or redact blocking material before archiving evidence: {blocking_ids}."]
    actions: list[str] = []
    if host_input is None:
        actions.append("Provide sanitized host input from a real external or customer-controlled machine.")
    if placeholders:
        actions.append("Replace example/template placeholder values with real sanitized external host observations.")
    non_pass = [str(lane.get("id")) for lane in lanes if status_rank(lane.get("status")) > 0]
    if non_pass:
        actions.append(f"Resolve or explicitly disclose non-clean trial lanes: {', '.join(non_pass[:8])}.")
    actions.append("Archive this evidence into readiness history only after confirming the boundary is acceptable.")
    return actions


def build_report(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    host_input_path = _resolve_path(args.host_input_json, root)
    host_input: dict[str, Any] | None = None
    host_input_error: str | None = None
    if host_input_path is not None:
        host_input, host_input_error = _read_json(host_input_path)

    placeholder_findings = detect_placeholder_material(host_input or {})
    required_findings = _required_host_findings(host_input)
    redaction_findings = detect_sensitive_material(host_input or {})

    lanes = [
        _host_lane(host_input, host_input_path, root),
        *_core_trial_lanes(host_input),
        _review_lane("placeholder_review", "Placeholder/template review", placeholder_findings),
        _review_lane("required_host_review", "Required host field review", required_findings),
        _source_lane("customer_host_v2", "Customer-host v2", args.customer_host_v2_json, root, _customer_host_summary),
        _source_lane("full_chain_random_repo_release", "Full-chain random repo release", args.full_chain_json, root, _full_chain_summary),
    ]
    if host_input_error:
        lanes[0]["status"] = STATUS_BLOCKING
        lanes[0]["warnings"] = [host_input_error]
    if redaction_findings:
        lanes.append(_review_lane("redaction_review", "Redaction review", redaction_findings))

    source_payloads: list[Any] = []
    for source_path in (args.customer_host_v2_json, args.full_chain_json):
        _, source_data, _ = _source_data(source_path, root)
        if source_data is not None:
            source_payloads.append(source_data)
    source_redaction_findings = detect_sensitive_material(source_payloads)
    if source_redaction_findings:
        redaction_findings.extend(source_redaction_findings)
        lanes.append(_review_lane("source_redaction_review", "Source evidence redaction review", source_redaction_findings))

    lane_statuses = [str(lane.get("status") or STATUS_UNKNOWN) for lane in lanes]
    status = combined_status(lane_statuses)
    selected_repo_ids: list[str] = []
    full_chain_lane = next((lane for lane in lanes if lane["id"] == "full_chain_random_repo_release"), None)
    if full_chain_lane:
        selected_repo_ids = [str(repo_id) for repo_id in full_chain_lane.get("summary", {}).get("selected_repo_ids") or []]

    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": args.generated_at or datetime.now(UTC).isoformat(),
        "evidence_type": "real-external-host-trial-evidence",
        "label": args.label,
        "version_label": args.version_label,
        "commit": args.commit,
        "status": status,
        "host_proof_level": _host_proof_level(host_input, lanes, placeholder_findings),
        "host_input_path": _display_path(host_input_path, root),
        "selected_repo_ids": selected_repo_ids,
        "summary": {
            "lanes": len(lanes),
            "pass": sum(1 for lane in lanes if status_rank(lane.get("status")) == 0),
            "warning": sum(1 for lane in lanes if status_rank(lane.get("status")) == 1),
            "blocking": sum(1 for lane in lanes if status_rank(lane.get("status")) >= 2),
            "operator_guided": sum(1 for lane in lanes if normalize_status(lane.get("status")) == STATUS_OPERATOR_GUIDED),
            "not_provided": sum(1 for lane in lanes if normalize_status(lane.get("status")) == STATUS_NOT_PROVIDED),
            "placeholder_findings": len(placeholder_findings),
            "required_findings": len(required_findings),
            "redaction_findings": len(redaction_findings),
            "selected_repositories": len(selected_repo_ids),
        },
        "lanes": lanes,
        "blockers": [lane for lane in lanes if normalize_status(lane.get("status")) == STATUS_BLOCKING],
        "placeholder_findings": _bounded(placeholder_findings),
        "required_host_findings": _bounded(required_findings),
        "redaction_findings": redaction_findings,
        "limitations": [
            "This evidence validates sanitized operator-supplied facts; it does not embed raw customer logs or secrets.",
            "A clean pass requires real non-template external/customer-controlled host input and clean source evidence.",
            "Local smoke or example-template evidence remains useful for pipeline testing but is not customer proof.",
        ],
        "recommended_next_actions": _recommended_next_actions(status, lanes, placeholder_findings, host_input),
        "sensitive_material_note": "Do not include tokens, .env files, private repository contents, raw database backups, raw model output, or raw customer logs in this evidence.",
    }
    return report


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
        "# Real External Host Trial Evidence",
        "",
        f"- Label: `{report.get('label')}`",
        f"- Generated at: `{report.get('generated_at')}`",
        f"- Status: `{report.get('status')}`",
        f"- Host proof level: `{report.get('host_proof_level')}`",
        f"- Host input: `{report.get('host_input_path') or '-'}`",
        f"- Selected repositories: `{', '.join(report.get('selected_repo_ids') or []) or '-'}`",
        f"- Pass lanes: `{summary.get('pass', 0)}`",
        f"- Warning lanes: `{summary.get('warning', 0)}`",
        f"- Blocking lanes: `{summary.get('blocking', 0)}`",
        f"- Placeholder findings: `{summary.get('placeholder_findings', 0)}`",
        f"- Redaction findings: `{summary.get('redaction_findings', 0)}`",
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
    lines.extend(["", "## Placeholder Findings", ""])
    for finding in report.get("placeholder_findings") or []:
        lines.append(f"- `{finding.get('id')}` at `{finding.get('path')}`")
    if not report.get("placeholder_findings"):
        lines.append("- none")
    lines.extend(["", "## Limitations", ""])
    for item in report.get("limitations") or []:
        lines.append(f"- {item}")
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
                readiness_history.FAMILY_REAL_EXTERNAL_HOST_TRIAL,
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
    parser = argparse.ArgumentParser(description="Collect real external host trial evidence.")
    parser.add_argument("--label", default="real-external-host-trial-evidence")
    parser.add_argument("--generated-at")
    parser.add_argument("--version-label")
    parser.add_argument("--commit")
    parser.add_argument("--host-input-json", help="Sanitized external/customer-host input JSON.")
    parser.add_argument("--customer-host-v2-json", help="Customer-host v2 evidence JSON path.")
    parser.add_argument("--full-chain-json", help="Full-chain random repo release evidence JSON path.")
    parser.add_argument("--output-json", default=".tmp/real-external-host-trial-evidence.json")
    parser.add_argument("--output-markdown", default=".tmp/real-external-host-trial-evidence.md")
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
    print(f"Real external host trial JSON written to {json_path}")
    print(f"Real external host trial Markdown written to {markdown_path}")
    if report.get("history_archive"):
        print(f"Archived to {report['history_archive']['entry_path']}")
    print(f"Status: {report['status']}")
    return 1 if report["status"] == STATUS_BLOCKING else 0


if __name__ == "__main__":
    raise SystemExit(main())
