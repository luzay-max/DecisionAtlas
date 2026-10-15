from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
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
WARNING_STATUSES = {"warning", "warn", "caution", "known_limitation", "needs_review", "manual_check"}
BLOCKING_STATUSES = {"blocking", "blocked", "failed", "failure", "error", "false"}

REQUIRED_MATERIALS = {
    "pilot_delivery_entry": "docs/project/pilot-customer-delivery-kit.md",
    "pilot_demo_script": "docs/project/pilot-demo-script.md",
    "pilot_deployment_checklist": "docs/project/pilot-deployment-checklist.md",
    "pilot_customer_faq": "docs/project/pilot-customer-faq.md",
    "pilot_tier_comparison": "docs/project/pilot-tier-comparison.md",
    "pilot_delivery_email": "docs/project/pilot-delivery-email-template.md",
    "pilot_commercial_proposal": "docs/project/pilot-commercial-proposal-kit.md",
    "pilot_paid_quote_template": "docs/project/pilot-paid-quote-template.md",
    "pilot_acceptance_checklist": "docs/project/pilot-acceptance-checklist.md",
    "pilot_support_boundary": "docs/project/pilot-support-renewal-upgrade-boundary.md",
    "commercial_sales_page": "docs/project/commercial-sales-page-draft.md",
    "commercial_one_page_brief": "docs/project/commercial-one-page-brief.md",
    "commercial_use_cases": "docs/project/commercial-use-cases.md",
    "private_repo_evidence_template": "docs/project/private-repo-pilot-evidence-template.md",
    "self_hosted_package_guide": "docs/project/self-hosted-package-guide.md",
    "license_support_boundary": "docs/project/self-hosted-license-and-support-boundary.md",
    "real_external_host_trial_guide": "docs/project/real-external-host-trial-evidence.md",
}

