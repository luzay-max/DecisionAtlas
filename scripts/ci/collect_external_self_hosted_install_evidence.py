from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
STATUS_PASSED = "passed"
STATUS_WARNING = "warning"
STATUS_OPERATOR_GUIDED = "operator_guided"
STATUS_NOT_PROVIDED = "not_provided"
STATUS_BLOCKED = "blocked"
ALLOWED_STATUSES = {
    STATUS_PASSED,
    STATUS_WARNING,
    STATUS_OPERATOR_GUIDED,
    STATUS_NOT_PROVIDED,
    STATUS_BLOCKED,
}
REQUIRED_LANES = [
    "package_identity",
    "startup",
    "health",
    "browser_smoke",
    "repository_import",
    "readiness_evidence",
    "redaction_review",
]
BLOCKING_MISSING_LANES = {"package_identity", "redaction_review"}

SECRET_VALUE_PATTERNS = [
    ("token_like_value", re.compile(r"(ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|glpat-[A-Za-z0-9_-]+|sk-[A-Za-z0-9_-]+|xox[baprs]-[A-Za-z0-9-]+)", re.IGNORECASE)),
    ("env_secret_assignment", re.compile(r"\b[A-Z0-9_]*(TOKEN|SECRET|PASSWORD|API_KEY|PRIVATE_KEY|DATABASE_URL)[A-Z0-9_]*\s*=\s*[^\s\"']+", re.IGNORECASE)),
    ("private_key_marker", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("raw_backup_marker", re.compile(r"(\bPGDMP\b|BEGIN DATABASE DUMP|COPY public\.|CREATE TABLE public\.)", re.IGNORECASE)),
    ("private_repo_snippet_marker", re.compile(r"(raw_private_repository|private_source_snippet|private_repo_snippet|BEGIN PRIVATE REPOSITORY CONTENT)", re.IGNORECASE)),
]


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
        return path.name


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


def normalize_status(value: Any, default: str = STATUS_NOT_PROVIDED) -> str:
    if value is None:
        return default
    normalized = str(value).strip().lower().replace(" ", "_").replace("-", "_")
    if normalized in {"pass", "passed", "success", "succeeded", "ok", "clean"}:
        return STATUS_PASSED
    if normalized in {"warn", "warnings", "caution", "needs_review", "non_blocking"}:
        return STATUS_WARNING
    if normalized in {"blocking", "blocked", "failed", "failure", "error"}:
        return STATUS_BLOCKED
    if normalized in {"operator", "operator_guided", "manual", "manual_check"}:
        return STATUS_OPERATOR_GUIDED
    if normalized in {"missing", "omitted", "not_provided", "not_available"}:
        return STATUS_NOT_PROVIDED
    return normalized if normalized in ALLOWED_STATUSES else STATUS_WARNING


def _bounded_text(value: Any, limit: int = 500) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if len(text) > limit:
        return text[: limit - 1].rstrip() + "..."
    return text


def _safe_text(value: Any, limit: int = 500) -> str | None:
    text = _bounded_text(value, limit)
    if text is None:
        return None
    if any(pattern.search(text) for _, pattern in SECRET_VALUE_PATTERNS):
        return "[redacted]"
    return text


def _safe_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _safe_value(item) for key, item in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, list):
        return [_safe_value(item) for item in value[:20]]
    if isinstance(value, str):
        return _safe_text(value)
    return value


def detect_sensitive_material(payload: dict[str, Any]) -> list[dict[str, Any]]:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    findings: list[dict[str, Any]] = []
    for finding_id, pattern in SECRET_VALUE_PATTERNS:
        if pattern.search(raw):
            findings.append({"id": finding_id, "status": STATUS_BLOCKED})
    return findings


