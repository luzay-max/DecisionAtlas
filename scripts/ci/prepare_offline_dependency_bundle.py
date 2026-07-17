from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any

from offline_dependency_bundle import (
    BUNDLE_TYPE,
    CHECKSUM_FILENAME,
    MANIFEST_FILENAME,
    REQUIRED_CATEGORIES,
    SBOM_FILENAME,
    SCHEMA_VERSION,
    build_offline_sbom,
    category_summaries,
    compose_images,
    current_tool_versions,
    generated_at,
    inventory_payload,
    json_bytes,
    package_bindings,
    platform_contract,
    reset_owned_directory,
    run_command,
    sanitize_text,
    write_checksums,
    uv_command,
)
from verify_self_hosted_package import verify_package


def _bounded_command(
    result: dict[str, Any],
    command_id: str,
    *,
    replacements: dict[str, str] | None = None,
) -> dict[str, Any]:
    return {
        "id": command_id,
        "status": result.get("status", "blocking"),
        "returncode": result.get("returncode"),
        "duration_seconds": result.get("duration_seconds"),
        "stdout_tail": sanitize_text(str(result.get("stdout_tail", "")), replacements=replacements),
        "stderr_tail": sanitize_text(str(result.get("stderr_tail", "")), replacements=replacements),
        **(
            {"error": sanitize_text(str(result["error"]), replacements=replacements)}
            if result.get("error")
            else {}
        ),
    }


