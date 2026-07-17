from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any

from offline_dependency_bundle import (
    BUNDLE_TYPE,
    CHECKSUM_FILENAME,
    MANIFEST_FILENAME,
    REQUIRED_CATEGORIES,
    SBOM_FILENAME,
    SCHEMA_VERSION,
    category_for_path,
    current_tool_versions,
    inventory_payload,
    json_bytes,
    load_json,
    package_bindings,
    parse_checksums,
    platform_contract,
    safe_relative_path,
    sha256_path,
)
from verify_self_hosted_package import verify_package


def _check(check_id: str, label: str, status: str, **details: Any) -> dict[str, Any]:
    return {"id": check_id, "label": label, "status": status, "details": details}


def _pass(check_id: str, label: str, **details: Any) -> dict[str, Any]:
    return _check(check_id, label, "pass", **details)


def _blocking(check_id: str, label: str, **details: Any) -> dict[str, Any]:
    return _check(check_id, label, "blocking", **details)


def _safe_files(bundle_dir: Path) -> tuple[dict[str, Path], list[dict[str, Any]]]:
    files: dict[str, Path] = {}
    violations: list[dict[str, Any]] = []
    seen_casefold: set[str] = set()
    for path in sorted(bundle_dir.rglob("*"), key=lambda item: item.relative_to(bundle_dir).as_posix()):
        relative = path.relative_to(bundle_dir).as_posix()
        if path.is_symlink():
            violations.append({"path": relative, "reason": "symbolic_link"})
            continue
        if not path.is_file():
            continue
        try:
            safe_relative_path(relative)
        except ValueError as exc:
            violations.append({"path": relative, "reason": str(exc)})
            continue
        folded = relative.casefold()
        if folded in seen_casefold:
            violations.append({"path": relative, "reason": "casefold_collision"})
            continue
        seen_casefold.add(folded)
        files[relative] = path
    return files, violations


def _sbom_valid(sbom: dict[str, Any]) -> tuple[bool, dict[str, int]]:
    components = sbom.get("components")
    metadata = sbom.get("metadata")
    if not isinstance(components, list):
        return False, {"components": 0, "npm": 0, "pypi": 0, "containers": 0}
    refs = [item.get("bom-ref") for item in components if isinstance(item, dict)]
    valid = (
        sbom.get("bomFormat") == "CycloneDX"
        and sbom.get("specVersion") == "1.6"
        and isinstance(metadata, dict)
        and bool(components)
        and len(refs) == len(components)
        and len(refs) == len(set(refs))
        and all(
            isinstance(item, dict)
            and item.get("name")
            and item.get("version")
            and item.get("bom-ref")
            for item in components
        )
    )
    return valid, {
        "components": len(components),
        "npm": sum(1 for item in components if str(item.get("purl", "")).startswith("pkg:npm/")),
        "pypi": sum(1 for item in components if str(item.get("purl", "")).startswith("pkg:pypi/")),
        "containers": sum(1 for item in components if item.get("type") == "container"),
    }