EVIDENCE_LANES = [
    ("pilot_delivery_verification", "Pilot delivery kit verification", "pilot_delivery_verification_json"),
    ("commercial_proposal_verification", "Commercial proposal kit verification", "commercial_proposal_verification_json"),
    ("package_verification", "Self-hosted package verification", "package_verification_json"),
    ("clean_install_rehearsal", "Clean install rehearsal", "clean_install_rehearsal_json"),
    ("release_rehearsal", "Release rehearsal", "release_rehearsal_json"),
    ("customer_host_v2", "Customer-host v2", "customer_host_v2_json"),
    ("real_external_host_trial", "Real external host trial", "real_external_host_trial_json"),
    ("full_chain_random_repo_release", "Full-chain random repo release", "full_chain_json"),
    ("readiness_history", "Readiness history", "readiness_history_json"),
    ("private_repo_pilot_evidence", "Private repo pilot evidence", "private_repo_evidence_json"),
    ("team_handoff", "Team handoff report", "team_handoff_json"),
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
        return [_bounded(item, limit=limit) for item in value[:25]]
    if isinstance(value, str):
        text = value.strip()
        return text if len(text) <= limit else text[: limit - 1].rstrip() + "..."
    return value


def detect_sensitive_material(texts: list[str]) -> list[dict[str, Any]]:
    raw = "\n".join(texts)
    findings = []
    for finding_id, pattern in SECRET_VALUE_PATTERNS:
        if pattern.search(raw):
            findings.append({"id": finding_id, "status": STATUS_BLOCKING})
    return findings


def _status_from_data(data: dict[str, Any] | None) -> str:
    if data is None:
        return STATUS_NOT_PROVIDED
    for key in ("status", "overall_status", "public_walkthrough_status", "agent_status", "result", "outcome"):
        if key in data:
            return normalize_status(data.get(key))
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    if "status" in summary:
        return normalize_status(summary.get("status"))
    return STATUS_UNKNOWN


def _compact_evidence_summary(data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"status": STATUS_NOT_PROVIDED}
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    details: dict[str, Any] = {
        "status": _status_from_data(data),
        "generated_at": data.get("generated_at"),
        "label": data.get("label"),
        "host_proof_level": data.get("host_proof_level"),
        "selected_repo_ids": data.get("selected_repo_ids") or [],
        "entry_id": data.get("entry_id"),
        "entrypoint": data.get("entrypoint"),
        "warning": summary.get("warning"),
        "blocking": summary.get("blocking"),
        "operator_guided": summary.get("operator_guided"),
        "not_provided": summary.get("not_provided"),
        "placeholder_findings": summary.get("placeholder_findings"),
    }
    blockers = data.get("blockers") if isinstance(data.get("blockers"), list) else []
    if blockers:
        details["blocker_count"] = len(blockers)
    return _bounded({key: value for key, value in details.items() if value not in (None, [], {})})


def _material_lanes(root: Path) -> list[dict[str, Any]]:
    lanes: list[dict[str, Any]] = []
    for material_id, relative in REQUIRED_MATERIALS.items():
        path = root / relative
        lanes.append(
            {
                "id": f"material:{material_id}",
                "label": relative,
                "status": STATUS_PASS if path.is_file() else STATUS_BLOCKING,
                "source_path": relative,
                "summary": {"path": relative},
                "warnings": [] if path.is_file() else ["required_material_missing"],
            }
        )
    return lanes


def _evidence_lane(lane_id: str, label: str, path_text: str | None, root: Path) -> dict[str, Any]:
    path = _resolve_path(path_text, root)
    lane = {
        "id": lane_id,
        "label": label,
        "status": STATUS_NOT_PROVIDED,
        "source_path": _display_path(path, root),
        "summary": {"reason": "source_not_provided"},
        "warnings": ["source_not_provided"],
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
    lane["status"] = _status_from_data(data)
    lane["summary"] = _compact_evidence_summary(data)
    lane["warnings"] = [] if status_rank(lane["status"]) == 0 else ["source_evidence_non_clean"]
    return lane


def _recommended_next_actions(lanes: list[dict[str, Any]], redaction_findings: list[dict[str, Any]]) -> list[str]:
    if redaction_findings:
        return ["Remove sensitive operator notes before sharing or archiving the pilot customer trial package."]
    non_clean = [str(lane["id"]) for lane in lanes if status_rank(lane.get("status")) > 0]
    actions = []
    if non_clean:
        actions.append(f"Resolve or disclose non-clean pilot package lanes: {', '.join(non_clean[:12])}.")
    if any(lane["id"] == "real_external_host_trial" and lane.get("summary", {}).get("host_proof_level") == "template_or_placeholder" for lane in lanes):
        actions.append("Replace template-only real external host evidence with sanitized observations from a real non-developer/customer-controlled host.")
    if any(lane["id"] == "private_repo_pilot_evidence" and normalize_status(lane.get("status")) != STATUS_PASS for lane in lanes):
        actions.append("Keep private repository proof operator-guided unless a sanitized customer-controlled evidence file is supplied.")
    actions.append("Send the generated bundle through a private customer channel; do not add customer-specific agreements, tokens, or legal terms to the public repository.")
    return actions


def build_package(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    evidence_lanes = [
        _evidence_lane(lane_id, label, getattr(args, attr_name), root)
        for lane_id, label, attr_name in EVIDENCE_LANES
    ]
    material_lanes = _material_lanes(root)
    redaction_findings = detect_sensitive_material(args.operator_note or [])
    redaction_lane = {
        "id": "operator_note_redaction",
        "label": "Operator note redaction",
        "status": STATUS_BLOCKING if redaction_findings else STATUS_PASS,
        "source_path": None,
        "summary": {"finding_count": len(redaction_findings)},
        "warnings": [finding["id"] for finding in redaction_findings],
    }
    lanes = [*material_lanes, *evidence_lanes, redaction_lane]
    status = combined_status([str(lane.get("status") or STATUS_UNKNOWN) for lane in lanes])
    generated_at = args.generated_at or datetime.now(UTC).isoformat()
    label = args.label
    bundle_dir = _resolve_path(args.bundle_dir or f".tmp/pilot-customer-trial-package/{label}", root)
    assert bundle_dir is not None
    package = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "evidence_type": "pilot-customer-trial-package",
        "label": label,
        "status": status,
        "bundle_dir": _display_path(bundle_dir, root),
        "summary": {
            "materials": len(material_lanes),
            "evidence_lanes": len(evidence_lanes),
            "pass": sum(1 for lane in lanes if status_rank(lane.get("status")) == 0),
            "warning": sum(1 for lane in lanes if status_rank(lane.get("status")) == 1),
            "blocking": sum(1 for lane in lanes if status_rank(lane.get("status")) >= 2),
            "operator_guided": sum(1 for lane in lanes if normalize_status(lane.get("status")) == STATUS_OPERATOR_GUIDED),
            "not_provided": sum(1 for lane in lanes if normalize_status(lane.get("status")) == STATUS_NOT_PROVIDED),
        },
        "materials": material_lanes,
        "evidence_lanes": evidence_lanes,
        "lanes": lanes,
        "blockers": [lane for lane in lanes if normalize_status(lane.get("status")) == STATUS_BLOCKING],
        "redaction_findings": redaction_findings,
        "recommended_next_actions": _recommended_next_actions(lanes, redaction_findings),
        "customer_boundary": [
            "Customer-specific agreements, contacts, legal terms, payment details, credentials, tokens, private repository content, and raw logs must stay outside the public repository.",
            "Warning or operator-guided packages can support internal preparation, but they are not clean customer-host validation.",
        ],
    }
    return package


def _markdown_cell(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, (dict, list)):
        text = json.dumps(value, sort_keys=True, ensure_ascii=False)
    else:
        text = str(value)
    return text.replace("|", "\\|").replace("\n", "<br>") or "-"


def render_markdown(package: dict[str, Any]) -> str:
    summary = package.get("summary") if isinstance(package.get("summary"), dict) else {}
    lines = [
        "# Pilot Customer Trial Package",
        "",
        f"- Label: `{package.get('label')}`",
        f"- Generated at: `{package.get('generated_at')}`",
        f"- Status: `{package.get('status')}`",
        f"- Bundle directory: `{package.get('bundle_dir')}`",
        f"- Pass lanes: `{summary.get('pass', 0)}`",
        f"- Warning lanes: `{summary.get('warning', 0)}`",
        f"- Blocking lanes: `{summary.get('blocking', 0)}`",
        f"- Not-provided lanes: `{summary.get('not_provided', 0)}`",
        "",
        "## Evidence Lanes",
        "",
        "| Lane | Status | Source | Summary | Warnings |",
        "| --- | --- | --- | --- | --- |",
    ]
    for lane in package.get("evidence_lanes") or []:
        lines.append(
            f"| {_markdown_cell(lane.get('label'))} | {_markdown_cell(lane.get('status'))} | "
            f"{_markdown_cell(lane.get('source_path'))} | {_markdown_cell(lane.get('summary'))} | "
            f"{_markdown_cell(lane.get('warnings'))} |"
        )
    lines.extend(["", "## Required Materials", "", "| Material | Status | Path |", "| --- | --- | --- |"])
    for lane in package.get("materials") or []:
        lines.append(f"| {_markdown_cell(lane.get('id'))} | {_markdown_cell(lane.get('status'))} | {_markdown_cell(lane.get('source_path'))} |")
    lines.extend(["", "## Recommended Next Actions", ""])
    for action in package.get("recommended_next_actions") or []:
        lines.append(f"- {action}")
    lines.extend(["", "## Customer Boundary", ""])
    for item in package.get("customer_boundary") or []:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def render_readme(package: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# DecisionAtlas Pilot Trial Package",
            "",
            f"- Label: `{package.get('label')}`",
            f"- Generated at: `{package.get('generated_at')}`",
            f"- Status: `{package.get('status')}`",
            "",
            "Use this folder as an operator-facing assembly point for a self-hosted pilot trial. It is not a customer-specific legal package and does not contain credentials or private repository data.",
            "",
            "## Files",
            "",
            "- `operator-checklist.md`: what the operator must run or disclose before trial handoff.",
            "- `evidence-manifest.json`: machine-readable lane summary.",
            "- `evidence-manifest.md`: human-readable lane summary.",
            "",
            "## Current Boundary",
            "",
            "- Non-clean lanes must be resolved or disclosed before claiming a clean external customer trial.",
            "- Real customer-host proof requires sanitized observations from a real external/customer-controlled machine.",
            "",
        ]
    )


def render_operator_checklist(package: dict[str, Any]) -> str:
    lines = [
        "# Pilot Trial Operator Checklist",
        "",
        "## Before Sharing",
        "",
        "- Review `evidence-manifest.md` and resolve or disclose every non-clean lane.",
        "- Confirm no customer-specific agreements, contacts, legal terms, tokens, private repository content, raw logs, or screenshots with secrets are stored in this repository.",
        "- If the real external host trial lane is `template_or_placeholder`, rerun it on a real non-developer or customer-controlled host.",
        "- If private repository proof is part of the claim, attach sanitized private-repo evidence generated on the customer-controlled host.",
        "",
        "## Required Commands To Consider",
        "",
        "- `python scripts\\ci\\verify_pilot_customer_delivery_kit.py`",
        "- `python scripts\\ci\\verify_pilot_commercial_proposal_kit.py`",
        "- `python scripts\\ci\\collect_real_external_host_trial_evidence.py ...`",
        "- `python scripts\\ci\\collect_full_chain_random_repo_release_rehearsal.py ...`",
        "- `python scripts\\ci\\collect_readiness_evidence_history.py archive ...`",
        "",
        "## Current Recommended Next Actions",
        "",
    ]
    lines.extend(f"- {action}" for action in package.get("recommended_next_actions") or [])
    lines.append("")
    return "\n".join(lines)


def write_outputs(root: Path, package: dict[str, Any], args: argparse.Namespace) -> tuple[Path, Path, Path]:
    output_json = _resolve_path(args.output_json, root)
    output_markdown = _resolve_path(args.output_markdown, root)
    bundle_dir = _resolve_path(str(package["bundle_dir"]), root)
    assert output_json is not None
    assert output_markdown is not None
    assert bundle_dir is not None
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.parent.mkdir(parents=True, exist_ok=True)
    if bundle_dir.exists() and args.clean_bundle:
        shutil.rmtree(bundle_dir)
    bundle_dir.mkdir(parents=True, exist_ok=True)

    manifest_json = bundle_dir / "evidence-manifest.json"
    manifest_md = bundle_dir / "evidence-manifest.md"
    package["generated_paths"] = {
        "json": _display_path(output_json, root),
        "markdown": _display_path(output_markdown, root),
        "bundle_dir": _display_path(bundle_dir, root),
        "bundle_readme": _display_path(bundle_dir / "README.md", root),
        "operator_checklist": _display_path(bundle_dir / "operator-checklist.md", root),
        "evidence_manifest_json": _display_path(manifest_json, root),
        "evidence_manifest_markdown": _display_path(manifest_md, root),
    }

    markdown = render_markdown(package)
    output_json.write_text(json.dumps(package, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_markdown.write_text(markdown, encoding="utf-8")
    manifest_json.write_text(json.dumps(package, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest_md.write_text(markdown, encoding="utf-8")
    (bundle_dir / "README.md").write_text(render_readme(package), encoding="utf-8")
    (bundle_dir / "operator-checklist.md").write_text(render_operator_checklist(package), encoding="utf-8")
    return output_json, output_markdown, bundle_dir


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect a DecisionAtlas pilot customer trial package.")
    parser.add_argument("--label", default="pilot-customer-trial-package")
    parser.add_argument("--generated-at")
    parser.add_argument("--output-json", default=".tmp/pilot-customer-trial-package.json")
    parser.add_argument("--output-markdown", default=".tmp/pilot-customer-trial-package.md")
    parser.add_argument("--bundle-dir")
    parser.add_argument("--clean-bundle", action="store_true")
    parser.add_argument("--operator-note", action="append", default=[])
    parser.add_argument("--pilot-delivery-verification-json")
    parser.add_argument("--commercial-proposal-verification-json")
    parser.add_argument("--package-verification-json")
    parser.add_argument("--clean-install-rehearsal-json")
    parser.add_argument("--release-rehearsal-json")
    parser.add_argument("--customer-host-v2-json")
    parser.add_argument("--real-external-host-trial-json")
    parser.add_argument("--full-chain-json")
    parser.add_argument("--readiness-history-json")
    parser.add_argument("--private-repo-evidence-json")
    parser.add_argument("--team-handoff-json")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    package = build_package(args, root)
    output_json, output_markdown, bundle_dir = write_outputs(root, package, args)
    print(f"Pilot customer trial package JSON written to {output_json}")
    print(f"Pilot customer trial package Markdown written to {output_markdown}")
    print(f"Pilot customer trial package bundle written to {bundle_dir}")
    print(f"Status: {package['status']}")
    return 1 if package["status"] == STATUS_BLOCKING else 0


if __name__ == "__main__":
    raise SystemExit(main())
