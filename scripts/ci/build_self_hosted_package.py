from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
DEFAULT_OUTPUT_ROOT = Path(".tmp/self-hosted-package")
PACKAGE_ROOT_NAME = "decisionatlas-self-hosted"

DOC_PATHS = [
    "docs/project/quick-start.md",
    "docs/project/deployment.md",
    "docs/project/self-hosted-package-guide.md",
    "docs/project/self-hosted-operations-runbook.md",
    "docs/project/self-hosted-readiness-checklist.md",
    "docs/project/self-hosted-delivery-rehearsal.md",
    "docs/project/self-hosted-commercial-baseline.md",
    "docs/project/pilot-customer-delivery-kit.md",
    "docs/project/pilot-demo-script.md",
    "docs/project/pilot-deployment-checklist.md",
    "docs/project/pilot-customer-faq.md",
    "docs/project/pilot-tier-comparison.md",
    "docs/project/pilot-delivery-email-template.md",
    "docs/project/pilot-commercial-proposal-kit.md",
    "docs/project/pilot-paid-quote-template.md",
    "docs/project/pilot-acceptance-checklist.md",
    "docs/project/pilot-support-renewal-upgrade-boundary.md",
    "docs/project/commercial-sales-page-draft.md",
    "docs/project/commercial-one-page-brief.md",
    "docs/project/commercial-use-cases.md",
    "docs/project/private-repo-pilot-evidence-template.md",
    "docs/project/private-repo-pilot-evidence-example.md",
    "docs/project/backup-restore-upgrade-rehearsal.md",
    "docs/project/external-self-hosted-install-evidence.md",
    "docs/project/team-handoff-reporting.md",
    "docs/project/self-hosted-license-and-support-boundary.md",
    "docs/project/release-checklist.md",
    "docs/project/code-decision-audit-template.md",
]

SCRIPT_PATHS = [
    "scripts/dev/start-real-stack.ps1",
    "scripts/dev/start-real-stack.bat",
    "scripts/dev/stop-real-stack.ps1",
    "scripts/dev/stop-real-stack.bat",
    "scripts/ci/pre-release.ps1",
    "scripts/ci/collect_release_evidence.py",
    "scripts/ci/collect_readiness_evidence_history.py",
    "scripts/ci/collect_team_handoff_report.py",
    "scripts/ci/rehearse_clean_self_hosted_install.py",
    "scripts/ci/rehearse_backup_restore_upgrade.py",
    "scripts/ci/rehearse_real_backup_restore_upgrade.py",
    "scripts/ci/collect_external_self_hosted_install_evidence.py",
    "scripts/ci/verify_pilot_customer_delivery_kit.py",
    "scripts/ci/verify_pilot_commercial_proposal_kit.py",
    "scripts/ci/verify_private_repo_pilot_evidence.py",
    "scripts/ci/verify_self_hosted_package.py",
    "scripts/demo/check_seeded_demo.py",
    "scripts/demo/collect_hosted_readiness.py",
    "scripts/demo/health-check.ps1",
    "scripts/demo/smoke-check.ps1",
    "scripts/demo/reset-demo.ps1",
    "scripts/demo/reseed-demo.ps1",
]

TEMPLATE_PATHS = [
    "templates/self-hosted.env.example",
    "templates/self-hosted-entitlement.example.json",
    "templates/private-repo-pilot-evidence.example.json",
    "templates/backup-restore-upgrade-rehearsal.example.json",
    "templates/external-self-hosted-install-evidence.example.json",
]

REQUIRED_SERVICES = [
    {"id": "postgres", "label": "PostgreSQL", "default_port": 5432, "required": True},
    {"id": "redis", "label": "Redis", "default_port": 6379, "required": True},
    {"id": "engine", "label": "Engine FastAPI", "default_url": "http://127.0.0.1:8000/health", "required": True},
    {"id": "api", "label": "Fastify API", "default_url": "http://127.0.0.1:3001/health", "required": True},
    {"id": "web", "label": "Next.js Web", "default_url": "http://127.0.0.1:3000", "required": True},
]

