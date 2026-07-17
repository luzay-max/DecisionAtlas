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
    REQUIRED_CATEGORIES,
    json_bytes,
    reset_owned_directory,
    run_command,
    sanitize_text,
    uv_command,
)
from verify_offline_dependency_bundle import verify_bundle


STATUS_PASS = "pass"
STATUS_BLOCKING = "blocking"
STATUS_NOT_REQUESTED = "not_requested"


def _stage(stage_id: str, label: str, status: str, **details: Any) -> dict[str, Any]:
    return {"id": stage_id, "label": label, "status": status, **details}


def _offline_env(bundle_copy: Path) -> dict[str, str]:
    env = os.environ.copy()
    blackhole = "http://127.0.0.1:9"
    for name in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
        env[name] = blackhole
    env["NO_PROXY"] = "127.0.0.1,localhost"
    env["no_proxy"] = "127.0.0.1,localhost"
    env["NPM_CONFIG_OFFLINE"] = "true"
    env["UV_OFFLINE"] = "1"
    env["UV_PYTHON_DOWNLOADS"] = "never"
    env["PLAYWRIGHT_BROWSERS_PATH"] = str(bundle_copy / REQUIRED_CATEGORIES["playwright_browsers"])
    env["UV_CACHE_DIR"] = str(bundle_copy / REQUIRED_CATEGORIES["uv_cache"])
    env["DECISIONATLAS_OFFLINE_INSTALL"] = "1"
    return env


def _live_env(offline_env: dict[str, str], repo: str) -> dict[str, str]:
    env = offline_env.copy()
    for name in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy", "NPM_CONFIG_OFFLINE", "UV_OFFLINE", "DECISIONATLAS_OFFLINE_INSTALL"):
        env.pop(name, None)
    env["NO_PROXY"] = "127.0.0.1,localhost"
    env["no_proxy"] = "127.0.0.1,localhost"
    env["PLAYWRIGHT_REAL_PUBLIC_REPO"] = repo
    return env


def _bounded_result(
    result: dict[str, Any],
    *,
    command_id: str,
    package_copy: Path,
    bundle_copy: Path,
) -> dict[str, Any]:
    replacements = {
        str(package_copy): "<isolated-package>",
        package_copy.as_posix(): "<isolated-package>",
        str(bundle_copy): "<isolated-offline-bundle>",
        bundle_copy.as_posix(): "<isolated-offline-bundle>",
    }
    return {
        "id": command_id,
        "status": result.get("status", STATUS_BLOCKING),
        "returncode": result.get("returncode"),
        "duration_seconds": result.get("duration_seconds"),
        "stdout_tail": sanitize_text(str(result.get("stdout_tail", "")), replacements=replacements),
        "stderr_tail": sanitize_text(str(result.get("stderr_tail", "")), replacements=replacements),
        **({"error": sanitize_text(str(result["error"]), replacements=replacements)} if result.get("error") else {}),
    }


