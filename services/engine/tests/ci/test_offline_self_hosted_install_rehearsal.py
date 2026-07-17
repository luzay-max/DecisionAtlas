from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[4]
SCRIPTS = ROOT / "scripts" / "ci"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def _load_script(name: str):
    module_path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _inputs(tmp_path: Path) -> tuple[Path, Path]:
    package = tmp_path / "package"
    bundle = tmp_path / "bundle"
    package.mkdir()
    (bundle / "payload/containers").mkdir(parents=True)
    (bundle / "payload/containers/images.tar").write_bytes(b"fixture")
    (bundle / "offline-dependency-bundle.json").write_text(
        json.dumps(
            {
                "package": {"version_label": "test", "commit": "abc123"},
                "container_images": [
                    {"reference": "pgvector/pgvector:pg17", "image_id": f"sha256:{'a' * 64}"},
                    {"reference": "redis:7.4-alpine", "image_id": f"sha256:{'b' * 64}"},
                ],
            }
        ),
        encoding="utf-8",
    )
    return package, bundle


def test_rehearsal_uses_offline_controls_and_keeps_live_lane_separate(tmp_path: Path, monkeypatch) -> None:
    rehearsal = _load_script("rehearse_offline_self_hosted_install")
    package, bundle = _inputs(tmp_path)
    calls: list[tuple[list[str], dict[str, str]]] = []

    monkeypatch.setattr(
        rehearsal,
        "verify_bundle",
        lambda **kwargs: {"status": "pass", "blockers": []},
    )

    def fake_run(command, *, cwd, env, timeout_seconds):
        calls.append((command, env))
        stdout = "ok"
        if command[:3] == ["docker", "image", "inspect"]:
            digest = "a" * 64 if "pgvector" in command[3] else "b" * 64
            stdout = f"sha256:{digest}"
        return {
            "status": "pass",
            "returncode": 0,
            "duration_seconds": 0.01,
            "stdout_tail": stdout,
            "stderr_tail": "",
        }

    args = rehearsal.parse_args(
        [
            "--package",
            str(package),
            "--bundle",
            str(bundle),
            "--scratch-root",
            str(tmp_path / "scratch"),
            "--label",
            "offline-test",
            "--repo",
            "fresh/example",
            "--run-live-repo",
        ]
    )
    report = rehearsal.rehearse_offline_install(args, ROOT, command_runner=fake_run)

    assert report["status"] == "pass"
    assert report["host_proof_level"] == "process_enforced_offline_install"
    assert report["is_customer_controlled"] is False
    assert report["offline_controls"]["kernel_network_namespace"] is False
    assert report["package_path"] == "<isolated-self-hosted-package>"
    statuses = {stage["id"]: stage["status"] for stage in report["stages"]}
    assert statuses["offline_browser_shell"] == "pass"
    assert statuses["live_repository_browser"] == "pass"

    offline_calls = [
        item
        for item in calls
        if not any("imported-workspace-core-loop.spec.ts" in argument for argument in item[0])
    ]
    assert all(item[1]["HTTPS_PROXY"] == "http://127.0.0.1:9" for item in offline_calls)
    pnpm_call = next(item for item in calls if "install" in item[0] and "--store-dir" in item[0])
    assert "--offline" in pnpm_call[0]
    uv_call = next(item for item in calls if "sync" in item[0])
    assert "--offline" in uv_call[0]
    live_call = next(
        item
        for item in calls
        if any("imported-workspace-core-loop.spec.ts" in argument for argument in item[0])
    )
    assert "HTTPS_PROXY" not in live_call[1]
    assert live_call[1]["PLAYWRIGHT_REAL_PUBLIC_REPO"] == "fresh/example"


def test_live_success_cannot_hide_offline_failure(tmp_path: Path, monkeypatch) -> None:
    rehearsal = _load_script("rehearse_offline_self_hosted_install")
    package, bundle = _inputs(tmp_path)
    monkeypatch.setattr(
        rehearsal,
        "verify_bundle",
        lambda **kwargs: {"status": "pass", "blockers": []},
    )

    def fake_run(command, *, cwd, env, timeout_seconds):
        fails = command[:3] == ["docker", "image", "load"]
        return {
            "status": "blocking" if fails else "pass",
            "returncode": 1 if fails else 0,
            "duration_seconds": 0.01,
            "stdout_tail": "",
            "stderr_tail": "missing image" if fails else "",
        }

    args = rehearsal.parse_args(
        [
            "--package",
            str(package),
            "--bundle",
            str(bundle),
            "--scratch-root",
            str(tmp_path / "scratch-failure"),
            "--run-live-repo",
        ]
    )
    report = rehearsal.rehearse_offline_install(args, ROOT, command_runner=fake_run)

    assert report["status"] == "blocking"
    statuses = {stage["id"]: stage["status"] for stage in report["stages"]}
    assert statuses["container_images"] == "blocking"
    assert statuses["offline_browser_shell"] == "blocking"
    assert statuses["live_repository_browser"] == "blocking"


def test_rehearsal_blocks_loaded_container_identity_mismatch(tmp_path: Path, monkeypatch) -> None:
    rehearsal = _load_script("rehearse_offline_self_hosted_install")
    package, bundle = _inputs(tmp_path)
    monkeypatch.setattr(
        rehearsal,
        "verify_bundle",
        lambda **kwargs: {"status": "pass", "blockers": []},
    )

    def fake_run(command, *, cwd, env, timeout_seconds):
        stdout = "ok"
        if command[:3] == ["docker", "image", "inspect"]:
            stdout = f"sha256:{'f' * 64}"
        return {
            "status": "pass",
            "returncode": 0,
            "duration_seconds": 0.01,
            "stdout_tail": stdout,
            "stderr_tail": "",
        }

    args = rehearsal.parse_args(
        [
            "--package",
            str(package),
            "--bundle",
            str(bundle),
            "--scratch-root",
            str(tmp_path / "scratch-mismatch"),
        ]
    )
    report = rehearsal.rehearse_offline_install(args, ROOT, command_runner=fake_run)

    assert report["status"] == "blocking"
    container_stage = next(stage for stage in report["stages"] if stage["id"] == "container_images")
    assert container_stage["status"] == "blocking"
    inspect_result = next(item for item in report["commands"] if item["id"].startswith("inspect_container:"))
    assert inspect_result["error"] == "loaded_container_image_identity_mismatch"
