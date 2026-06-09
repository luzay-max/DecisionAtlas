from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from verify_self_hosted_package import verify_package  # noqa: E402


SCHEMA_VERSION = 1
STATUS_PASS = "pass"
STATUS_WARNING = "warning"
STATUS_BLOCKING = "blocking"
STATUS_NOT_PROVIDED = "not_provided"
STATUS_OPERATOR_GUIDED = "operator_guided"
STATUS_KNOWN_LIMITATION = "known_limitation"
STATUS_LOCAL_STACK_FAILURE = "local_stack_failure"

NON_CLEAN_STATUSES = {
    STATUS_WARNING,
    STATUS_BLOCKING,
    STATUS_NOT_PROVIDED,
    STATUS_OPERATOR_GUIDED,
    STATUS_KNOWN_LIMITATION,
    STATUS_LOCAL_STACK_FAILURE,
    "caution",
    "failed",
    "failure",
    "missing",
    "unknown",
}
BLOCKING_STATUSES = {STATUS_BLOCKING, "failed", "failure", "error"}

REQUIRED_PACKAGE_ASSETS = [
    "manifest.json",
    "README.md",
    "templates/self-hosted.env.example",
    "templates/self-hosted-entitlement.example.json",
    "docs/project/self-hosted-package-guide.md",
    "docs/project/self-hosted-operations-runbook.md",
    "docs/project/self-hosted-readiness-checklist.md",
    "docs/project/self-hosted-delivery-rehearsal.md",
    "docs/project/self-hosted-license-and-support-boundary.md",
    "docs/project/team-handoff-reporting.md",
    "scripts/dev/start-real-stack.ps1",
    "scripts/dev/start-real-stack.bat",
    "scripts/ci/verify_self_hosted_package.py",
    "scripts/ci/collect_team_handoff_report.py",
]

DEFERRED_LANES = [
    "billing",
    "hosted_multi_tenancy",
    "marketplace_or_self_service_oauth",
    "hosted_secret_vault",
    "enterprise_sso",
    "online_license_server",
    "runtime_license_enforcement",
]


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip().lower()).strip("-")
    return slug or "clean-self-hosted-install"


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


def _normalize_status(value: Any, default: str = "unknown") -> str:
    if value is None:
        return default
    normalized = str(value).strip().lower().replace(" ", "_").replace("-", "_")
    if normalized in {"passed", "success", "succeeded", "ok", "clean", "continue"}:
        return STATUS_PASS
    if normalized in {"warn", "warnings", "caution", "needs_review", "non_blocking"}:
        return STATUS_WARNING
    if normalized in {"blocked", "failed", "failure", "error"}:
        return STATUS_BLOCKING
    return normalized or default


def _status_from_evidence(data: dict[str, Any]) -> str:
    setup = data.get("setup") if isinstance(data.get("setup"), dict) else {}
    if setup.get("outcome") == STATUS_LOCAL_STACK_FAILURE:
        return STATUS_LOCAL_STACK_FAILURE
    if setup.get("benchmark_ready") is True:
        return STATUS_PASS
    for key in ("overall_status", "status", "result", "state"):
        if key in data:
            return _normalize_status(data.get(key))
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    if summary.get("operationally_blocked"):
        return STATUS_WARNING
    if summary.get("regressed"):
        return STATUS_WARNING
    return STATUS_PASS


def _source_summary(source_id: str, label: str, path_text: str | None, root: Path) -> dict[str, Any]:
    path = _resolve_path(path_text, root)
    if path is None:
        return {
            "id": source_id,
            "label": label,
            "source_path": None,
            "status": STATUS_NOT_PROVIDED,
            "details": {"rerun_condition": f"Provide --{source_id.replace('_', '-')}-json."},
        }
    if not path.exists():
        return {
            "id": source_id,
            "label": label,
            "source_path": _display_path(path, root),
            "status": STATUS_WARNING,
            "details": {"error": "source_missing"},
        }
    data, error = _read_json(path)
    if error or data is None:
        return {
            "id": source_id,
            "label": label,
            "source_path": _display_path(path, root),
            "status": STATUS_WARNING,
            "details": {"error": error},
        }
    return {
        "id": source_id,
        "label": label,
        "source_path": _display_path(path, root),
        "status": _status_from_evidence(data),
        "details": _compact_evidence_details(data),
    }


