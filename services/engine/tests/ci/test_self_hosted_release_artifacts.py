from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tarfile
import warnings
import zipfile

import pytest


ROOT = Path(__file__).resolve().parents[4]
SCRIPT_DIR = ROOT / "scripts" / "ci"


def _load_script(name: str):
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
    module_path = SCRIPT_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _scratch(name: str) -> Path:
    path = ROOT / ".tmp" / "ci-test-scratch" / name
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path


def _build_and_publish(name: str):
    builder = _load_script("build_self_hosted_package")
    publisher = _load_script("publish_self_hosted_release_artifacts")
    root = _scratch(name)
    package_root = root / "packages"
    builder.build_package(
        root=ROOT,
        output_root=package_root,
        package_label="decisionatlas-self-hosted-test",
        version_label="0.4.0-test",
        commit="abc123",
        generated_at="2026-07-16T00:00:00+00:00",
    )
    package_dir = package_root / "decisionatlas-self-hosted-test"
    report = publisher.publish_release_artifacts(
        package_dir=package_dir,
        output_root=root / "releases",
        source_date_epoch=0,
        generated_at="2026-07-16T00:00:00+00:00",
    )
    return root, package_dir, root / "releases" / "0.4.0-test", report


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _refresh_integrity(release_dir: Path, filename: str) -> None:
    manifest_path = release_dir / "release-artifacts.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    target = release_dir / filename
    for artifact in manifest["artifacts"]:
        if artifact["filename"] == filename:
            artifact["size"] = target.stat().st_size
            artifact["sha256"] = _sha256(target)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    checksums = {
        path.name: _sha256(path)
        for path in release_dir.iterdir()
        if path.is_file() and path.name != "SHA256SUMS" and not path.name.endswith("publication.json")
    }
    (release_dir / "SHA256SUMS").write_text(
        "".join(f"{checksums[name]}  {name}\n" for name in sorted(checksums)),
        encoding="utf-8",
    )


def test_release_artifact_publication_is_deterministic_and_verifiable() -> None:
    publisher = _load_script("publish_self_hosted_release_artifacts")
    verifier = _load_script("verify_self_hosted_release_artifacts")
    root, package_dir, first_dir, first_report = _build_and_publish("release-artifacts-deterministic")
    second_report = publisher.publish_release_artifacts(
        package_dir=package_dir,
        output_root=root / "second-releases",
        source_date_epoch=0,
        generated_at="2026-07-17T00:00:00+00:00",
    )
    second_dir = root / "second-releases" / "0.4.0-test"

    expected_names = {
        "decisionatlas-self-hosted-0.4.0-test.zip",
        "decisionatlas-self-hosted-0.4.0-test.tar.gz",
        "decisionatlas-self-hosted-0.4.0-test.cdx.json",
        "release-artifacts.json",
        "SHA256SUMS",
    }
    assert {path.name for path in first_dir.iterdir()} == expected_names
    assert {path.name: _sha256(path) for path in first_dir.iterdir()} == {
        path.name: _sha256(path) for path in second_dir.iterdir()
    }
    assert first_report["package_content_sha256"] == second_report["package_content_sha256"]

    verification = verifier.verify_release_artifacts(
        first_dir,
        generated_at="2026-07-16T00:00:00+00:00",
        scratch_root=root,
        extract_verified_to=root / "retained",
    )
    assert verification["status"] == "pass"
    assert verification["blockers"] == []
    assert verification["host_proof_level"] == "independent_runner_release_artifact"
    assert verification["is_customer_controlled"] is False
    assert verification["release_directory"] == "<operator-selected-release-dir>"
    assert str(root) not in json.dumps(verification)
    assert {item["archive_kind"] for item in verification["package_verification"]} == {"zip", "tar_gz"}
    assert all(item["status"] == "pass" for item in verification["package_verification"])
    assert verification["sbom"]["npm"] > 0
    assert verification["sbom"]["pypi"] > 0
    assert (root / "retained" / "decisionatlas-self-hosted-0.4.0-test" / "README.md").exists()
    assert any(item["id"] == "retained_extraction" and item["status"] == "pass" for item in verification["checks"])


def test_sbom_parsers_cover_scoped_peer_and_python_dependencies(tmp_path: Path) -> None:
    publisher = _load_script("publish_self_hosted_release_artifacts")
    pnpm_lock = tmp_path / "pnpm-lock.yaml"
    pnpm_lock.write_text(
        """lockfileVersion: '9.0'\npackages:\n  '@scope/pkg@1.2.3(peer@4.5.6)':\n    resolution: {}\n  plain@2.0.0:\n    resolution: {}\nsnapshots:\n  plain@2.0.0: {}\n""",
        encoding="utf-8",
    )
    uv_lock = tmp_path / "uv.lock"
    uv_lock.write_text(
        """version = 1\nrevision = 3\n[[package]]\nname = "FastAPI"\nversion = "0.116.1"\n""",
        encoding="utf-8",
    )

    npm = publisher._pnpm_components(pnpm_lock)
    python = publisher._python_components(uv_lock)

    assert {item["purl"] for item in npm} == {
        "pkg:npm/%40scope/pkg@1.2.3",
        "pkg:npm/plain@2.0.0",
    }
    assert [item["purl"] for item in python] == ["pkg:pypi/fastapi@0.116.1"]