def _inspect_image(
    reference: str,
    package_dir: Path,
    runner,
    *,
    replacements: dict[str, str] | None = None,
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    result = runner(
        [
            "docker",
            "image",
            "inspect",
            reference,
            "--format",
            '{"Id":"{{.Id}}","RepoDigests":{{json .RepoDigests}}}',
        ],
        cwd=package_dir,
        timeout_seconds=120,
    )
    bounded = _bounded_command(result, f"inspect_container:{reference}", replacements=replacements)
    if result.get("status") != "pass":
        return None, bounded
    try:
        data = json.loads(str(result.get("stdout_tail", "")).strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError):
        bounded["status"] = "blocking"
        bounded["error"] = "container_inspect_output_invalid"
        return None, bounded
    image_id = data.get("Id")
    if not isinstance(image_id, str) or not image_id.startswith("sha256:"):
        bounded["status"] = "blocking"
        bounded["error"] = "container_image_id_missing"
        return None, bounded
    return {
        "reference": reference,
        "image_id": image_id,
        "repo_digests": sorted(item for item in data.get("RepoDigests", []) if isinstance(item, str)),
    }, bounded


def prepare_bundle(
    *,
    package_dir: Path,
    output_dir: Path,
    command_runner=run_command,
    generated_at_value: str | None = None,
    timeout_seconds: int = 1800,
) -> dict[str, Any]:
    package_dir = package_dir.resolve()
    output_dir = output_dir.resolve()
    package_report = verify_package(package_dir, generated_at=generated_at_value)
    if package_report.get("status") != "pass":
        return {
            "schema_version": SCHEMA_VERSION,
            "evidence_type": "offline-dependency-bundle-preparation",
            "generated_at": generated_at(generated_at_value),
            "status": "blocking",
            "bundle_created": False,
            "blockers": [{"id": "package_verification", "reason": "package_not_runnable"}],
            "commands": [],
        }

    package_manifest = json.loads((package_dir / "manifest.json").read_text(encoding="utf-8"))
    bindings = package_bindings(package_dir)
    images = compose_images(package_dir / "docker-compose.yml")
    owned_root = output_dir.parent
    owned_root.mkdir(parents=True, exist_ok=True)
    staging = owned_root / f".{output_dir.name}.staging"
    reset_owned_directory(staging, owned_root)
    prepare_package = staging / ".prepare-package"
    replacements = {
        str(package_dir): "<self-hosted-package>",
        str(output_dir): "<offline-bundle>",
        str(staging): "<offline-bundle-staging>",
        str(prepare_package): "<prepare-package>",
    }
    commands: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    image_records: list[dict[str, Any]] = []

    try:
        tool_versions = current_tool_versions(package_dir, command_runner)
        shutil.copytree(package_dir, prepare_package)
        pnpm_store = staging / REQUIRED_CATEGORIES["pnpm_store"]
        uv_cache = staging / REQUIRED_CATEGORIES["uv_cache"]
        browser_path = staging / REQUIRED_CATEGORIES["playwright_browsers"]
        image_tar = staging / REQUIRED_CATEGORIES["container_images"]
        for path in (pnpm_store, uv_cache, browser_path, image_tar.parent):
            path.mkdir(parents=True, exist_ok=True)

        steps = [
            (
                "pnpm_fetch",
                ["pnpm", "fetch", "--frozen-lockfile", "--store-dir", str(pnpm_store)],
                os.environ.copy(),
            ),
        ]
        uv_env = os.environ.copy()
        uv_env["UV_PROJECT_ENVIRONMENT"] = str(staging / ".prepare-venv")
        uv_env["UV_CACHE_DIR"] = str(uv_cache)
        steps.append(
            (
                "uv_sync_cache",
                uv_command(
                    "sync",
                    "--project",
                    "services/engine",
                    "--frozen",
                    "--no-install-project",
                    "--no-python-downloads",
                    "--cache-dir",
                    str(uv_cache),
                ),
                uv_env,
            )
        )
        steps.insert(
            1,
            (
                "pnpm_prepare_install",
                ["pnpm", "install", "--offline", "--frozen-lockfile", "--store-dir", str(pnpm_store)],
                os.environ.copy(),
            ),
        )
        browser_env = os.environ.copy()
        browser_env["PLAYWRIGHT_BROWSERS_PATH"] = str(browser_path)
        steps.append(
            (
                "playwright_install",
                ["pnpm", "--filter", "@decisionatlas/web", "exec", "playwright", "install", "chromium"],
                browser_env,
            )
        )

        for step_id, command, env in steps:
            result = command_runner(command, cwd=prepare_package, env=env, timeout_seconds=timeout_seconds)
            commands.append(_bounded_command(result, step_id, replacements=replacements))
            if result.get("status") != "pass":
                blockers.append({"id": step_id, "reason": "command_failed"})
                break

        if not blockers:
            for image in images:
                result = command_runner(["docker", "pull", image], cwd=prepare_package, timeout_seconds=timeout_seconds)
                commands.append(
                    _bounded_command(result, f"pull_container:{image}", replacements=replacements)
                )
                if result.get("status") != "pass":
                    blockers.append({"id": f"pull_container:{image}", "reason": "command_failed"})
                    break
                record, bounded = _inspect_image(
                    image,
                    prepare_package,
                    command_runner,
                    replacements=replacements,
                )
                commands.append(bounded)
                if record is None:
                    blockers.append({"id": f"inspect_container:{image}", "reason": "invalid_image_identity"})
                    break
                image_records.append(record)

        if not blockers:
            result = command_runner(
                ["docker", "image", "save", "-o", str(image_tar), *images],
                cwd=prepare_package,
                timeout_seconds=timeout_seconds,
            )
            commands.append(
                _bounded_command(result, "save_container_images", replacements=replacements)
            )
            if result.get("status") != "pass":
                blockers.append({"id": "save_container_images", "reason": "command_failed"})

        shutil.rmtree(staging / ".prepare-venv", ignore_errors=True)
        shutil.rmtree(prepare_package, ignore_errors=True)
        if blockers:
            raise RuntimeError("offline_bundle_preparation_failed")

        inventory, payload_digest, payload_size = inventory_payload(staging)
        summaries = category_summaries(inventory)
        empty_categories = [name for name, item in summaries.items() if item["file_count"] == 0]
        if empty_categories:
            blockers.extend({"id": f"category:{name}", "reason": "category_empty"} for name in empty_categories)
            raise RuntimeError("offline_bundle_category_empty")

        sbom = build_offline_sbom(
            package_dir=package_dir,
            package_manifest=package_manifest,
            payload_digest=payload_digest,
            images=image_records,
        )
        (staging / SBOM_FILENAME).write_bytes(json_bytes(sbom))
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "bundle_type": BUNDLE_TYPE,
            "generated_at": generated_at(generated_at_value),
            "status": "pass",
            "package": {
                "version_label": package_manifest.get("version_label"),
                "commit": package_manifest.get("commit"),
                "bindings": bindings,
            },
            "platform_contract": platform_contract(tool_versions),
            "categories": summaries,
            "container_images": image_records,
            "inventory": inventory,
            "payload_content_sha256": payload_digest,
            "payload_file_count": len(inventory),
            "payload_size": payload_size,
            "sbom_filename": SBOM_FILENAME,
            "checksum_filename": CHECKSUM_FILENAME,
            "proof_boundary": {
                "offline_control": "package_manager_offline_flags_and_blackhole_proxy",
                "physical_air_gap": "not_proven",
                "customer_host_installation": "not_proven",
                "cryptographic_signing": "not_provided",
                "vulnerability_analysis": "not_provided",
                "cross_platform_portability": "not_supported",
            },
        }
        (staging / MANIFEST_FILENAME).write_bytes(json_bytes(manifest))
        checksum_paths = [staging / MANIFEST_FILENAME, staging / SBOM_FILENAME]
        checksum_paths.extend(staging / item["path"] for item in inventory)
        write_checksums(staging, checksum_paths)

        if output_dir.exists():
            if not output_dir.is_dir() or any(output_dir.iterdir()):
                raise ValueError("Offline bundle output directory already exists and is not empty.")
            output_dir.rmdir()
        staging.rename(output_dir)
        return {
            "schema_version": SCHEMA_VERSION,
            "evidence_type": "offline-dependency-bundle-preparation",
            "generated_at": manifest["generated_at"],
            "status": "pass",
            "bundle_created": True,
            "bundle_path": "<operator-selected-offline-bundle>",
            "package_version": package_manifest.get("version_label"),
            "package_commit": package_manifest.get("commit"),
            "platform_contract": manifest["platform_contract"],
            "categories": summaries,
            "payload_file_count": len(inventory),
            "payload_size": payload_size,
            "payload_content_sha256": payload_digest,
            "sbom_component_count": len(sbom["components"]),
            "container_images": image_records,
            "commands": commands,
            "blockers": [],
            "warnings": [
                "The bundle is platform/toolchain specific and does not include Node, Python, pnpm, uv, Docker, or the operating system.",
                "Checksums do not authenticate the publisher; signing and vulnerability analysis are not provided.",
            ],
            "host_proof_level": "offline_dependency_bundle_prepared",
            "is_customer_controlled": False,
        }
    except (OSError, ValueError, RuntimeError) as exc:
        shutil.rmtree(staging, ignore_errors=True)
        if not blockers:
            blockers.append(
                {
                    "id": "preparation_exception",
                    "reason": sanitize_text(str(exc), replacements=replacements),
                }
            )
        return {
            "schema_version": SCHEMA_VERSION,
            "evidence_type": "offline-dependency-bundle-preparation",
            "generated_at": generated_at(generated_at_value),
            "status": "blocking",
            "bundle_created": False,
            "commands": commands,
            "blockers": blockers,
        }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Offline Dependency Bundle Preparation",
        "",
        f"- Status: `{report['status']}`",
        f"- Package: `{report.get('package_version')}`",
        f"- Commit: `{report.get('package_commit')}`",
        f"- Proof level: `{report.get('host_proof_level', 'not_ready')}`",
        "- Customer controlled: `false`",
        "",
        "## Categories",
        "",
        "| Category | Files | Size |",
        "| --- | ---: | ---: |",
    ]
    for name, item in sorted(report.get("categories", {}).items()):
        lines.append(f"| {name} | {item.get('file_count', 0)} | {item.get('size', 0)} |")
    lines.extend(["", "## Blockers", ""])
    blockers = report.get("blockers", [])
    lines.extend(f"- `{item.get('id')}`: {item.get('reason')}" for item in blockers)
    if not blockers:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Boundaries",
            "",
            "- Tool-native caches are platform and toolchain specific.",
            "- Process-enforced offline installation is not physical air-gap or customer-host proof.",
            "- Signing and vulnerability analysis are not provided.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare approved DecisionAtlas offline dependency caches.")
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, default=Path(".tmp/offline-dependency-preparation.json"))
    parser.add_argument("--output-markdown", type=Path, default=Path(".tmp/offline-dependency-preparation.md"))
    parser.add_argument("--generated-at", default=None)
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    package_dir = args.package if args.package.is_absolute() else root / args.package
    output_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    report = prepare_bundle(
        package_dir=package_dir,
        output_dir=output_dir,
        generated_at_value=args.generated_at,
        timeout_seconds=args.timeout_seconds,
    )
    output_json = args.output_json if args.output_json.is_absolute() else root / args.output_json
    output_markdown = args.output_markdown if args.output_markdown.is_absolute() else root / args.output_markdown
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_bytes(json_bytes(report))
    write_markdown(output_markdown, report)
    print(f"Offline dependency preparation status: {report['status']}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
