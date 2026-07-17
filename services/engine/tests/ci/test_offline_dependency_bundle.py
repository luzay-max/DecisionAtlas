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


class FakeBundleRunner:
    def __init__(self, *, fail_id: str | None = None) -> None:
        self.fail_id = fail_id
        self.calls: list[tuple[list[str], Path, dict[str, str] | None]] = []

    def __call__(self, command, *, cwd, timeout_seconds, env=None):
        command = [str(item) for item in command]
        self.calls.append((command, cwd, env))
        command_text = " ".join(command)
        command_id = ""
        stdout = "ok"
        if command[:2] == ["node", "--version"]:
            command_id, stdout = "node_version", "v22.14.0"
        elif command[:2] == ["pnpm", "--version"]:
            command_id, stdout = "pnpm_version", "10.6.0"
        elif "uv" in command_text and "--version" in command:
            command_id, stdout = "uv_version", "uv 0.10.6"
        elif command[:2] == ["docker", "version"]:
            command_id, stdout = "docker_version", "29.2.1"
        elif command[:2] == ["pnpm", "fetch"]:
            command_id = "pnpm_fetch"
            store = Path(command[command.index("--store-dir") + 1])
            (store / "v10/files/aa").mkdir(parents=True, exist_ok=True)
            (store / "v10/files/aa/pkg-index.json").write_text('{"name":"fixture"}\n', encoding="utf-8")
        elif "sync" in command and "--cache-dir" in command:
            command_id = "uv_sync_cache"
            cache = Path(command[command.index("--cache-dir") + 1])
            (cache / "archive-v0/fixture").mkdir(parents=True, exist_ok=True)
            (cache / "archive-v0/fixture/package.whl").write_bytes(b"wheel-fixture")
        elif "playwright" in command and "install" in command:
            command_id = "playwright_install"
            browser = Path((env or {})["PLAYWRIGHT_BROWSERS_PATH"])
            (browser / "chromium-123/chrome-win").mkdir(parents=True, exist_ok=True)
            (browser / "chromium-123/chrome-win/chrome.exe").write_bytes(b"browser-fixture")
        elif command[:3] == ["docker", "image", "inspect"]:
            command_id = f"inspect_container:{command[3]}"
            digest = "a" * 64 if "pgvector" in command[3] else "b" * 64
            stdout = json.dumps({"Id": f"sha256:{digest}", "RepoDigests": [f"{command[3].split(':')[0]}@sha256:{digest}"]})
        elif command[:2] == ["docker", "pull"]:
            command_id = f"pull_container:{command[2]}"
        elif command[:3] == ["docker", "image", "save"]:
            command_id = "save_container_images"
            output = Path(command[command.index("-o") + 1])
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b"container-image-tar-fixture")

        status = "blocking" if self.fail_id == command_id else "pass"
        return {
            "status": status,
            "returncode": 1 if status == "blocking" else 0,
            "duration_seconds": 0.01,
            "stdout_tail": stdout if status == "pass" else "",
            "stderr_tail": "fixture command failed" if status == "blocking" else "",
        }


def _build_package(tmp_path: Path) -> Path:
    builder = _load_script("build_self_hosted_package")
    builder.build_package(
        root=ROOT,
        output_root=tmp_path / "packages",
        package_label="decisionatlas-offline-test",
        version_label="0.4.0-offline-test",
        commit="abc123",
        generated_at="2026-07-16T00:00:00+00:00",
    )
    return tmp_path / "packages/decisionatlas-offline-test"


def _prepare(tmp_path: Path, *, fail_id: str | None = None):
    preparation = _load_script("prepare_offline_dependency_bundle")
    package_dir = _build_package(tmp_path)
    bundle_dir = tmp_path / "offline-bundle"
    runner = FakeBundleRunner(fail_id=fail_id)
    report = preparation.prepare_bundle(
        package_dir=package_dir,
        output_dir=bundle_dir,
        command_runner=runner,
        generated_at_value="2026-07-16T00:00:00+00:00",
    )
    return package_dir, bundle_dir, report, runner


def _verify(package_dir: Path, bundle_dir: Path):
    verifier = _load_script("verify_offline_dependency_bundle")
    manifest = json.loads((bundle_dir / "offline-dependency-bundle.json").read_text(encoding="utf-8"))
    return verifier.verify_bundle(
        bundle_dir=bundle_dir,
        package_dir=package_dir,
        generated_at_value="2026-07-16T00:00:00+00:00",
        actual_platform_contract=manifest["platform_contract"],
    )


def _refresh_checksums(bundle_dir: Path) -> None:
    contract = _load_script("offline_dependency_bundle")
    paths = [
        path
        for path in bundle_dir.rglob("*")
        if path.is_file() and path.name != contract.CHECKSUM_FILENAME
    ]
    contract.write_checksums(bundle_dir, paths)