def _compact_evidence_details(data: dict[str, Any]) -> dict[str, Any]:
    details: dict[str, Any] = {}
    for key in (
        "generated_at",
        "label",
        "version_label",
        "commit",
        "package_label",
        "package_path",
        "overall_status",
        "status",
        "result",
        "state",
    ):
        if data.get(key) is not None:
            details[key] = data.get(key)
    setup = data.get("setup") if isinstance(data.get("setup"), dict) else None
    if setup:
        details["setup"] = {
            "outcome": setup.get("outcome"),
            "benchmark_ready": setup.get("benchmark_ready"),
        }
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else None
    if summary:
        details["summary"] = {
            key: summary.get(key)
            for key in ("repositories", "improved", "regressed", "operationally_blocked", "release_evidence_ready")
            if key in summary
        }
    blockers = data.get("blockers") if isinstance(data.get("blockers"), list) else []
    if blockers:
        details["blocker_count"] = len(blockers)
    return details


def _safe_reset_owned_dir(path: Path, owned_root: Path) -> None:
    resolved_path = path.resolve()
    resolved_root = owned_root.resolve()
    if resolved_path == resolved_root or resolved_root not in resolved_path.parents:
        raise ValueError(f"Refusing to reset path outside owned scratch root: {path}")
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def _copy_package_to_clean_workspace(package_dir: Path, workspace_dir: Path, scratch_root: Path) -> tuple[Path | None, list[dict[str, Any]]]:
    checks: list[dict[str, Any]] = []
    if not package_dir.exists() or not package_dir.is_dir():
        checks.append(
            {
                "id": "package_input",
                "label": "Package input exists",
                "status": STATUS_BLOCKING,
                "details": {"path": package_dir.as_posix()},
            }
        )
        return None, checks

    _safe_reset_owned_dir(workspace_dir, scratch_root)
    clean_package_dir = workspace_dir / "package-copy"
    shutil.copytree(package_dir, clean_package_dir)
    checks.append(
        {
            "id": "clean_package_copy",
            "label": "Package copied into isolated clean workspace",
            "status": STATUS_PASS,
            "details": {"path": clean_package_dir.as_posix()},
        }
    )
    return clean_package_dir, checks


def _check_required_assets(clean_package_dir: Path | None) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    if clean_package_dir is None:
        return checks
    for relative in REQUIRED_PACKAGE_ASSETS:
        present = (clean_package_dir / relative).is_file()
        checks.append(
            {
                "id": f"asset:{relative}",
                "label": f"Required handoff asset {relative}",
                "status": STATUS_PASS if present else STATUS_BLOCKING,
                "details": {"path": relative},
            }
        )
    readme_text = (clean_package_dir / "README.md").read_text(encoding="utf-8", errors="ignore") if (
        clean_package_dir / "README.md"
    ).exists() else ""
    for needle in ("rehearse_clean_self_hosted_install.py", "verify_self_hosted_package.py", "self-hosted.env.example"):
        checks.append(
            {
                "id": f"readme_reference:{needle}",
                "label": f"README references {needle}",
                "status": STATUS_PASS if needle in readme_text else STATUS_WARNING,
                "details": {"needle": needle},
            }
        )
    return checks


def _probe_url(label: str, url: str | None, timeout: float) -> dict[str, Any]:
    if not url:
        return {
            "id": f"live_probe:{label}",
            "label": f"Live probe {label}",
            "status": STATUS_OPERATOR_GUIDED,
            "details": {"reason": "url_not_provided"},
        }
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            status_code = getattr(response, "status", None)
    except (OSError, urllib.error.URLError) as exc:
        return {
            "id": f"live_probe:{label}",
            "label": f"Live probe {label}",
            "status": STATUS_LOCAL_STACK_FAILURE,
            "details": {"url": url, "error": str(exc)[:240]},
        }
    return {
        "id": f"live_probe:{label}",
        "label": f"Live probe {label}",
        "status": STATUS_PASS if status_code and status_code < 500 else STATUS_WARNING,
        "details": {"url": url, "status_code": status_code},
    }


