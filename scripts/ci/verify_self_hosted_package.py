from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
STATUS_PASS = "pass"
STATUS_BLOCKING = "blocking"
STATUS_OPERATOR_GUIDED = "operator_guided"
STATUS_NOT_PROVIDED = "not_provided"
STATUS_KNOWN_LIMITATION = "known_limitation"

REQUIRED_MANIFEST_FIELDS = [
    "schema_version",
    "project",
    "package_label",
    "version_label",
    "commit",
    "generated_at",
    "docs",
    "scripts",
    "templates",
    "required_services",
    "default_urls",
    "validation_commands",
    "secret_exclusion_patterns",
    "support_boundary",
    "unsupported_capabilities",
    "readiness_evidence_expectations",
]

REQUIRED_PACKAGE_FILES = [
    "manifest.json",
    "README.md",
    "templates/self-hosted.env.example",
    "templates/self-hosted-entitlement.example.json",
    "docs/project/self-hosted-package-guide.md",
    "docs/project/self-hosted-operations-runbook.md",
    "docs/project/self-hosted-readiness-checklist.md",
    "docs/project/self-hosted-delivery-rehearsal.md",
    "docs/project/pilot-customer-delivery-kit.md",
    "docs/project/pilot-demo-script.md",
    "docs/project/pilot-deployment-checklist.md",
    "docs/project/pilot-customer-faq.md",
    "docs/project/pilot-tier-comparison.md",
    "docs/project/pilot-delivery-email-template.md",
    "docs/project/self-hosted-license-and-support-boundary.md",
    "scripts/dev/start-real-stack.ps1",
    "scripts/dev/start-real-stack.bat",
    "scripts/dev/stop-real-stack.ps1",
    "scripts/ci/pre-release.ps1",
    "scripts/ci/rehearse_clean_self_hosted_install.py",
    "scripts/ci/verify_pilot_customer_delivery_kit.py",
    "scripts/ci/collect_team_handoff_report.py",
]

FORBIDDEN_PACKAGE_PATHS = [
    ".env",
    ".tmp",
    "node_modules",
    ".venv",
    "__pycache__",
    ".pytest_cache",
]

OPTIONAL_RUNTIME_LANES = [
    {
        "id": "runtime_smoke",
        "label": "Runtime smoke",
        "status": STATUS_OPERATOR_GUIDED,
        "reason": "Package verifier is offline; run real-stack smoke separately.",
    },
    {
        "id": "private_repository_token_validation",
        "label": "Private repository token validation",
        "status": STATUS_OPERATOR_GUIDED,
        "reason": "Customer token must remain on operator-controlled host and is not included in the package.",
    },
    {
        "id": "live_benchmark",
        "label": "Live public repository benchmark",
        "status": STATUS_NOT_PROVIDED,
        "reason": "Run public GitHub import rehearsal and benchmark comparison separately before claiming this lane.",
    },
    {
        "id": "readiness_history",
        "label": "Readiness evidence history",
        "status": STATUS_NOT_PROVIDED,
        "reason": "Archive generated evidence into docs/evidence/readiness separately.",
    },
    {
        "id": "clean_self_hosted_install_rehearsal",
        "label": "Clean self-hosted install rehearsal",
        "status": STATUS_NOT_PROVIDED,
        "reason": "Run rehearse_clean_self_hosted_install.py separately before claiming external operator trial readiness.",
    },
    {
        "id": "pilot_customer_delivery_kit",
        "label": "Pilot customer delivery kit",
        "status": STATUS_NOT_PROVIDED,
        "reason": "Run verify_pilot_customer_delivery_kit.py and attach customer-readable pilot materials before external evaluation.",
    },
    {
        "id": "team_handoff_report",
        "label": "Team handoff report",
        "status": STATUS_NOT_PROVIDED,
        "reason": "Generate JSON/Markdown handoff evidence after release, readiness, benchmark, and package evidence are available.",
    },
    {
        "id": "license_support_boundary",
        "label": "License and support boundary",
        "status": STATUS_OPERATOR_GUIDED,
        "reason": "Package includes boundary docs and an entitlement template; attach customer-specific entitlement separately for paid handoff.",
    },
]