def _lane_from_value(lane_id: str, value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {
            "id": lane_id,
            "status": STATUS_BLOCKED if lane_id in BLOCKING_MISSING_LANES else STATUS_NOT_PROVIDED,
            "evidence": None,
            "warnings": ["lane_missing_or_not_object"],
        }
    status = normalize_status(value.get("status"))
    warnings = []
    if status not in ALLOWED_STATUSES:
        status = STATUS_WARNING
        warnings.append("status_not_recognized")
    return {
        "id": lane_id,
        "status": status,
        "evidence": _safe_text(value.get("evidence") or value.get("summary") or value.get("details")),
        "warnings": warnings,
    }


def classify_lanes(data: dict[str, Any]) -> list[dict[str, Any]]:
    raw_lanes = data.get("lanes") if isinstance(data.get("lanes"), dict) else {}
    lanes = [_lane_from_value(lane_id, raw_lanes.get(lane_id)) for lane_id in REQUIRED_LANES]
    extra_lanes = sorted(set(raw_lanes) - set(REQUIRED_LANES))
    for lane_id in extra_lanes:
        lanes.append(_lane_from_value(str(lane_id), raw_lanes.get(lane_id)))
    return lanes


def _overall_status(lanes: list[dict[str, Any]], redaction_findings: list[dict[str, Any]]) -> str:
    statuses = {normalize_status(lane.get("status")) for lane in lanes}
    if redaction_findings or STATUS_BLOCKED in statuses:
        return STATUS_BLOCKED
    if statuses & {STATUS_WARNING, STATUS_OPERATOR_GUIDED, STATUS_NOT_PROVIDED}:
        return STATUS_WARNING
    return STATUS_PASSED


def build_evidence(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    input_path = _resolve_path(args.input_json, root)
    if input_path is None:
        return _blocked_bundle(args, root, "input_not_provided")
    data, error = _read_json(input_path)
    if error or data is None:
        return _blocked_bundle(args, root, error or "input_unreadable", input_path=input_path)

    lanes = classify_lanes(data)
    redaction_findings = detect_sensitive_material(data)
    if redaction_findings:
        for lane in lanes:
            if lane["id"] == "redaction_review":
                lane["status"] = STATUS_BLOCKED
                lane["warnings"] = [*lane.get("warnings", []), "sensitive_material_detected"]

    external_host = data.get("external_host") if isinstance(data.get("external_host"), dict) else {}
    package_identity = data.get("package_identity") if isinstance(data.get("package_identity"), dict) else {}
    acknowledgement = data.get("redaction_acknowledgement") if isinstance(data.get("redaction_acknowledgement"), dict) else {}
    status = _overall_status(lanes, redaction_findings)
    limitations = data.get("limitations") if isinstance(data.get("limitations"), list) else []
    source_paths = data.get("source_evidence_paths") if isinstance(data.get("source_evidence_paths"), list) else []
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": args.generated_at or datetime.now(UTC).isoformat(),
        "label": args.label or data.get("evidence_label") or "external-self-hosted-install-evidence",
        "input_path": _display_path(input_path, root),
        "status": status,
        "external_host": _safe_value(external_host),
        "package_identity": _safe_value(package_identity),
        "lanes": lanes,
        "source_evidence_paths": [_safe_text(path) for path in source_paths[:20]],
        "redaction_acknowledgement": {
            "acknowledged": bool(acknowledgement.get("acknowledged")),
            "reviewer": _safe_text(acknowledgement.get("reviewer")),
            "note": _safe_text(acknowledgement.get("note")),
        },
        "redaction_findings": redaction_findings,
        "limitations": [_safe_text(item) for item in limitations[:20]],
        "recommended_next_actions": _recommended_next_actions(status, lanes, redaction_findings),
    }


def _blocked_bundle(
    args: argparse.Namespace,
    root: Path,
    reason: str,
    *,
    input_path: Path | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": args.generated_at or datetime.now(UTC).isoformat(),
        "label": args.label or "external-self-hosted-install-evidence",
        "input_path": _display_path(input_path, root),
        "status": STATUS_BLOCKED,
        "external_host": {},
        "package_identity": {},
        "lanes": [_lane_from_value(lane_id, None) for lane_id in REQUIRED_LANES],
        "source_evidence_paths": [],
        "redaction_acknowledgement": {"acknowledged": False, "reviewer": None, "note": None},
        "redaction_findings": [],
        "limitations": [],
        "recommended_next_actions": [f"Provide a readable explicit evidence input JSON: {reason}."],
    }


def _recommended_next_actions(
    status: str,
    lanes: list[dict[str, Any]],
    redaction_findings: list[dict[str, Any]],
) -> list[str]:
    if redaction_findings:
        return [
            "Remove token-like values, .env assignments, private keys, raw backup markers, and private repository snippets before sharing evidence.",
            "Regenerate JSON and Markdown after redaction.",
        ]
    non_pass = [lane["id"] for lane in lanes if normalize_status(lane.get("status")) != STATUS_PASSED]
    if status == STATUS_BLOCKED:
        return [f"Resolve blocked external install evidence lanes: {', '.join(non_pass[:8])}."]
    if non_pass:
        return [
            f"Review non-pass external install evidence lanes: {', '.join(non_pass[:8])}.",
            "Disclose operator-guided or not-provided lanes before claiming customer-host readiness.",
        ]
    return ["Attach this evidence to release, handoff, and Code Decision Audit materials."]


def _markdown_cell(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, (dict, list)):
        text = json.dumps(value, sort_keys=True, ensure_ascii=False)
    else:
        text = str(value)
    return text.replace("|", "\\|").replace("\n", "<br>") or "-"


def render_markdown(bundle: dict[str, Any]) -> str:
    host = bundle.get("external_host") if isinstance(bundle.get("external_host"), dict) else {}
    package = bundle.get("package_identity") if isinstance(bundle.get("package_identity"), dict) else {}
    lines = [
        "# External Self-Hosted Install Evidence",
        "",
        f"- Label: `{bundle.get('label')}`",
        f"- Generated at: `{bundle.get('generated_at')}`",
        f"- Status: `{bundle.get('status')}`",
        f"- Input: `{bundle.get('input_path') or '-'}`",
        "",
        "## Host Profile",
        "",
        f"- Host class: `{host.get('host_class') or 'not_provided'}`",
        f"- OS: `{host.get('os') or 'not_provided'}`",
        f"- Runtime: `{host.get('runtime') or 'not_provided'}`",
        f"- Customer controlled: `{host.get('is_customer_controlled')}`",
        f"- Operator: `{host.get('operator') or 'not_provided'}`",
        "",
        "## Package Identity",
        "",
        f"- Package: `{package.get('package_label') or 'not_provided'}`",
        f"- Version: `{package.get('version_label') or 'not_provided'}`",
        f"- Commit: `{package.get('commit') or 'not_provided'}`",
        f"- Manifest SHA256: `{package.get('package_manifest_sha256') or 'not_provided'}`",
        "",
        "## Evidence Lanes",
        "",
        "| Lane | Status | Evidence | Warnings |",
        "| --- | --- | --- | --- |",
    ]
    for lane in bundle.get("lanes", []):
        if isinstance(lane, dict):
            lines.append(
                f"| {_markdown_cell(lane.get('id'))} | {_markdown_cell(lane.get('status'))} | "
                f"{_markdown_cell(lane.get('evidence'))} | {_markdown_cell(lane.get('warnings'))} |"
            )

    lines.extend(["", "## Source Evidence Paths", ""])
    for path in bundle.get("source_evidence_paths") or []:
        lines.append(f"- `{path}`")
    if not bundle.get("source_evidence_paths"):
        lines.append("- not_provided")

    lines.extend(["", "## Redaction", ""])
    acknowledgement = bundle.get("redaction_acknowledgement") if isinstance(bundle.get("redaction_acknowledgement"), dict) else {}
    lines.append(f"- Acknowledged: `{acknowledgement.get('acknowledged')}`")
    lines.append(f"- Reviewer: `{acknowledgement.get('reviewer') or 'not_provided'}`")
    if bundle.get("redaction_findings"):
        lines.append(f"- Findings: `{bundle.get('redaction_findings')}`")
    else:
        lines.append("- Findings: `none_detected`")

    lines.extend(["", "## Limitations", ""])
    for item in bundle.get("limitations") or []:
        lines.append(f"- {item}")
    if not bundle.get("limitations"):
        lines.append("- not_provided")

    lines.extend(["", "## Recommended Next Actions", ""])
    for item in bundle.get("recommended_next_actions") or []:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def write_outputs(bundle: dict[str, Any], output_json: Path, output_markdown: Path) -> None:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(bundle, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    output_markdown.write_text(render_markdown(bundle), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect sanitized external self-hosted install evidence.")
    parser.add_argument("--input-json", required=True, help="Operator-filled external install evidence JSON.")
    parser.add_argument("--output-json", default=".tmp/external-self-hosted-install-evidence.json")
    parser.add_argument("--output-markdown", default=".tmp/external-self-hosted-install-evidence.md")
    parser.add_argument("--label")
    parser.add_argument("--generated-at")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    bundle = build_evidence(args, root)
    output_json = _resolve_path(args.output_json, root)
    output_markdown = _resolve_path(args.output_markdown, root)
    assert output_json is not None
    assert output_markdown is not None
    write_outputs(bundle, output_json, output_markdown)
    print(f"External install evidence JSON written to {output_json}")
    print(f"External install evidence Markdown written to {output_markdown}")
    print(f"Status: {bundle['status']}")
    return 1 if bundle["status"] == STATUS_BLOCKED else 0


if __name__ == "__main__":
    raise SystemExit(main())