VALIDATION_COMMANDS = [
    "openspec validate --all --strict",
    "python scripts\\governance\\agent_guardrail.py --summary",
    "powershell -NoProfile -ExecutionPolicy Bypass -File .\\scripts\\ci\\pre-release.ps1",
    "python scripts\\ci\\verify_self_hosted_package.py --package <package-path>",
    "python scripts\\ci\\rehearse_clean_self_hosted_install.py --package <package-path> --output-json .tmp\\clean-self-hosted-install-rehearsal.json --output-markdown .tmp\\clean-self-hosted-install-rehearsal.md",
    "python scripts\\ci\\rehearse_backup_restore_upgrade.py --input-json templates\\backup-restore-upgrade-rehearsal.example.json --output-json .tmp\\backup-restore-upgrade-rehearsal.json --output-markdown .tmp\\backup-restore-upgrade-rehearsal.md",
    "python scripts\\ci\\rehearse_real_backup_restore_upgrade.py --label real-continuity-rehearsal --previous-version <previous> --target-version <target> --output-json .tmp\\real-backup-restore-upgrade-rehearsal.json --output-markdown .tmp\\real-backup-restore-upgrade-rehearsal.md",
    "python scripts\\ci\\collect_external_self_hosted_install_evidence.py --input-json templates\\external-self-hosted-install-evidence.example.json --output-json .tmp\\external-self-hosted-install-evidence.json --output-markdown .tmp\\external-self-hosted-install-evidence.md",
    "python scripts\\ci\\verify_pilot_customer_delivery_kit.py --output-json .tmp\\pilot-customer-delivery-kit-verification.json --output-markdown .tmp\\pilot-customer-delivery-kit-verification.md",
    "python scripts\\ci\\verify_pilot_commercial_proposal_kit.py --output-json .tmp\\pilot-commercial-proposal-kit-verification.json --output-markdown .tmp\\pilot-commercial-proposal-kit-verification.md",
    "python scripts\\ci\\verify_private_repo_pilot_evidence.py --evidence-json templates\\private-repo-pilot-evidence.example.json --evidence-markdown docs\\project\\private-repo-pilot-evidence-example.md --output-json .tmp\\private-repo-pilot-evidence-verification.json --output-markdown .tmp\\private-repo-pilot-evidence-verification.md",
    "python scripts\\ci\\collect_team_handoff_report.py --release-evidence-json .tmp\\release-evidence.json --hosted-readiness-json .tmp\\hosted-operator-readiness.json --benchmark-comparison-json .tmp\\real-repo-benchmark-comparison.json --readiness-history-index-json docs\\evidence\\readiness\\index.json --package-verification-json .tmp\\self-hosted-package-verification.json --license-support-json templates\\self-hosted-entitlement.example.json",
    "pnpm --filter @decisionatlas/web e2e -- team-self-hosted-rehearsal.spec.ts",
]

UNSUPPORTED_CAPABILITIES = [
    "billing",
    "hosted_multi_tenancy",
    "marketplace_or_self_service_oauth",
    "hosted_secret_vault",
    "enterprise_sso",
    "managed_hosted_operations",
    "runtime_license_enforcement",
]

SECRET_EXCLUSION_PATTERNS = [
    ".env",
    ".tmp",
    "node_modules",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "*.db",
    "*.sqlite",
    "*.log",
]


@dataclass(frozen=True)
class CopiedAsset:
    source: str
    target: str
    required: bool = True


def _copy_allowlisted_files(root: Path, package_dir: Path, paths: list[str]) -> list[CopiedAsset]:
    copied: list[CopiedAsset] = []
    for relative in paths:
        source = root / relative
        if not source.exists() or not source.is_file():
            raise FileNotFoundError(f"Required package asset does not exist: {relative}")
        target = package_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        copied.append(CopiedAsset(source=relative, target=target.relative_to(package_dir).as_posix()))
    return copied


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