def _read_manifest(package_dir: Path) -> tuple[dict[str, Any] | None, list[str]]:
    path = package_dir / "manifest.json"
    if not path.exists():
        return None, ["manifest.json is missing"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, [f"manifest.json is invalid JSON: {exc}"]
    if not isinstance(data, dict):
        return None, ["manifest.json must contain a JSON object"]
    return data, []


def _relative_files(package_dir: Path) -> set[str]:
    files: set[str] = set()
    for path in package_dir.rglob("*"):
        if path.is_file():
            files.add(path.relative_to(package_dir).as_posix())
    return files


def _check_required_manifest_fields(manifest: dict[str, Any] | None) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for field in REQUIRED_MANIFEST_FIELDS:
        present = manifest is not None and field in manifest and manifest.get(field) not in (None, "", [])
        checks.append(
            {
                "id": f"manifest_field:{field}",
                "label": f"Manifest field {field}",
                "status": STATUS_PASS if present else STATUS_BLOCKING,
                "details": {"field": field},
            }
        )
    return checks


def _check_required_files(package_dir: Path, files: set[str]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for relative in REQUIRED_PACKAGE_FILES:
        checks.append(
            {
                "id": f"file:{relative}",
                "label": f"Required file {relative}",
                "status": STATUS_PASS if relative in files else STATUS_BLOCKING,
                "details": {"path": relative},
            }
        )

    env_text = (package_dir / "templates/self-hosted.env.example").read_text(encoding="utf-8", errors="ignore") if (
        package_dir / "templates/self-hosted.env.example"
    ).exists() else ""
    for key in ("DATABASE_URL", "REDIS_URL", "ENGINE_BASE_URL", "API_BASE_URL", "AUTO_BOOTSTRAP_AUTH"):
        checks.append(
            {
                "id": f"env_template:{key}",
                "label": f"Environment template includes {key}",
                "status": STATUS_PASS if key in env_text else STATUS_BLOCKING,
                "details": {"key": key},
            }
        )
    return checks


def _check_forbidden_paths(files: set[str]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    violations: list[str] = []
    for relative in files:
        parts = set(relative.split("/"))
        if parts & set(FORBIDDEN_PACKAGE_PATHS):
            violations.append(relative)
        if relative.endswith((".db", ".sqlite", ".log")):
            violations.append(relative)
    checks.append(
        {
            "id": "secret_exclusions",
            "label": "Forbidden local state and secret-like files are excluded",
            "status": STATUS_PASS if not violations else STATUS_BLOCKING,
            "details": {"violations": sorted(set(violations))},
        }
    )
    return checks


def _check_manifest_references(manifest: dict[str, Any] | None, files: set[str]) -> list[dict[str, Any]]:
    if manifest is None:
        return []
    checks: list[dict[str, Any]] = []
    for group in ("docs", "scripts", "templates"):
        assets = manifest.get(group)
        if not isinstance(assets, list):
            checks.append(
                {
                    "id": f"manifest_assets:{group}",
                    "label": f"Manifest {group} assets are listed",
                    "status": STATUS_BLOCKING,
                    "details": {"reason": "not_a_list"},
                }
            )
            continue
        for index, asset in enumerate(assets):
            target = asset.get("target") if isinstance(asset, dict) else None
            present = isinstance(target, str) and target in files
            checks.append(
                {
                    "id": f"manifest_asset:{group}:{index}",
                    "label": f"Manifest {group} asset {target or index}",
                    "status": STATUS_PASS if present else STATUS_BLOCKING,
                    "details": {"target": target},
                }
            )
    return checks


def calculate_status(checks: list[dict[str, Any]]) -> str:
    return STATUS_BLOCKING if any(check["status"] == STATUS_BLOCKING for check in checks) else STATUS_PASS


def verify_package(package_dir: Path, *, generated_at: str | None = None) -> dict[str, Any]:
    manifest, manifest_errors = _read_manifest(package_dir)
    files = _relative_files(package_dir) if package_dir.exists() else set()
    checks: list[dict[str, Any]] = []

    if not package_dir.exists():
        checks.append(
            {
                "id": "package_dir",
                "label": "Package directory exists",
                "status": STATUS_BLOCKING,
                "details": {"path": package_dir.as_posix()},
            }
        )
    else:
        checks.append(
            {
                "id": "package_dir",
                "label": "Package directory exists",
                "status": STATUS_PASS,
                "details": {"path": package_dir.as_posix()},
            }
        )

    for error in manifest_errors:
        checks.append(
            {
                "id": "manifest_read",
                "label": "Manifest can be read",
                "status": STATUS_BLOCKING,
                "details": {"error": error},
            }
        )

    checks.extend(_check_required_manifest_fields(manifest))
    checks.extend(_check_required_files(package_dir, files))
    checks.extend(_check_forbidden_paths(files))
    checks.extend(_check_manifest_references(manifest, files))

    status = calculate_status(checks)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at or datetime.now(UTC).isoformat(),
        "package_path": package_dir.as_posix(),
        "package_label": manifest.get("package_label") if manifest else None,
        "version_label": manifest.get("version_label") if manifest else None,
        "commit": manifest.get("commit") if manifest else None,
        "status": status,
        "checked_file_count": len(files),
        "checks": checks,
        "non_pass_lanes": OPTIONAL_RUNTIME_LANES,
        "blockers": [check for check in checks if check["status"] == STATUS_BLOCKING],
        "notes": [
            "Package verification is offline and checks handoff structure only.",
            "Clean install rehearsal, runtime smoke, private repository token validation, live benchmark, readiness history, team handoff, and customer-specific entitlement evidence must be generated separately before clean customer claims.",
        ],
    }


def _markdown_cell(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, (dict, list)):
        text = json.dumps(value, sort_keys=True)
    else:
        text = str(value)
    return text.replace("|", "\\|").replace("\n", "<br>") or "-"


def render_markdown(bundle: dict[str, Any]) -> str:
    lines = [
        "# Self-Hosted Package Verification",
        "",
        f"- Generated at: `{bundle.get('generated_at')}`",
        f"- Package: `{bundle.get('package_path')}`",
        f"- Version: `{bundle.get('version_label')}`",
        f"- Commit: `{bundle.get('commit')}`",
        f"- Status: `{bundle.get('status')}`",
        "",
        "## Checks",
        "",
        "| Check | Status | Details |",
        "| --- | --- | --- |",
    ]
    for check in bundle.get("checks", []):
        lines.append(
            "| "
            + " | ".join(_markdown_cell(value) for value in (check.get("label"), check.get("status"), check.get("details")))
            + " |"
        )

    lines.extend(["", "## Non-Pass Runtime Lanes", "", "| Lane | Status | Reason |", "| --- | --- | --- |"])
    for lane in bundle.get("non_pass_lanes", []):
        lines.append(
            "| "
            + " | ".join(_markdown_cell(value) for value in (lane.get("label"), lane.get("status"), lane.get("reason")))
            + " |"
        )

    lines.extend(["", "## Notes", ""])
    for note in bundle.get("notes", []):
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify a DecisionAtlas self-hosted package directory.")
    parser.add_argument("--package", type=Path, required=True, help="Package directory to verify.")
    parser.add_argument("--output-json", type=Path, default=Path(".tmp/self-hosted-package-verification.json"))
    parser.add_argument("--output-markdown", type=Path, default=Path(".tmp/self-hosted-package-verification.md"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    package_dir = args.package if args.package.is_absolute() else root / args.package
    bundle = verify_package(package_dir)
    output_json = args.output_json if args.output_json.is_absolute() else root / args.output_json
    output_markdown = args.output_markdown if args.output_markdown.is_absolute() else root / args.output_markdown
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(bundle, indent=2, sort_keys=True), encoding="utf-8")
    output_markdown.write_text(render_markdown(bundle), encoding="utf-8")
    print(json.dumps(bundle, indent=2, sort_keys=True))
    return 0 if bundle["status"] == STATUS_PASS else 1


if __name__ == "__main__":
    raise SystemExit(main())
