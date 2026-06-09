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


def _write_json(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_clean_rehearsal_generates_json_and_markdown(tmp_path: Path) -> None:
    builder = _load_script("build_self_hosted_package")
    rehearsal = _load_script("rehearse_clean_self_hosted_install")
    root = Path(__file__).resolve().parents[4]
    builder.build_package(
        root=root,
        output_root=tmp_path,
        package_label="decisionatlas-self-hosted-test",
        version_label="test-version",
        commit="abc123",
        generated_at="2026-06-09T00:00:00+00:00",
    )
    package_dir = tmp_path / "decisionatlas-self-hosted-test"
    release = _write_json(tmp_path / "release.json", {"overall_status": "passed", "generated_at": "2026-06-09T00:00:00+00:00"})
    hosted = _write_json(tmp_path / "hosted.json", {"overall_status": "operator_guided", "lanes": []})
    package_verification = _write_json(tmp_path / "package.json", {"status": "pass", "package_label": "decisionatlas-self-hosted-test"})

    args = rehearsal.parse_args(
        [
            "--package",
            str(package_dir),
            "--label",
            "clean-test",
            "--version-label",
            "test-version",
            "--commit",
            "abc123",
            "--generated-at",
            "2026-06-09T01:00:00+00:00",
            "--release-evidence-json",
            str(release),
            "--hosted-readiness-json",
            str(hosted),
            "--package-verification-json",
            str(package_verification),
        ]
    )
    bundle = rehearsal.build_rehearsal(args, root)
    markdown = rehearsal.render_markdown(bundle)

    assert bundle["status"] == "warning"
    assert bundle["clean_package_path"].endswith("package-copy")
    assert any(check["id"] == "clean_package_copy" and check["status"] == "pass" for check in bundle["checks"])
    assert any(check["id"] == "copied_package_verification" and check["status"] == "pass" for check in bundle["checks"])
    assert bundle["source_evidence"][0]["status"] == "pass"
    assert bundle["source_evidence"][1]["status"] == "operator_guided"
    assert "Clean Self-Hosted Install Rehearsal" in markdown
    assert "operator_guided" in markdown


def test_clean_rehearsal_blocks_missing_package(tmp_path: Path) -> None:
    rehearsal = _load_script("rehearse_clean_self_hosted_install")
    root = Path(__file__).resolve().parents[4]

    args = rehearsal.parse_args(
        [
            "--package",
            str(tmp_path / "missing-package"),
            "--label",
            "missing-package-test",
            "--generated-at",
            "2026-06-09T01:00:00+00:00",
        ]
    )
    bundle = rehearsal.build_rehearsal(args, root)

    assert bundle["status"] == "blocking"
    assert any(blocker["id"] == "package_input" for blocker in bundle["blockers"])


def test_clean_rehearsal_blocks_missing_required_asset(tmp_path: Path) -> None:
    builder = _load_script("build_self_hosted_package")
    rehearsal = _load_script("rehearse_clean_self_hosted_install")
    root = Path(__file__).resolve().parents[4]
    builder.build_package(
        root=root,
        output_root=tmp_path,
        package_label="decisionatlas-self-hosted-test",
        version_label="test-version",
        commit="abc123",
        generated_at="2026-06-09T00:00:00+00:00",
    )
    package_dir = tmp_path / "decisionatlas-self-hosted-test"
    (package_dir / "docs" / "project" / "self-hosted-package-guide.md").unlink()

    args = rehearsal.parse_args(["--package", str(package_dir), "--label", "asset-test"])
    bundle = rehearsal.build_rehearsal(args, root)

    assert bundle["status"] == "blocking"
    assert any(check["id"] == "asset:docs/project/self-hosted-package-guide.md" for check in bundle["blockers"])


def test_clean_rehearsal_preserves_optional_evidence_statuses(tmp_path: Path) -> None:
    builder = _load_script("build_self_hosted_package")
    rehearsal = _load_script("rehearse_clean_self_hosted_install")
    root = Path(__file__).resolve().parents[4]
    builder.build_package(
        root=root,
        output_root=tmp_path,
        package_label="decisionatlas-self-hosted-test",
        version_label="test-version",
        commit="abc123",
        generated_at="2026-06-09T00:00:00+00:00",
    )
    public_import = _write_json(
        tmp_path / "public-import.json",
        {"setup": {"outcome": "local_stack_failure", "benchmark_ready": False}},
    )

    args = rehearsal.parse_args(
        [
            "--package",
            str(tmp_path / "decisionatlas-self-hosted-test"),
            "--public-github-import-json",
            str(public_import),
        ]
    )
    bundle = rehearsal.build_rehearsal(args, root)
    statuses = {item["id"]: item["status"] for item in bundle["source_evidence"]}

    assert statuses["public_github_import"] == "local_stack_failure"
    assert statuses["benchmark_comparison"] == "not_provided"
    assert bundle["status"] == "warning"