def _write_package_readme(package_dir: Path, manifest: dict[str, Any]) -> None:
    lines = [
        "# DecisionAtlas Self-Hosted Package",
        "",
        f"- Package label: `{manifest['package_label']}`",
        f"- Version label: `{manifest['version_label']}`",
        f"- Commit: `{manifest['commit']}`",
        f"- Generated at: `{manifest['generated_at']}`",
        "",
        "## Start",
        "",
        "```powershell",
        "powershell -NoProfile -ExecutionPolicy Bypass -File .\\scripts\\dev\\start-real-stack.ps1",
        "```",
        "",
        "On Windows, `scripts\\dev\\start-real-stack.bat` is the one-click launcher.",
        "",
        "## Configure",
        "",
        "Copy `templates/self-hosted.env.example` to `.env` on the operator-controlled host and fill deployment-specific values.",
        "Do not commit or share real secrets, provider keys, repository tokens, database dumps, or private repository contents.",
        "",
        "## Validate",
        "",
    ]
    for command in manifest["validation_commands"]:
        lines.extend(["```powershell", command, "```", ""])
    lines.extend(
        [
            "## Required Docs",
            "",
            "- `docs/project/self-hosted-package-guide.md`",
            "- `docs/project/self-hosted-operations-runbook.md`",
            "- `docs/project/self-hosted-readiness-checklist.md`",
            "- `docs/project/self-hosted-delivery-rehearsal.md`",
            "- `docs/project/external-self-hosted-install-evidence.md`",
            "- `docs/project/self-hosted-license-and-support-boundary.md`",
            "",
            "## Explicitly Out Of Scope",
            "",
        ]
    )
    for item in manifest["unsupported_capabilities"]:
        lines.append(f"- `{item}`")
    lines.append("")
    (package_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


def build_manifest(
    *,
    root: Path,
    package_dir: Path,
    package_label: str,
    version_label: str,
    commit: str | None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    resolved_commit = commit or _git_commit(root) or "unknown"
    return {
        "schema_version": SCHEMA_VERSION,
        "project": "DecisionAtlas",
        "package_label": package_label,
        "version_label": version_label,
        "commit": resolved_commit,
        "generated_at": generated_at or datetime.now(UTC).isoformat(),
        "package_path": package_dir.as_posix(),
        "package_root_name": PACKAGE_ROOT_NAME,
        "docs": [{"source": path, "target": path, "required": True} for path in DOC_PATHS],
        "scripts": [{"source": path, "target": path, "required": True} for path in SCRIPT_PATHS],
        "templates": [{"source": path, "target": path, "required": True} for path in TEMPLATE_PATHS],
        "required_services": REQUIRED_SERVICES,
        "default_urls": {
            "web": "http://127.0.0.1:3000",
            "api": "http://127.0.0.1:3001/health",
            "engine": "http://127.0.0.1:8000/health",
        },
        "validation_commands": VALIDATION_COMMANDS,
        "secret_exclusion_patterns": SECRET_EXCLUSION_PATTERNS,
        "support_boundary": {
            "package_type": "source_tree_handoff",
            "secret_custody": "customer_controlled_host_only",
            "runtime_smoke_required_separately": True,
            "readiness_history_required_for_clean_customer_claims": True,
            "team_handoff_report_required_for_customer_handoff": True,
            "license_support_boundary_required_for_paid_customer_handoff": True,
        },
        "unsupported_capabilities": UNSUPPORTED_CAPABILITIES,
        "readiness_evidence_expectations": [
            "package_verification_json",
            "package_verification_markdown",
            "openspec_strict_validation",
            "governance_guardrail_summary",
            "pre_release_or_explicit_substitute",
            "release_evidence",
            "hosted_operator_readiness",
            "team_workflow_browser_rehearsal_for_team_claims",
            "public_github_import_rehearsal_before_live_benchmark_claims",
            "readiness_evidence_history_entry_for_customer_claims",
            "team_handoff_report_json",
            "team_handoff_report_markdown",
            "clean_self_hosted_install_rehearsal_json",
            "clean_self_hosted_install_rehearsal_markdown",
            "pilot_customer_delivery_kit_verification_json",
            "pilot_customer_delivery_kit_verification_markdown",
            "pilot_commercial_proposal_kit_verification_json",
            "pilot_commercial_proposal_kit_verification_markdown",
            "private_repo_pilot_evidence_template",
            "private_repo_pilot_evidence_verification_json",
            "private_repo_pilot_evidence_verification_markdown",
            "backup_restore_upgrade_rehearsal_json",
            "backup_restore_upgrade_rehearsal_markdown",
            "real_backup_restore_upgrade_rehearsal_json",
            "real_backup_restore_upgrade_rehearsal_markdown",
            "external_self_hosted_install_evidence_template",
            "external_self_hosted_install_evidence_json",
            "external_self_hosted_install_evidence_markdown",
            "commercial_sales_enablement_kit",
            "license_support_boundary_doc",
            "offline_entitlement_template",
        ],
    }


def build_package(
    *,
    root: Path,
    output_root: Path,
    package_label: str,
    version_label: str,
    commit: str | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    package_dir = output_root / package_label
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True, exist_ok=True)

    manifest = build_manifest(
        root=root,
        package_dir=package_dir,
        package_label=package_label,
        version_label=version_label,
        commit=commit,
        generated_at=generated_at,
    )
    _write_package_readme(package_dir, manifest)
    _copy_allowlisted_files(root, package_dir, DOC_PATHS)
    _copy_allowlisted_files(root, package_dir, SCRIPT_PATHS)
    _copy_allowlisted_files(root, package_dir, TEMPLATE_PATHS)
    (package_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    return manifest | {"package_path": package_dir.as_posix()}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a DecisionAtlas self-hosted release package directory.")
    parser.add_argument("--label", default=PACKAGE_ROOT_NAME, help="Package directory label.")
    parser.add_argument("--version-label", default="self-hosted-preview", help="Human-readable version label.")
    parser.add_argument("--commit", default=None, help="Commit to record in the manifest. Defaults to current HEAD.")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT, help="Root directory for packages.")
    parser.add_argument("--output-json", type=Path, default=None, help="Optional path to copy the manifest JSON.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    manifest = build_package(
        root=root,
        output_root=root / args.output_root,
        package_label=args.label,
        version_label=args.version_label,
        commit=args.commit,
    )
    if args.output_json is not None:
        output_json = args.output_json if args.output_json.is_absolute() else root / args.output_json
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
