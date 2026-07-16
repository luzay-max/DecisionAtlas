from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_script(name: str):
    root = Path(__file__).resolve().parents[4]
    module_path = root / "scripts" / "ci" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _build_package(tmp_path: Path) -> tuple[Path, Path]:
    builder = _load_script("build_self_hosted_package")
    root = Path(__file__).resolve().parents[4]
    builder.build_package(
        root=root,
        output_root=tmp_path,
        package_label="decisionatlas-runnable-test",
        version_label="test-version",
        commit="abc123",
        generated_at="2026-07-16T00:00:00+00:00",
    )
    return root, tmp_path / "decisionatlas-runnable-test"


def test_runnable_rehearsal_runs_all_commands_from_isolated_package_copy(tmp_path: Path, monkeypatch) -> None:
    rehearsal = _load_script("rehearse_runnable_self_hosted_package")
    root, package_dir = _build_package(tmp_path)
    command_calls: list[tuple[list[str], Path, dict[str, str] | None]] = []

    def fake_run(command, *, cwd, timeout_seconds, env=None):
        command_calls.append((command, cwd, env))
        return {
            "status": "pass",
            "command": command,
            "cwd": cwd.as_posix(),
            "returncode": 0,
            "duration_seconds": 0.01,
            "stdout_tail": "ok",
            "stderr_tail": "",
        }

    monkeypatch.setattr(rehearsal, "_run_command", fake_run)
    args = rehearsal.parse_args(
        [
            "--package",
            str(package_dir),
            "--scratch-root",
            str(tmp_path / "isolated"),
            "--label",
            "isolated-test",
            "--host-class",
            "github_hosted_windows_runner",
            "--repo",
            "pallets/markupsafe",
            "--install-dependencies",
            "--install-browser",
            "--run-smoke",
        ]
    )

    report = rehearsal.rehearse_package(args, root)
    package_copy = Path(report["package_copy"])

    assert report["status"] == "pass"
    assert report["host_proof_level"] == "independent_host_package_smoke"
    assert report["host_profile"]["is_customer_controlled"] is False
    service_stage = next(stage for stage in report["stages"] if stage["id"] == "service_startup")
    assert service_stage["status"] == "pass"
    assert service_stage["urls"]["api"] == "http://127.0.0.1:3001/health"
    assert service_stage["proof_mechanism"] == "playwright_web_server_health_gates"
    assert len(command_calls) == 4
    assert all(cwd == package_copy for _, cwd, _ in command_calls)
    assert command_calls[-1][0][-1] == "--workers=1"
    assert "127.0.0.1" in (command_calls[-1][2] or {})["NO_PROXY"]
    assert "localhost" in (command_calls[-1][2] or {})["no_proxy"]
    assert report["repository"] == "pallets/markupsafe"


def test_runnable_rehearsal_blocks_when_dependency_install_fails(tmp_path: Path, monkeypatch) -> None:
    rehearsal = _load_script("rehearse_runnable_self_hosted_package")
    root, package_dir = _build_package(tmp_path)

    def fail_run(command, *, cwd, timeout_seconds, env=None):
        return {
            "status": "blocking",
            "command": command,
            "cwd": cwd.as_posix(),
            "returncode": 1,
            "duration_seconds": 0.01,
            "stdout_tail": "",
            "stderr_tail": "install failed",
        }

    monkeypatch.setattr(rehearsal, "_run_command", fail_run)
    args = rehearsal.parse_args(
        [
            "--package",
            str(package_dir),
            "--scratch-root",
            str(tmp_path / "isolated-failure"),
            "--install-dependencies",
            "--install-browser",
            "--run-smoke",
        ]
    )

    report = rehearsal.rehearse_package(args, root)
    statuses = {stage["id"]: stage["status"] for stage in report["stages"]}

    assert report["status"] == "blocking"
    assert report["host_proof_level"] == "package_runtime_not_clean"
    assert statuses["install_dependencies"] == "blocking"
    assert statuses["install_browser"] == "blocking"
    assert statuses["service_startup"] == "blocking"
    assert statuses["browser_smoke"] == "blocking"


def test_runnable_rehearsal_redacts_bounded_secret_output() -> None:
    rehearsal = _load_script("rehearse_runnable_self_hosted_package")

    sanitized = rehearsal._sanitize_output("prefix github_pat_exampleSECRET token=abc123")

    assert "github_pat_" not in sanitized
    assert "abc123" not in sanitized
    assert sanitized.count("[REDACTED]") == 2


def test_uv_command_falls_back_to_current_python_when_uv_is_not_on_path(monkeypatch) -> None:
    rehearsal = _load_script("rehearse_runnable_self_hosted_package")
    monkeypatch.setattr(rehearsal.shutil, "which", lambda name: None)

    command = rehearsal._uv_command("sync", "--project", "services/engine")

    assert command[:3] == [sys.executable, "-m", "uv"]


def test_run_command_resolves_windows_command_shims(tmp_path: Path, monkeypatch) -> None:
    rehearsal = _load_script("rehearse_runnable_self_hosted_package")
    captured: dict[str, list[str]] = {}

    class Completed:
        returncode = 0
        stdout = "ok"
        stderr = ""

    monkeypatch.setattr(rehearsal.shutil, "which", lambda name: "C:/tools/pnpm.CMD")

    def fake_subprocess_run(command, **kwargs):
        captured["command"] = command
        return Completed()

    monkeypatch.setattr(rehearsal.subprocess, "run", fake_subprocess_run)

    result = rehearsal._run_command(
        ["pnpm", "--version"],
        cwd=tmp_path,
        timeout_seconds=10,
    )

    assert captured["command"] == ["C:/tools/pnpm.CMD", "--version"]
    assert result["command"] == ["pnpm", "--version"]
    assert result["status"] == "pass"