def rehearse_offline_install(args: argparse.Namespace, root: Path, command_runner=run_command) -> dict[str, Any]:
    source_package = (args.package if args.package.is_absolute() else root / args.package).resolve()
    source_bundle = (args.bundle if args.bundle.is_absolute() else root / args.bundle).resolve()
    scratch_root = (
        (args.scratch_root if args.scratch_root.is_absolute() else root / args.scratch_root).resolve()
        if args.scratch_root
        else Path(tempfile.gettempdir()).resolve() / "decisionatlas-offline-install-rehearsal"
    )
    rehearsal_root = scratch_root / args.label
    package_copy = rehearsal_root / "package-copy"
    bundle_copy = rehearsal_root / "offline-bundle-copy"
    scratch_root.mkdir(parents=True, exist_ok=True)
    reset_owned_directory(rehearsal_root, scratch_root)
    stages: list[dict[str, Any]] = []
    commands: list[dict[str, Any]] = []

    try:
        shutil.copytree(source_package, package_copy)
        shutil.copytree(source_bundle, bundle_copy)
    except OSError as exc:
        stages.append(_stage("copy_inputs", "Copy package and offline bundle into isolated root", STATUS_BLOCKING, reason=sanitize_text(str(exc))))
    else:
        stages.append(_stage("copy_inputs", "Copy package and offline bundle into isolated root", STATUS_PASS))

    verification = (
        verify_bundle(bundle_dir=bundle_copy, package_dir=package_copy, generated_at_value=args.generated_at)
        if package_copy.exists() and bundle_copy.exists()
        else {"status": STATUS_BLOCKING, "blockers": [{"id": "copy_inputs"}]}
    )
    stages.append(
        _stage(
            "verify_bundle",
            "Verify copied package and offline dependency bundle",
            verification.get("status", STATUS_BLOCKING),
            blocker_ids=[item.get("id") for item in verification.get("blockers", [])[:20]],
        )
    )
    can_run = verification.get("status") == STATUS_PASS
    offline_env = _offline_env(bundle_copy)

    def execute(
        command_id: str,
        command: list[str],
        *,
        env: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> dict[str, Any]:
        if not can_run:
            return {"id": command_id, "status": STATUS_BLOCKING, "error": "bundle_verification_failed"}
        result = command_runner(
            command,
            cwd=package_copy,
            env=env,
            timeout_seconds=timeout or args.install_timeout_seconds,
        )
        bounded = _bounded_result(
            result,
            command_id=command_id,
            package_copy=package_copy,
            bundle_copy=bundle_copy,
        )
        commands.append(bounded)
        return bounded

    image_tar = bundle_copy / REQUIRED_CATEGORIES["container_images"]
    container_status = execute(
        "load_container_images",
        ["docker", "image", "load", "-i", str(image_tar)],
        env=offline_env,
    )["status"]
    manifest = json.loads((bundle_copy / "offline-dependency-bundle.json").read_text(encoding="utf-8")) if can_run else {}
    if container_status == STATUS_PASS:
        for image in manifest.get("container_images", []):
            inspect_result = execute(
                f"inspect_container:{image.get('reference')}",
                ["docker", "image", "inspect", str(image.get("reference")), "--format", "{{.Id}}"],
                env=offline_env,
                timeout=120,
            )
            actual_image_id = str(inspect_result.get("stdout_tail", "")).strip().splitlines()[-1:]
            actual_image_id = actual_image_id[0] if actual_image_id else ""
            expected_image_id = str(image.get("image_id", ""))
            if inspect_result["status"] != STATUS_PASS or actual_image_id != expected_image_id:
                inspect_result["status"] = STATUS_BLOCKING
                inspect_result["error"] = "loaded_container_image_identity_mismatch"
                container_status = STATUS_BLOCKING
                break
    stages.append(
        _stage(
            "container_images",
            "Load and inspect bundled container images without registry pulls",
            container_status,
            image_count=len(manifest.get("container_images", [])),
            pull_policy="never",
        )
    )

    pnpm_status = execute(
        "pnpm_offline_install",
        [
            "pnpm",
            "install",
            "--offline",
            "--frozen-lockfile",
            "--store-dir",
            str(bundle_copy / REQUIRED_CATEGORIES["pnpm_store"]),
        ],
        env=offline_env,
    )["status"]
    stages.append(
        _stage(
            "pnpm_offline_install",
            "Install Node dependencies from bundled pnpm store",
            pnpm_status,
            offline_flag=True,
        )
    )

    uv_env = offline_env.copy()
    uv_env["UV_PROJECT_ENVIRONMENT"] = str(package_copy / "services/engine/.venv")
    uv_status = (
        execute(
            "uv_offline_sync",
            uv_command(
                "sync",
                "--project",
                "services/engine",
                "--offline",
                "--frozen",
                "--no-python-downloads",
                "--cache-dir",
                str(bundle_copy / REQUIRED_CATEGORIES["uv_cache"]),
            ),
            env=uv_env,
        )["status"]
        if pnpm_status == STATUS_PASS
        else STATUS_BLOCKING
    )
    stages.append(
        _stage(
            "uv_offline_sync",
            "Install Python dependencies from bundled uv cache",
            uv_status,
            offline_flag=True,
        )
    )

    shell_status = (
        execute(
            "offline_browser_shell",
            [
                "pnpm",
                "--filter",
                "@decisionatlas/web",
                "exec",
                "playwright",
                "test",
                "tests-e2e/offline-package-shell.spec.ts",
                "--workers=1",
            ],
            env=uv_env,
            timeout=args.smoke_timeout_seconds,
        )["status"]
        if uv_status == STATUS_PASS and container_status == STATUS_PASS
        else STATUS_BLOCKING
    )
    stages.append(
        _stage(
            "offline_browser_shell",
            "Start Engine/API/Web and run local-only browser shell",
            shell_status,
            network_control="package_manager_offline_flags_and_blackhole_proxy",
            external_browser_requests_allowed=False,
        )
    )

    live_status = STATUS_NOT_REQUESTED
    if args.run_live_repo and shell_status == STATUS_PASS:
        live_status = execute(
            "live_repository_browser",
            [
                "pnpm",
                "--filter",
                "@decisionatlas/web",
                "exec",
                "playwright",
                "test",
                "tests-e2e/imported-workspace-core-loop.spec.ts",
                "--workers=1",
            ],
            env=_live_env(uv_env, args.repo),
            timeout=args.smoke_timeout_seconds,
        )["status"]
    elif args.run_live_repo:
        live_status = STATUS_BLOCKING
    stages.append(
        _stage(
            "live_repository_browser",
            "Run separately labelled live-network public repository core loop",
            live_status,
            requested=bool(args.run_live_repo),
            repository=args.repo if args.run_live_repo else None,
        )
    )

    required = [stage for stage in stages if stage["id"] != "live_repository_browser" or args.run_live_repo]
    status = STATUS_BLOCKING if any(stage["status"] == STATUS_BLOCKING for stage in required) else STATUS_PASS
    return {
        "schema_version": 1,
        "evidence_type": "offline-self-hosted-install-rehearsal",
        "generated_at": args.generated_at or datetime.now(UTC).isoformat(),
        "status": status,
        "label": args.label,
        "package_version": manifest.get("package", {}).get("version_label"),
        "package_commit": manifest.get("package", {}).get("commit"),
        "package_path": "<isolated-self-hosted-package>",
        "bundle_path": "<isolated-offline-dependency-bundle>",
        "repository": args.repo if args.run_live_repo else None,
        "host_proof_level": "process_enforced_offline_install" if status == STATUS_PASS else "offline_install_not_clean",
        "is_customer_controlled": False,
        "offline_controls": {
            "pnpm_offline": True,
            "uv_offline": True,
            "blackhole_proxy": "http://127.0.0.1:9",
            "localhost_exempt": True,
            "playwright_browser_path": "<isolated-offline-bundle>/payload/playwright/browsers",
            "container_pull_policy": "never",
            "kernel_network_namespace": False,
        },
        "stages": stages,
        "commands": commands,
        "blockers": [stage for stage in required if stage["status"] == STATUS_BLOCKING],
        "warnings": [
            "Windows process-level offline controls are not proof of a physical air gap.",
            "Maintainer or CI rehearsal is not customer-controlled-host proof.",
        ],
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Offline Self-Hosted Install Rehearsal",
        "",
        f"- Status: `{report['status']}`",
        f"- Package: `{report.get('package_version')}`",
        f"- Commit: `{report.get('package_commit')}`",
        f"- Proof level: `{report['host_proof_level']}`",
        "- Customer controlled: `false`",
        "",
        "## Stages",
        "",
        "| Stage | Status |",
        "| --- | --- |",
    ]
    lines.extend(f"| {stage['label']} | `{stage['status']}` |" for stage in report["stages"])
    lines.extend(["", "## Boundaries", ""])
    lines.extend(f"- {warning}" for warning in report["warnings"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rehearse DecisionAtlas installation from an approved offline dependency bundle.")
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--scratch-root", type=Path, default=None)
    parser.add_argument("--label", default="offline-self-hosted-install")
    parser.add_argument("--repo", default="pallets/markupsafe")
    parser.add_argument("--run-live-repo", action="store_true")
    parser.add_argument("--install-timeout-seconds", type=int, default=1800)
    parser.add_argument("--smoke-timeout-seconds", type=int, default=600)
    parser.add_argument("--generated-at", default=None)
    parser.add_argument("--output-json", type=Path, default=Path(".tmp/offline-self-hosted-install-rehearsal.json"))
    parser.add_argument("--output-markdown", type=Path, default=Path(".tmp/offline-self-hosted-install-rehearsal.md"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    report = rehearse_offline_install(args, root)
    output_json = args.output_json if args.output_json.is_absolute() else root / args.output_json
    output_markdown = args.output_markdown if args.output_markdown.is_absolute() else root / args.output_markdown
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_bytes(json_bytes(report))
    write_markdown(output_markdown, report)
    print(f"Offline self-hosted rehearsal status: {report['status']}")
    return 0 if report["status"] == STATUS_PASS else 1


if __name__ == "__main__":
    raise SystemExit(main())
