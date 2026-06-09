from __future__ import annotations

import importlib.util
import json
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


def test_self_hosted_package_builder_writes_manifest_and_allowlisted_assets(tmp_path: Path) -> None:
    builder = _load_script("build_self_hosted_package")
    root = Path(__file__).resolve().parents[4]

    manifest = builder.build_package(
        root=root,
        output_root=tmp_path,
        package_label="decisionatlas-self-hosted-test",
        version_label="test-version",
        commit="abc123",
        generated_at="2026-06-08T00:00:00+00:00",
    )

    package_dir = tmp_path / "decisionatlas-self-hosted-test"
    manifest_path = package_dir / "manifest.json"
    readme_path = package_dir / "README.md"

    assert manifest["package_label"] == "decisionatlas-self-hosted-test"
    assert manifest["commit"] == "abc123"
    assert manifest_path.exists()
    assert readme_path.exists()
    assert "DecisionAtlas Self-Hosted Package" in readme_path.read_text(encoding="utf-8")
    assert (package_dir / "templates" / "self-hosted.env.example").exists()
    assert (package_dir / "templates" / "self-hosted-entitlement.example.json").exists()
    assert (package_dir / "docs" / "project" / "self-hosted-package-guide.md").exists()
    assert (package_dir / "docs" / "project" / "self-hosted-license-and-support-boundary.md").exists()
    assert (package_dir / "scripts" / "dev" / "start-real-stack.ps1").exists()

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert data["version_label"] == "test-version"
    assert "runtime_license_enforcement" in data["unsupported_capabilities"]
    assert "offline_entitlement_template" in data["readiness_evidence_expectations"]
    assert "python scripts\\ci\\verify_self_hosted_package.py --package <package-path>" in data["validation_commands"]


def test_self_hosted_package_verifier_passes_valid_package(tmp_path: Path) -> None:
    builder = _load_script("build_self_hosted_package")
    verifier = _load_script("verify_self_hosted_package")
    root = Path(__file__).resolve().parents[4]
    builder.build_package(
        root=root,
        output_root=tmp_path,
        package_label="decisionatlas-self-hosted-test",
        version_label="test-version",
        commit="abc123",
        generated_at="2026-06-08T00:00:00+00:00",
    )

    package_dir = tmp_path / "decisionatlas-self-hosted-test"
    bundle = verifier.verify_package(package_dir, generated_at="2026-06-08T00:00:00+00:00")
    markdown = verifier.render_markdown(bundle)

    assert bundle["status"] == "pass"
    assert bundle["blockers"] == []
    assert bundle["checked_file_count"] > 10
    assert {lane["id"] for lane in bundle["non_pass_lanes"]} == {
        "runtime_smoke",
        "private_repository_token_validation",
        "live_benchmark",
        "readiness_history",
        "team_handoff_report",
        "license_support_boundary",
    }
    assert "Runtime smoke" in markdown
    assert "operator_guided" in markdown
    assert "not_provided" in markdown


def test_self_hosted_package_verifier_blocks_missing_required_file(tmp_path: Path) -> None:
    builder = _load_script("build_self_hosted_package")
    verifier = _load_script("verify_self_hosted_package")
    root = Path(__file__).resolve().parents[4]
    builder.build_package(
        root=root,
        output_root=tmp_path,
        package_label="decisionatlas-self-hosted-test",
        version_label="test-version",
        commit="abc123",
        generated_at="2026-06-08T00:00:00+00:00",
    )

    package_dir = tmp_path / "decisionatlas-self-hosted-test"
    (package_dir / "scripts" / "dev" / "start-real-stack.ps1").unlink()

    bundle = verifier.verify_package(package_dir, generated_at="2026-06-08T00:00:00+00:00")

    assert bundle["status"] == "blocking"
    assert any(
        blocker["id"] == "file:scripts/dev/start-real-stack.ps1"
        for blocker in bundle["blockers"]
    )


def test_self_hosted_package_verifier_blocks_secret_like_files(tmp_path: Path) -> None:
    builder = _load_script("build_self_hosted_package")
    verifier = _load_script("verify_self_hosted_package")
    root = Path(__file__).resolve().parents[4]
    builder.build_package(
        root=root,
        output_root=tmp_path,
        package_label="decisionatlas-self-hosted-test",
        version_label="test-version",
        commit="abc123",
        generated_at="2026-06-08T00:00:00+00:00",
    )

    package_dir = tmp_path / "decisionatlas-self-hosted-test"
    (package_dir / ".env").write_text("LLM_API_KEY=secret", encoding="utf-8")

    bundle = verifier.verify_package(package_dir, generated_at="2026-06-08T00:00:00+00:00")

    assert bundle["status"] == "blocking"
    assert any(blocker["id"] == "secret_exclusions" for blocker in bundle["blockers"])