def _overall_status(checks: list[dict[str, Any]], evidence: list[dict[str, Any]], live_probes: list[dict[str, Any]]) -> str:
    statuses = {
        _normalize_status(item.get("status"))
        for item in [*checks, *evidence, *live_probes]
    }
    if statuses & BLOCKING_STATUSES:
        return STATUS_BLOCKING
    if statuses & NON_CLEAN_STATUSES:
        return STATUS_WARNING
    return STATUS_PASS


def build_rehearsal(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    label = _slugify(args.label)
    scratch_root = root / ".tmp" / "clean-self-hosted-install"
    workspace_dir = scratch_root / label
    package_dir = _resolve_path(args.package, root)
    assert package_dir is not None

    clean_package_dir, checks = _copy_package_to_clean_workspace(package_dir, workspace_dir, scratch_root)
    checks.extend(_check_required_assets(clean_package_dir))

    if clean_package_dir is not None:
        package_verification = verify_package(clean_package_dir)
        checks.append(
            {
                "id": "copied_package_verification",
                "label": "Copied package passes offline verifier",
                "status": _normalize_status(package_verification.get("status")),
                "details": {
                    "checked_file_count": package_verification.get("checked_file_count"),
                    "blocker_count": len(package_verification.get("blockers") or []),
                },
            }
        )

    evidence = [
        _source_summary("release_evidence", "Release evidence", args.release_evidence_json, root),
        _source_summary("hosted_readiness", "Hosted/operator readiness", args.hosted_readiness_json, root),
        _source_summary("benchmark_comparison", "Benchmark comparison", args.benchmark_comparison_json, root),
        _source_summary("readiness_history", "Readiness evidence history", args.readiness_history_json, root),
        _source_summary("package_verification", "Package verification", args.package_verification_json, root),
        _source_summary("public_github_import", "Public GitHub import rehearsal", args.public_github_import_json, root),
        _source_summary("license_support", "License and support boundary", args.license_support_json, root),
        _source_summary("team_handoff", "Team handoff report", args.team_handoff_json, root),
    ]
    live_probes = [
        _probe_url("web", args.web_url, args.probe_timeout),
        _probe_url("api", args.api_url, args.probe_timeout),
        _probe_url("engine", args.engine_url, args.probe_timeout),
    ] if args.probe_live_stack else [
        {
            "id": "live_probe",
            "label": "Live stack probing",
            "status": STATUS_OPERATOR_GUIDED,
            "details": {"reason": "probe_not_requested"},
        }
    ]

    blockers = [item for item in [*checks, *evidence, *live_probes] if _normalize_status(item.get("status")) in BLOCKING_STATUSES]
    warnings = [item for item in [*checks, *evidence, *live_probes] if _normalize_status(item.get("status")) in NON_CLEAN_STATUSES]
    status = _overall_status(checks, evidence, live_probes)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": args.generated_at or datetime.now(UTC).isoformat(),
        "label": label,
        "version_label": args.version_label,
        "commit": args.commit,
        "package_path": _display_path(package_dir, root),
        "clean_workspace_path": _display_path(workspace_dir, root),
        "clean_package_path": _display_path(clean_package_dir, root) if clean_package_dir else None,
        "status": status,
        "checks": checks,
        "source_evidence": evidence,
        "live_probes": live_probes,
        "blockers": blockers,
        "warning_count": len(warnings),
        "deferred_product_lanes": DEFERRED_LANES,
        "recommended_next_actions": _recommended_next_actions(status, blockers, warnings),
        "limitations": [
            "This rehearsal validates a clean package copy and evidence bundle, not a full VM or customer-server install.",
            "Live URL probing is optional and must remain non-pass when URLs are not provided or unreachable.",
            "Secrets, repository tokens, .env files, private repository dumps, and database backups are not included.",
        ],
    }


def _recommended_next_actions(status: str, blockers: list[dict[str, Any]], warnings: list[dict[str, Any]]) -> list[str]:
    if status == STATUS_BLOCKING:
        return [
            "Resolve blocking package, asset, or evidence inputs before external operator trial.",
            *[f"Fix {item.get('id')}" for item in blockers[:5]],
        ]
    if warnings:
        return [
            "Review non-pass evidence lanes and either rerun with the missing input or disclose the operator-guided limitation.",
            "Archive clean install rehearsal evidence into readiness history before customer handoff.",
        ]
    return ["Archive this evidence with release readiness materials before customer handoff."]


