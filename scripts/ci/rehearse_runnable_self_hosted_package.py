from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from verify_self_hosted_package import verify_package  # noqa: E402


SCHEMA_VERSION = 1
STATUS_PASS = "pass"
STATUS_BLOCKING = "blocking"
STATUS_OPERATOR_GUIDED = "operator_guided"
SECRET_PATTERNS = [
    re.compile(r"github_pat_[A-Za-z0-9_]+"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]+"),
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"(?i)(api[_-]?key|token|password)\s*[=:]\s*\S+"),
]


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip().lower()).strip("-")
    return slug or "runnable-self-hosted-package"


def _resolve_path(path: Path, root: Path) -> Path:
    return path if path.is_absolute() else root / path


def _sanitize_output(value: str, limit: int = 4000) -> str:
    text = value[-limit:]
    for pattern in SECRET_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return text


def _reset_owned_directory(path: Path, owned_root: Path) -> None:
    resolved_path = path.resolve()
    resolved_root = owned_root.resolve()
    if resolved_path == resolved_root or resolved_root not in resolved_path.parents:
        raise ValueError(f"Refusing to reset path outside rehearsal root: {path}")
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def _run_command(
    command: list[str],
    *,
    cwd: Path,
    timeout_seconds: int,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    started_at = datetime.now(UTC)
    resolved_executable = shutil.which(command[0])
    execution_command = [resolved_executable, *command[1:]] if resolved_executable else command
    try:
        completed = subprocess.run(
            execution_command,
            cwd=cwd,
            env=env,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
        )
        status = STATUS_PASS if completed.returncode == 0 else STATUS_BLOCKING
        return {
            "status": status,
            "command": command,
            "cwd": cwd.as_posix(),
            "returncode": completed.returncode,
            "duration_seconds": round((datetime.now(UTC) - started_at).total_seconds(), 3),
            "stdout_tail": _sanitize_output(completed.stdout or ""),
            "stderr_tail": _sanitize_output(completed.stderr or ""),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "status": STATUS_BLOCKING,
            "command": command,
            "cwd": cwd.as_posix(),
            "returncode": None,
            "duration_seconds": round((datetime.now(UTC) - started_at).total_seconds(), 3),
            "error": f"timeout_after_{timeout_seconds}_seconds",
            "stdout_tail": _sanitize_output(str(exc.stdout or "")),
            "stderr_tail": _sanitize_output(str(exc.stderr or "")),
        }
    except OSError as exc:
        return {
            "status": STATUS_BLOCKING,
            "command": command,
            "cwd": cwd.as_posix(),
            "returncode": None,
            "duration_seconds": round((datetime.now(UTC) - started_at).total_seconds(), 3),
            "error": _sanitize_output(str(exc)),
        }


def _stage(stage_id: str, label: str, status: str, **details: Any) -> dict[str, Any]:
    return {"id": stage_id, "label": label, "status": status, **details}


def _uv_command(*arguments: str) -> list[str]:
    return ["uv", *arguments] if shutil.which("uv") else [sys.executable, "-m", "uv", *arguments]


def _with_local_no_proxy(env: dict[str, str]) -> dict[str, str]:
    values = [
        item.strip()
        for key in ("NO_PROXY", "no_proxy")
        for item in env.get(key, "").split(",")
        if item.strip()
    ]
    for host in ("127.0.0.1", "localhost"):
        if host not in values:
            values.append(host)
    merged = ",".join(values)
    env["NO_PROXY"] = merged
    env["no_proxy"] = merged
    return env


def rehearse_package(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    source_package = _resolve_path(args.package, root).resolve()
    scratch_root = (
        _resolve_path(args.scratch_root, root).resolve()
        if args.scratch_root
        else Path(tempfile.gettempdir()).resolve() / "decisionatlas-runnable-package-rehearsal"
    )
    label = _slugify(args.label)
    rehearsal_root = scratch_root / label
    package_copy = rehearsal_root / "package-copy"
    scratch_root.mkdir(parents=True, exist_ok=True)
    _reset_owned_directory(rehearsal_root, scratch_root)

    stages: list[dict[str, Any]] = []
    if not source_package.exists() or not source_package.is_dir():
        stages.append(
            _stage(
                "copy_package",
                "Copy package into isolated runtime root",
                STATUS_BLOCKING,
                error="package_missing_or_not_directory",
            )
        )
    else:
        shutil.copytree(source_package, package_copy)
        stages.append(
            _stage(
                "copy_package",
                "Copy package into isolated runtime root",
                STATUS_PASS,
                source_package=source_package.as_posix(),
                package_copy=package_copy.as_posix(),
            )
        )

    verification = verify_package(package_copy, generated_at=args.generated_at) if package_copy.exists() else {
        "status": STATUS_BLOCKING,
        "runnable_status": STATUS_BLOCKING,
        "blockers": [{"id": "package_copy_missing"}],
    }
    stages.append(
        _stage(
            "verify_package",
            "Verify runnable package inputs",
            verification.get("status", STATUS_BLOCKING),
            runnable_status=verification.get("runnable_status"),
            blocker_ids=[str(item.get("id")) for item in verification.get("blockers", [])[:20]],
        )
    )

    commands: list[dict[str, Any]] = []
    can_run = verification.get("status") == STATUS_PASS
    install_status = STATUS_OPERATOR_GUIDED
    if args.install_dependencies and can_run:
        for command in (
            ["pnpm", "install", "--frozen-lockfile"],
            _uv_command("sync", "--project", "services/engine", "--frozen"),
        ):
            result = _run_command(command, cwd=package_copy, timeout_seconds=args.install_timeout_seconds)
            commands.append(result)
            if result["status"] != STATUS_PASS:
                break
        install_status = STATUS_PASS if commands and all(item["status"] == STATUS_PASS for item in commands) else STATUS_BLOCKING
    elif args.install_dependencies:
        install_status = STATUS_BLOCKING
    stages.append(
        _stage(
            "install_dependencies",
            "Install exact Node and Python dependencies",
            install_status,
            requested=bool(args.install_dependencies),
        )
    )

    browser_install_status = STATUS_OPERATOR_GUIDED
    if args.install_browser and can_run and install_status == STATUS_PASS:
        result = _run_command(
            ["pnpm", "--filter", "@decisionatlas/web", "exec", "playwright", "install", "chromium"],
            cwd=package_copy,
            timeout_seconds=args.install_timeout_seconds,
        )
        commands.append(result)
        browser_install_status = result["status"]
    elif args.install_browser:
        browser_install_status = STATUS_BLOCKING
    stages.append(
        _stage(
            "install_browser",
            "Install Playwright Chromium",
            browser_install_status,
            requested=bool(args.install_browser),
        )
    )

    smoke_status = STATUS_OPERATOR_GUIDED
    smoke_result: dict[str, Any] | None = None
    if args.run_smoke and can_run and install_status == STATUS_PASS:
        smoke_env = _with_local_no_proxy(os.environ.copy())
        smoke_env["PLAYWRIGHT_REAL_PUBLIC_REPO"] = args.repo
        smoke_result = _run_command(
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
            cwd=package_copy,
            env=smoke_env,
            timeout_seconds=args.smoke_timeout_seconds,
        )
        commands.append(smoke_result)
        smoke_status = smoke_result["status"]
    elif args.run_smoke:
        smoke_status = STATUS_BLOCKING
    stages.append(
        _stage(
            "service_startup",
            "Start engine, API, and web with health gates",
            smoke_status,
            requested=bool(args.run_smoke),
            proof_mechanism="playwright_web_server_health_gates",
            urls={
                "engine": "http://127.0.0.1:8000/health",
                "api": "http://127.0.0.1:3001/health",
                "web": "http://127.0.0.1:3000",
            },
            duration_seconds=smoke_result.get("duration_seconds") if smoke_result else None,
        )
    )
    stages.append(
        _stage(
            "browser_smoke",
            "Run imported-workspace browser smoke",
            smoke_status,
            requested=bool(args.run_smoke),
            repository=args.repo,
        )
    )

    requested_stages = [
        stage
        for stage in stages
        if stage["id"] in {"copy_package", "verify_package"}
        or stage.get("requested")
    ]
    status = STATUS_BLOCKING if any(stage["status"] == STATUS_BLOCKING for stage in requested_stages) else (
        STATUS_PASS
        if args.install_dependencies and args.install_browser and args.run_smoke
        and all(stage["status"] == STATUS_PASS for stage in requested_stages)
        else STATUS_OPERATOR_GUIDED
    )
    host_proof_level = (
        "customer_controlled_package_smoke"
        if status == STATUS_PASS and args.is_customer_controlled
        else "independent_host_package_smoke"
        if status == STATUS_PASS and args.host_class not in {"local", "local_workstation"}
        else "local_isolated_package_smoke"
        if status == STATUS_PASS
        else "package_runtime_not_clean"
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": args.generated_at or datetime.now(UTC).isoformat(),
        "evidence_type": "runnable-self-hosted-package-rehearsal",
        "label": args.label,
        "version_label": args.version_label,
        "commit": args.commit,
        "status": status,
        "host_proof_level": host_proof_level,
        "host_profile": {
            "host_class": args.host_class,
            "os_family": args.os_family,
            "is_customer_controlled": bool(args.is_customer_controlled),
        },
        "source_package": source_package.as_posix(),
        "package_copy": package_copy.as_posix(),
        "repository": args.repo,
        "stages": stages,
        "commands": commands,
        "summary": {
            "pass": sum(1 for stage in stages if stage["status"] == STATUS_PASS),
            "blocking": sum(1 for stage in stages if stage["status"] == STATUS_BLOCKING),
            "operator_guided": sum(1 for stage in stages if stage["status"] == STATUS_OPERATOR_GUIDED),
        },
        "limitations": [
            "Dependency installation downloads packages unless an operator supplies an approved cache or mirror.",
            "GitHub-hosted and local isolated rehearsals prove package independence but are not customer-controlled-host proof.",
            "Evidence stores only bounded command tails and does not store tokens, raw private source, databases, or raw model output.",
        ],
        "recommended_next_actions": (
            []
            if status == STATUS_PASS and args.is_customer_controlled
            else ["Repeat the same runnable package rehearsal on a sanitized customer-controlled host before clean customer claims."]
        ),
    }


def _markdown_cell(value: Any) -> str:
    if value is None:
        return "-"
    text = json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else str(value)
    return text.replace("|", "\\|").replace("\n", "<br>") or "-"


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Runnable Self-Hosted Package Rehearsal",
        "",
        f"- Generated at: `{report.get('generated_at')}`",
        f"- Status: `{report.get('status')}`",
        f"- Host proof: `{report.get('host_proof_level')}`",
        f"- Host class: `{(report.get('host_profile') or {}).get('host_class')}`",
        f"- Customer controlled: `{(report.get('host_profile') or {}).get('is_customer_controlled')}`",
        f"- Repository: `{report.get('repository')}`",
        f"- Package copy: `{report.get('package_copy')}`",
        "",
        "## Stages",
        "",
        "| Stage | Status | Details |",
        "| --- | --- | --- |",
    ]
    for stage in report.get("stages", []):
        details = {key: value for key, value in stage.items() if key not in {"id", "label", "status"}}
        lines.append(
            "| "
            + " | ".join(
                _markdown_cell(value)
                for value in (stage.get("label"), stage.get("status"), details)
            )
            + " |"
        )
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.get("limitations", []))
    lines.extend(["", "## Next Actions", ""])
    actions = report.get("recommended_next_actions", [])
    lines.extend(f"- {item}" for item in actions or ["No additional action recorded."])
    lines.append("")
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Exercise a runnable DecisionAtlas self-hosted package from an isolated copy.")
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--label", default="runnable-self-hosted-package")
    parser.add_argument("--version-label", default="self-hosted-preview")
    parser.add_argument("--commit", default="unknown")
    parser.add_argument("--generated-at")
    parser.add_argument("--scratch-root", type=Path)
    parser.add_argument("--host-class", default="local_workstation")
    parser.add_argument("--os-family", default="windows")
    parser.add_argument("--is-customer-controlled", action="store_true")
    parser.add_argument("--repo", default="pallets/markupsafe")
    parser.add_argument("--install-dependencies", action="store_true")
    parser.add_argument("--install-browser", action="store_true")
    parser.add_argument("--run-smoke", action="store_true")
    parser.add_argument("--install-timeout-seconds", type=int, default=900)
    parser.add_argument("--smoke-timeout-seconds", type=int, default=900)
    parser.add_argument("--output-json", type=Path, default=Path(".tmp/runnable-self-hosted-package-rehearsal.json"))
    parser.add_argument("--output-markdown", type=Path, default=Path(".tmp/runnable-self-hosted-package-rehearsal.md"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    report = rehearse_package(args, root)
    output_json = _resolve_path(args.output_json, root)
    output_markdown = _resolve_path(args.output_markdown, root)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    output_markdown.write_text(render_markdown(report), encoding="utf-8")
    print(f"Runnable package rehearsal JSON written to {output_json}")
    print(f"Runnable package rehearsal Markdown written to {output_markdown}")
    print(f"Status: {report['status']}")
    return 0 if report["status"] in {STATUS_PASS, STATUS_OPERATOR_GUIDED} else 1


if __name__ == "__main__":
    raise SystemExit(main())