def verify_bundle(
    *,
    bundle_dir: Path,
    package_dir: Path,
    generated_at_value: str | None = None,
    actual_platform_contract: dict[str, Any] | None = None,
    command_runner=None,
) -> dict[str, Any]:
    bundle_dir = bundle_dir.resolve()
    package_dir = package_dir.resolve()
    checks: list[dict[str, Any]] = []

    package_report = verify_package(package_dir, generated_at=generated_at_value)
    checks.append(
        _pass("package_verification", "Selected package passes verifier")
        if package_report.get("status") == "pass"
        else _blocking("package_verification", "Selected package passes verifier", blocker_count=len(package_report.get("blockers", [])))
    )

    files, violations = _safe_files(bundle_dir) if bundle_dir.is_dir() else ({}, [{"reason": "bundle_missing"}])
    checks.append(
        _pass("bundle_paths", "Bundle paths are safe", file_count=len(files))
        if not violations
        else _blocking("bundle_paths", "Bundle paths are safe", violations=violations[:20])
    )

    manifest: dict[str, Any] | None = None
    sbom: dict[str, Any] | None = None
    checksums: dict[str, str] = {}
    try:
        manifest = load_json(bundle_dir / MANIFEST_FILENAME)
        checks.append(_pass("manifest_json", "Bundle manifest is readable"))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        checks.append(_blocking("manifest_json", "Bundle manifest is readable", reason=str(exc)))
    try:
        sbom = load_json(bundle_dir / SBOM_FILENAME)
        checks.append(_pass("sbom_json", "Bundle SBOM is readable"))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        checks.append(_blocking("sbom_json", "Bundle SBOM is readable", reason=str(exc)))
    try:
        checksums = parse_checksums(bundle_dir / CHECKSUM_FILENAME)
        checks.append(_pass("checksums_parse", "SHA256SUMS is readable", entry_count=len(checksums)))
    except (OSError, ValueError) as exc:
        checks.append(_blocking("checksums_parse", "SHA256SUMS is readable", reason=str(exc)))

    if manifest is None:
        return _report(checks, manifest, {}, generated_at_value)

    identity_ok = (
        manifest.get("schema_version") == SCHEMA_VERSION
        and manifest.get("bundle_type") == BUNDLE_TYPE
        and manifest.get("status") == "pass"
    )
    checks.append(
        _pass("manifest_identity", "Bundle manifest identity is valid")
        if identity_ok
        else _blocking("manifest_identity", "Bundle manifest identity is valid")
    )

    expected_checksum_files = set(files) - {CHECKSUM_FILENAME}
    checksum_coverage = set(checksums) == expected_checksum_files
    checksum_mismatches = [
        relative
        for relative in sorted(set(checksums) & set(files))
        if sha256_path(files[relative]) != checksums[relative]
    ]
    checks.append(
        _pass("checksum_coverage", "Checksums cover exactly every retained file", entry_count=len(checksums))
        if checksum_coverage and not checksum_mismatches
        else _blocking(
            "checksum_coverage",
            "Checksums cover exactly every retained file",
            missing=sorted(expected_checksum_files - set(checksums))[:20],
            unexpected=sorted(set(checksums) - expected_checksum_files)[:20],
            mismatched=checksum_mismatches[:20],
        )
    )

    inventory = manifest.get("inventory")
    inventory_items = inventory if isinstance(inventory, list) else []
    try:
        actual_inventory, actual_digest, actual_size = inventory_payload(bundle_dir)
    except ValueError as exc:
        actual_inventory, actual_digest, actual_size = [], "", 0
        checks.append(_blocking("payload_inventory", "Payload inventory is safe and readable", reason=str(exc)))
    else:
        inventory_ok = (
            inventory_items == actual_inventory
            and manifest.get("payload_content_sha256") == actual_digest
            and manifest.get("payload_file_count") == len(actual_inventory)
            and manifest.get("payload_size") == actual_size
        )
        checks.append(
            _pass("payload_inventory", "Payload inventory matches manifest", file_count=len(actual_inventory), size=actual_size)
            if inventory_ok
            else _blocking("payload_inventory", "Payload inventory matches manifest")
        )

    categories = manifest.get("categories")
    category_data = categories if isinstance(categories, dict) else {}
    missing_categories = []
    for name, expected_path in REQUIRED_CATEGORIES.items():
        item = category_data.get(name)
        if not isinstance(item, dict) or item.get("path") != expected_path or not isinstance(item.get("file_count"), int) or item.get("file_count", 0) <= 0:
            missing_categories.append(name)
    checks.append(
        _pass("category_completeness", "All approved cache categories are present", categories=sorted(category_data))
        if not missing_categories and set(category_data) == set(REQUIRED_CATEGORIES)
        else _blocking("category_completeness", "All approved cache categories are present", missing=missing_categories)
    )

    package_data = manifest.get("package")
    expected_bindings = package_data.get("bindings") if isinstance(package_data, dict) else None
    try:
        actual_bindings = package_bindings(package_dir)
    except ValueError as exc:
        actual_bindings = {}
        checks.append(_blocking("package_bindings", "Bundle is bound to selected package", reason=str(exc)))
    else:
        checks.append(
            _pass("package_bindings", "Bundle is bound to selected package", files=sorted(actual_bindings))
            if expected_bindings == actual_bindings
            else _blocking(
                "package_bindings",
                "Bundle is bound to selected package",
                mismatched=sorted(
                    key for key in set(actual_bindings) | set(expected_bindings or {})
                    if actual_bindings.get(key) != (expected_bindings or {}).get(key)
                ),
            )
        )

    expected_contract = manifest.get("platform_contract")
    try:
        if actual_platform_contract is None:
            versions = current_tool_versions(package_dir, command_runner) if command_runner else current_tool_versions(package_dir)
            actual_platform_contract = platform_contract(versions)
    except ValueError as exc:
        actual_platform_contract = {}
        checks.append(_blocking("platform_contract", "Consumer platform matches bundle", reason=str(exc)))
    else:
        mismatches = sorted(
            key
            for key in set(expected_contract or {}) | set(actual_platform_contract or {})
            if (expected_contract or {}).get(key) != (actual_platform_contract or {}).get(key)
        )
        checks.append(
            _pass("platform_contract", "Consumer platform matches bundle")
            if not mismatches
            else _blocking("platform_contract", "Consumer platform matches bundle", mismatched=mismatches)
        )

    sbom_summary: dict[str, int] = {}
    if sbom is not None:
        valid_sbom, sbom_summary = _sbom_valid(sbom)
        container_count = len(manifest.get("container_images", [])) if isinstance(manifest.get("container_images"), list) else 0
        valid_sbom = valid_sbom and sbom_summary.get("containers") == container_count
        checks.append(
            _pass("sbom_structure", "CycloneDX SBOM is valid", **sbom_summary)
            if valid_sbom
            else _blocking("sbom_structure", "CycloneDX SBOM is valid", **sbom_summary)
        )

    return _report(checks, manifest, sbom_summary, generated_at_value)