def _markdown_cell(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, (dict, list)):
        text = json.dumps(value, sort_keys=True, ensure_ascii=False)
    else:
        text = str(value)
    return text.replace("|", "\\|").replace("\n", "<br>") or "-"


def render_markdown(bundle: dict[str, Any]) -> str:
    lines = [
        "# Clean Self-Hosted Install Rehearsal",
        "",
        f"- Label: `{bundle.get('label')}`",
        f"- Generated at: `{bundle.get('generated_at')}`",
        f"- Version: `{bundle.get('version_label') or '-'}`",
        f"- Commit: `{bundle.get('commit') or '-'}`",
        f"- Package: `{bundle.get('package_path')}`",
        f"- Clean workspace: `{bundle.get('clean_workspace_path')}`",
        f"- Clean package: `{bundle.get('clean_package_path') or '-'}`",
        f"- Status: `{bundle.get('status')}`",
        "",
        "## Clean Workspace Checks",
        "",
        "| Check | Status | Details |",
        "| --- | --- | --- |",
    ]
    for check in bundle.get("checks", []):
        lines.append(f"| {_markdown_cell(check.get('label'))} | {_markdown_cell(check.get('status'))} | {_markdown_cell(check.get('details'))} |")

    lines.extend(["", "## Source Evidence", "", "| Evidence | Status | Path | Details |", "| --- | --- | --- | --- |"])
    for item in bundle.get("source_evidence", []):
        lines.append(
            f"| {_markdown_cell(item.get('label'))} | {_markdown_cell(item.get('status'))} | "
            f"{_markdown_cell(item.get('source_path'))} | {_markdown_cell(item.get('details'))} |"
        )

    lines.extend(["", "## Live Stack Probes", "", "| Probe | Status | Details |", "| --- | --- | --- |"])
    for item in bundle.get("live_probes", []):
        lines.append(f"| {_markdown_cell(item.get('label'))} | {_markdown_cell(item.get('status'))} | {_markdown_cell(item.get('details'))} |")

    lines.extend(["", "## Deferred Product Lanes", ""])
    for lane in bundle.get("deferred_product_lanes", []):
        lines.append(f"- `{lane}`")

    lines.extend(["", "## Limitations", ""])
    for item in bundle.get("limitations", []):
        lines.append(f"- {item}")

    lines.extend(["", "## Recommended Next Actions", ""])
    for item in bundle.get("recommended_next_actions", []):
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def write_outputs(bundle: dict[str, Any], output_json: Path, output_markdown: Path) -> None:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(bundle, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    output_markdown.write_text(render_markdown(bundle), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a clean DecisionAtlas self-hosted package install rehearsal.")
    parser.add_argument("--package", required=True, help="Self-hosted package directory to rehearse.")
    parser.add_argument("--label", default="clean-self-hosted-install-rehearsal")
    parser.add_argument("--version-label")
    parser.add_argument("--commit")
    parser.add_argument("--generated-at")
    parser.add_argument("--output-json", default=".tmp/clean-self-hosted-install-rehearsal.json")
    parser.add_argument("--output-markdown", default=".tmp/clean-self-hosted-install-rehearsal.md")
    parser.add_argument("--release-evidence-json")
    parser.add_argument("--hosted-readiness-json")
    parser.add_argument("--benchmark-comparison-json")
    parser.add_argument("--readiness-history-json")
    parser.add_argument("--package-verification-json")
    parser.add_argument("--public-github-import-json")
    parser.add_argument("--license-support-json")
    parser.add_argument("--team-handoff-json")
    parser.add_argument("--probe-live-stack", action="store_true")
    parser.add_argument("--web-url")
    parser.add_argument("--api-url")
    parser.add_argument("--engine-url")
    parser.add_argument("--probe-timeout", type=float, default=2.0)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    bundle = build_rehearsal(args, root)
    output_json = _resolve_path(args.output_json, root)
    output_markdown = _resolve_path(args.output_markdown, root)
    assert output_json is not None
    assert output_markdown is not None
    write_outputs(bundle, output_json, output_markdown)
    print(json.dumps(bundle, indent=2, sort_keys=True, ensure_ascii=False))
    return 1 if bundle["status"] == STATUS_BLOCKING else 0


if __name__ == "__main__":
    raise SystemExit(main())