def test_publisher_rejects_unsafe_version_and_unsanitized_package_path() -> None:
    publisher = _load_script("publish_self_hosted_release_artifacts")
    root, package_dir, _, _ = _build_and_publish("release-artifacts-unsafe-version")
    manifest_path = package_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["version_label"] = "../escape"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="Version label"):
        publisher.publish_release_artifacts(package_dir=package_dir, output_root=root / "unsafe")

    manifest["version_label"] = "safe-version"
    manifest["package_path"] = "C:/private/build/path"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="sanitized package_path"):
        publisher.publish_release_artifacts(package_dir=package_dir, output_root=root / "unsafe")

    manifest["package_path"] = "."
    manifest["commit"] = "../unsafe-commit"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="commit"):
        publisher.publish_release_artifacts(package_dir=package_dir, output_root=root / "unsafe")


def test_verifier_blocks_tampered_archive_before_extraction() -> None:
    verifier = _load_script("verify_self_hosted_release_artifacts")
    _, _, release_dir, _ = _build_and_publish("release-artifacts-tampered")
    zip_path = release_dir / "decisionatlas-self-hosted-0.4.0-test.zip"
    zip_path.write_bytes(zip_path.read_bytes() + b"tampered")

    report = verifier.verify_release_artifacts(release_dir)

    assert report["status"] == "blocking"
    assert any(item["id"] == "artifact:zip" for item in report["blockers"])
    assert report["package_verification"] == []


def test_verifier_blocks_traversal_even_with_refreshed_hashes() -> None:
    verifier = _load_script("verify_self_hosted_release_artifacts")
    _, _, release_dir, _ = _build_and_publish("release-artifacts-traversal")
    zip_path = release_dir / "decisionatlas-self-hosted-0.4.0-test.zip"
    with zipfile.ZipFile(zip_path, "a") as archive:
        archive.writestr("decisionatlas-self-hosted-0.4.0-test/../escape.txt", "escape")
    _refresh_integrity(release_dir, zip_path.name)

    report = verifier.verify_release_artifacts(release_dir)

    assert report["status"] == "blocking"
    assert any(item["id"] == "zip_safety" for item in report["blockers"])


def test_verifier_blocks_safe_member_mismatch_between_archive_formats() -> None:
    verifier = _load_script("verify_self_hosted_release_artifacts")
    _, _, release_dir, _ = _build_and_publish("release-artifacts-member-mismatch")
    zip_path = release_dir / "decisionatlas-self-hosted-0.4.0-test.zip"
    with zipfile.ZipFile(zip_path, "a") as archive:
        archive.writestr("decisionatlas-self-hosted-0.4.0-test/extra-safe.txt", "extra")
    _refresh_integrity(release_dir, zip_path.name)

    report = verifier.verify_release_artifacts(release_dir)

    assert report["status"] == "blocking"
    assert any(item["id"] == "member_parity" for item in report["blockers"])


def test_verifier_blocks_duplicate_zip_member() -> None:
    verifier = _load_script("verify_self_hosted_release_artifacts")
    _, _, release_dir, _ = _build_and_publish("release-artifacts-duplicate")
    zip_path = release_dir / "decisionatlas-self-hosted-0.4.0-test.zip"
    member = "decisionatlas-self-hosted-0.4.0-test/README.md"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with zipfile.ZipFile(zip_path, "a") as archive:
            archive.writestr(member, "duplicate")
    _refresh_integrity(release_dir, zip_path.name)

    report = verifier.verify_release_artifacts(release_dir)

    assert report["status"] == "blocking"
    zip_blocker = next(item for item in report["blockers"] if item["id"] == "zip_safety")
    assert any(item["reason"] == "duplicate_member" for item in zip_blocker["details"]["violations"])


def test_verifier_blocks_malformed_sbom_with_matching_checksums() -> None:
    verifier = _load_script("verify_self_hosted_release_artifacts")
    _, _, release_dir, _ = _build_and_publish("release-artifacts-sbom")
    sbom_path = release_dir / "decisionatlas-self-hosted-0.4.0-test.cdx.json"
    sbom = json.loads(sbom_path.read_text(encoding="utf-8"))
    sbom["components"] = []
    sbom_path.write_text(json.dumps(sbom, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _refresh_integrity(release_dir, sbom_path.name)

    report = verifier.verify_release_artifacts(release_dir)

    assert report["status"] == "blocking"
    assert any(item["id"] == "sbom_structure" for item in report["blockers"])


@pytest.mark.parametrize(
    ("member", "reason"),
    [
        ("/absolute.txt", "absolute_or_backslash_path"),
        ("root/../escape.txt", "unsafe_path_segment"),
        ("root\\escape.txt", "absolute_or_backslash_path"),
        ("root/.env", "secret_like_path"),
        ("root/node_modules/pkg.js", "forbidden_package_path"),
        ("other/README.md", "unexpected_root"),
    ],
)
def test_archive_member_safety_rejects_unsafe_and_forbidden_paths(member: str, reason: str) -> None:
    verifier = _load_script("verify_self_hosted_release_artifacts")
    safe, actual_reason = verifier._safe_member(member, "root")
    assert safe is False
    assert actual_reason == reason