def test_preparation_and_verification_cover_all_categories_and_bindings(tmp_path: Path) -> None:
    package_dir, bundle_dir, preparation, runner = _prepare(tmp_path)

    assert preparation["status"] == "pass"
    assert preparation["bundle_created"] is True
    assert preparation["bundle_path"] == "<operator-selected-offline-bundle>"
    assert set(preparation["categories"]) == {
        "pnpm_store",
        "uv_cache",
        "playwright_browsers",
        "container_images",
    }
    assert all(item["file_count"] > 0 for item in preparation["categories"].values())
    assert len(preparation["container_images"]) == 2
    assert preparation["platform_contract"]["uv"] == "0.10.6"
    assert any(call[0][:2] == ["pnpm", "fetch"] for call in runner.calls)

    local_root = str(tmp_path.resolve())
    command_text = json.dumps(preparation["commands"], sort_keys=True)
    assert local_root not in command_text

    verification = _verify(package_dir, bundle_dir)

    assert verification["status"] == "pass"
    assert verification["blockers"] == []
    assert verification["package_path"] == "<operator-selected-self-hosted-package>"
    assert verification["bundle_path"] == "<operator-selected-offline-bundle>"
    assert verification["sbom"]["containers"] == 2
    assert verification["sbom"]["npm"] > 0
    assert verification["sbom"]["pypi"] > 0


def test_preparation_failure_does_not_retain_partial_bundle(tmp_path: Path) -> None:
    _, bundle_dir, report, _ = _prepare(tmp_path, fail_id="uv_sync_cache")

    assert report["status"] == "blocking"
    assert report["bundle_created"] is False
    assert not bundle_dir.exists()
    assert any(item["id"] == "uv_sync_cache" for item in report["blockers"])


def test_verifier_blocks_payload_tampering(tmp_path: Path) -> None:
    package_dir, bundle_dir, _, _ = _prepare(tmp_path)
    target = next((bundle_dir / "payload/pnpm/store").rglob("*.json"))
    target.write_text("tampered", encoding="utf-8")

    report = _verify(package_dir, bundle_dir)

    assert report["status"] == "blocking"
    assert any(item["id"] == "checksum_coverage" for item in report["blockers"])


def test_verifier_blocks_package_binding_mismatch(tmp_path: Path) -> None:
    package_dir, bundle_dir, _, _ = _prepare(tmp_path)
    lockfile = package_dir / "pnpm-lock.yaml"
    lockfile.write_text(lockfile.read_text(encoding="utf-8") + "\n# changed\n", encoding="utf-8")

    report = _verify(package_dir, bundle_dir)

    assert report["status"] == "blocking"
    assert any(item["id"] == "package_bindings" for item in report["blockers"])


def test_verifier_blocks_platform_mismatch(tmp_path: Path) -> None:
    verifier = _load_script("verify_offline_dependency_bundle")
    package_dir, bundle_dir, _, _ = _prepare(tmp_path)
    manifest = json.loads((bundle_dir / "offline-dependency-bundle.json").read_text(encoding="utf-8"))
    actual = dict(manifest["platform_contract"])
    actual["python"] = "0.0"

    report = verifier.verify_bundle(
        bundle_dir=bundle_dir,
        package_dir=package_dir,
        actual_platform_contract=actual,
    )

    assert report["status"] == "blocking"
    blocker = next(item for item in report["blockers"] if item["id"] == "platform_contract")
    assert blocker["details"]["mismatched"] == ["python"]


def test_verifier_blocks_unlisted_forbidden_payload(tmp_path: Path) -> None:
    package_dir, bundle_dir, _, _ = _prepare(tmp_path)
    forbidden = bundle_dir / "payload/pnpm/store/.env"
    forbidden.write_text("TOKEN=secret", encoding="utf-8")

    report = _verify(package_dir, bundle_dir)

    assert report["status"] == "blocking"
    assert any(item["id"] == "bundle_paths" for item in report["blockers"])


def test_path_contract_allows_uv_marker_but_rejects_git_metadata() -> None:
    contract = _load_script("offline_dependency_bundle")

    assert contract.safe_relative_path("payload/uv/cache/sdists-v9/.git").name == ".git"
    for path in (
        "payload/uv/cache/sdists-v9/.git/config",
        "payload/pnpm/store/.git",
        "payload/playwright/browsers/.git/config",
    ):
        try:
            contract.safe_relative_path(path)
        except ValueError:
            pass
        else:
            raise AssertionError(f"Expected Git metadata path to be rejected: {path}")


def test_verifier_blocks_missing_category_payload_even_with_refreshed_checksums(tmp_path: Path) -> None:
    package_dir, bundle_dir, _, _ = _prepare(tmp_path)
    browser = next((bundle_dir / "payload/playwright/browsers").rglob("chrome.exe"))
    browser.unlink()
    _refresh_checksums(bundle_dir)

    report = _verify(package_dir, bundle_dir)

    assert report["status"] == "blocking"
    assert any(item["id"] == "payload_inventory" for item in report["blockers"])


def test_verifier_blocks_malformed_sbom_with_matching_checksum(tmp_path: Path) -> None:
    package_dir, bundle_dir, _, _ = _prepare(tmp_path)
    sbom_path = bundle_dir / "offline-dependency-bundle.cdx.json"
    sbom = json.loads(sbom_path.read_text(encoding="utf-8"))
    sbom["components"][0]["bom-ref"] = sbom["components"][1]["bom-ref"]
    sbom_path.write_text(json.dumps(sbom, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _refresh_checksums(bundle_dir)

    report = _verify(package_dir, bundle_dir)

    assert report["status"] == "blocking"
    assert any(item["id"] == "sbom_structure" for item in report["blockers"])