def _report(
    checks: list[dict[str, Any]],
    manifest: dict[str, Any] | None,
    sbom_summary: dict[str, int],
    generated_at_value: str | None,
) -> dict[str, Any]:
    blockers = [item for item in checks if item["status"] == "blocking"]
    package = manifest.get("package", {}) if manifest else {}
    return {
        "schema_version": SCHEMA_VERSION,
        "evidence_type": "offline-dependency-bundle-verification",
        "generated_at": generated_at_value or datetime.now(UTC).isoformat(),
        "status": "blocking" if blockers else "pass",
        "bundle_path": "<operator-selected-offline-bundle>",
        "package_path": "<operator-selected-self-hosted-package>",
        "package_version": package.get("version_label"),
        "package_commit": package.get("commit"),
        "platform_contract": manifest.get("platform_contract") if manifest else None,
        "categories": manifest.get("categories", {}) if manifest else {},
        "payload_content_sha256": manifest.get("payload_content_sha256") if manifest else None,
        "payload_file_count": manifest.get("payload_file_count", 0) if manifest else 0,
        "payload_size": manifest.get("payload_size", 0) if manifest else 0,
        "sbom": sbom_summary,
        "container_images": manifest.get("container_images", []) if manifest else [],
        "checks": checks,
        "blockers": blockers,
        "warnings": [
            "Process-enforced offline installation is not physical air-gap or customer-controlled-host proof.",
            "Checksums do not authenticate the publisher; signing and vulnerability analysis are not provided.",
        ],
        "host_proof_level": "offline_dependency_bundle_verified",
        "is_customer_controlled": False,
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Offline Dependency Bundle Verification",
        "",
        f"- Status: `{report['status']}`",
        f"- Package: `{report.get('package_version')}`",
        f"- Commit: `{report.get('package_commit')}`",
        f"- Payload files: `{report.get('payload_file_count', 0)}`",
        f"- Payload size: `{report.get('payload_size', 0)}`",
        f"- Proof level: `{report['host_proof_level']}`",
        "- Customer controlled: `false`",
        "",
        "## Checks",
        "",
        "| Check | Status |",
        "| --- | --- |",
    ]
    lines.extend(f"| {item['label']} | `{item['status']}` |" for item in report["checks"])
    lines.extend(["", "## Boundaries", ""])
    lines.extend(f"- {warning}" for warning in report["warnings"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify an approved DecisionAtlas offline dependency bundle.")
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, default=Path(".tmp/offline-dependency-verification.json"))
    parser.add_argument("--output-markdown", type=Path, default=Path(".tmp/offline-dependency-verification.md"))
    parser.add_argument("--generated-at", default=None)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    bundle_dir = args.bundle if args.bundle.is_absolute() else root / args.bundle
    package_dir = args.package if args.package.is_absolute() else root / args.package
    report = verify_bundle(
        bundle_dir=bundle_dir,
        package_dir=package_dir,
        generated_at_value=args.generated_at,
    )
    output_json = args.output_json if args.output_json.is_absolute() else root / args.output_json
    output_markdown = args.output_markdown if args.output_markdown.is_absolute() else root / args.output_markdown
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_bytes(json_bytes(report))
    write_markdown(output_markdown, report)
    print(f"Offline dependency verification status: {report['status']}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
