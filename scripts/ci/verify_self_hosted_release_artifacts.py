from __future__ import annotations

import argparse
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import stat
import sys
import tarfile
import tempfile
from typing import Any, Callable
import zipfile

from verify_self_hosted_package import FORBIDDEN_PACKAGE_PATHS, verify_package


SCHEMA_VERSION = 1
REQUIRED_KINDS = {"zip", "tar_gz", "cyclonedx_sbom"}


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")


def _blocking(identifier: str, label: str, **details: Any) -> dict[str, Any]:
    return {"id": identifier, "label": label, "status": "blocking", "details": details}


def _pass(identifier: str, label: str, **details: Any) -> dict[str, Any]:
    return {"id": identifier, "label": label, "status": "pass", "details": details}


def _load_json(path: Path, label: str, checks: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not path.is_file():
        checks.append(_blocking(f"file:{path.name}", f"{label} exists", path=path.name))
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        checks.append(_blocking(f"json:{path.name}", f"{label} is valid JSON", error=str(exc)))
        return None
    if not isinstance(value, dict):
        checks.append(_blocking(f"json:{path.name}", f"{label} is a JSON object", reason="not_an_object"))
        return None
    checks.append(_pass(f"json:{path.name}", f"{label} is readable", path=path.name))
    return value


def _parse_checksums(path: Path, checks: list[dict[str, Any]]) -> dict[str, str]:
    if not path.is_file():
        checks.append(_blocking("checksums", "SHA256SUMS exists", path=path.name))
        return {}
    entries: dict[str, str] = {}
    errors: list[str] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line:
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2 or len(parts[0]) != 64 or any(character not in "0123456789abcdef" for character in parts[0]):
            errors.append(f"line_{line_number}")
            continue
        digest, filename = parts
        if filename in entries or Path(filename).name != filename:
            errors.append(f"line_{line_number}")
            continue
        entries[filename] = digest
    checks.append(
        _pass("checksums", "SHA256SUMS is well formed", entry_count=len(entries))
        if not errors
        else _blocking("checksums", "SHA256SUMS is well formed", invalid_lines=errors)
    )
    return entries


def _safe_member(member: str, expected_root: str) -> tuple[bool, str | None]:
    if not member or "\\" in member or member.startswith("/"):
        return False, "absolute_or_backslash_path"
    path = PurePosixPath(member)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        return False, "unsafe_path_segment"
    if len(path.parts) < 2 or path.parts[0] != expected_root:
        return False, "unexpected_root"
    package_parts = path.parts[1:]
    folded = {part.casefold() for part in package_parts}
    if any(part == ".env" or part.startswith(".env.") for part in package_parts):
        return False, "secret_like_path"
    if folded & {item.casefold() for item in FORBIDDEN_PACKAGE_PATHS}:
        return False, "forbidden_package_path"
    filename = package_parts[-1].casefold()
    if filename.endswith((".db", ".sqlite", ".log", ".pyc", ".pyo", ".tsbuildinfo")):
        return False, "forbidden_file_suffix"
    return True, None


def _zip_members(path: Path, root: str) -> tuple[dict[str, zipfile.ZipInfo], list[dict[str, str]]]:
    members: dict[str, zipfile.ZipInfo] = {}
    folded_members: set[str] = set()
    errors: list[dict[str, str]] = []
    try:
        with zipfile.ZipFile(path) as archive:
            for info in archive.infolist():
                if info.filename in members:
                    errors.append({"member": info.filename, "reason": "duplicate_member"})
                    continue
                folded = info.filename.casefold()
                if folded in folded_members:
                    errors.append({"member": info.filename, "reason": "casefold_member_collision"})
                    continue
                folded_members.add(folded)
                safe, reason = _safe_member(info.filename, root)
                mode = (info.external_attr >> 16) & 0o170000
                if not safe:
                    errors.append({"member": info.filename, "reason": str(reason)})
                elif info.is_dir():
                    errors.append({"member": info.filename, "reason": "directory_entry_not_allowed"})
                elif mode not in {0, stat.S_IFREG}:
                    errors.append({"member": info.filename, "reason": "special_file_not_allowed"})
                else:
                    members[info.filename] = info
    except (OSError, zipfile.BadZipFile) as exc:
        errors.append({"member": path.name, "reason": f"invalid_zip:{exc}"})
    return members, errors


def _tar_members(path: Path, root: str) -> tuple[dict[str, tarfile.TarInfo], list[dict[str, str]]]:
    members: dict[str, tarfile.TarInfo] = {}
    folded_members: set[str] = set()
    errors: list[dict[str, str]] = []
    try:
        with tarfile.open(path, mode="r:gz") as archive:
            for info in archive.getmembers():
                if info.name in members:
                    errors.append({"member": info.name, "reason": "duplicate_member"})
                    continue
                folded = info.name.casefold()
                if folded in folded_members:
                    errors.append({"member": info.name, "reason": "casefold_member_collision"})
                    continue
                folded_members.add(folded)
                safe, reason = _safe_member(info.name, root)
                if not safe:
                    errors.append({"member": info.name, "reason": str(reason)})
                elif not info.isfile():
                    errors.append({"member": info.name, "reason": "special_or_directory_entry_not_allowed"})
                else:
                    members[info.name] = info
    except (OSError, tarfile.TarError) as exc:
        errors.append({"member": path.name, "reason": f"invalid_tar:{exc}"})
    return members, errors


def _content_digest(root: Path) -> tuple[str, int, int]:
    digest = hashlib.sha256()
    count = 0
    size_total = 0
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        size = path.stat().st_size
        file_digest = _sha256_path(path)
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(size).encode("ascii"))
        digest.update(b"\0")
        digest.update(file_digest.encode("ascii"))
        digest.update(b"\n")
        count += 1
        size_total += size
    return digest.hexdigest(), count, size_total


def _extract_zip(path: Path, destination: Path, members: dict[str, zipfile.ZipInfo]) -> None:
    with zipfile.ZipFile(path) as archive:
        for name in sorted(members):
            target = destination.joinpath(*PurePosixPath(name).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(members[name]) as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)


def _extract_tar(path: Path, destination: Path, members: dict[str, tarfile.TarInfo]) -> None:
    with tarfile.open(path, mode="r:gz") as archive:
        for name in sorted(members):
            source = archive.extractfile(members[name])
            if source is None:
                raise ValueError(f"Unable to read tar member: {name}")
            target = destination.joinpath(*PurePosixPath(name).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            with source, target.open("wb") as output:
                shutil.copyfileobj(source, output)


def _sbom_checks(sbom: dict[str, Any] | None, checks: list[dict[str, Any]]) -> dict[str, int]:
    if sbom is None:
        return {"components": 0, "npm": 0, "pypi": 0}
    components = sbom.get("components")
    metadata = sbom.get("metadata")
    references = [item.get("bom-ref") for item in components] if isinstance(components, list) else []
    valid = (
        sbom.get("bomFormat") == "CycloneDX"
        and sbom.get("specVersion") == "1.6"
        and isinstance(metadata, dict)
        and isinstance(components, list)
        and bool(components)
        and all(isinstance(item, dict) and item.get("name") and item.get("version") and item.get("purl") for item in components)
        and len(references) == len(set(references))
    )
    checks.append(
        _pass("sbom_structure", "CycloneDX SBOM structure is valid", component_count=len(components))
        if valid
        else _blocking("sbom_structure", "CycloneDX SBOM structure is valid", reason="invalid_or_duplicate_components")
    )
    if not isinstance(components, list):
        return {"components": 0, "npm": 0, "pypi": 0}
    return {
        "components": len(components),
        "npm": sum(1 for item in components if str(item.get("purl", "")).startswith("pkg:npm/")),
        "pypi": sum(1 for item in components if str(item.get("purl", "")).startswith("pkg:pypi/")),
    }


def verify_release_artifacts(
    release_dir: Path,
    *,
    generated_at: str | None = None,
    scratch_root: Path | None = None,
    extract_verified_to: Path | None = None,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    manifest_path = release_dir / "release-artifacts.json"
    manifest = _load_json(manifest_path, "Release artifact manifest", checks)
    checksums = _parse_checksums(release_dir / "SHA256SUMS", checks)

    if manifest is None:
        return _report(release_dir, generated_at, checks, None, {}, [])
    root = manifest.get("archive_root")
    artifacts = manifest.get("artifacts")
    required_fields = ("schema_version", "project", "version_label", "commit", "archive_root", "source_date_epoch", "package_file_count", "package_uncompressed_size", "package_content_sha256", "proof_boundary")
    missing = [field for field in required_fields if manifest.get(field) in (None, "")]
    valid_identity = not missing and manifest.get("schema_version") == SCHEMA_VERSION and manifest.get("project") == "DecisionAtlas"
    checks.append(
        _pass("manifest_identity", "Release manifest identity is valid", version=manifest.get("version_label"))
        if valid_identity
        else _blocking("manifest_identity", "Release manifest identity is valid", missing_fields=missing)
    )
    if not isinstance(root, str) or not root.startswith("decisionatlas-self-hosted-"):
        checks.append(_blocking("archive_root", "Archive root is versioned and safe", value=root))
        root = "invalid-root"
    else:
        checks.append(_pass("archive_root", "Archive root is versioned and safe", value=root))

    artifact_entries = artifacts if isinstance(artifacts, list) else []
    by_kind = {item.get("kind"): item for item in artifact_entries if isinstance(item, dict)}
    missing_kinds = sorted(REQUIRED_KINDS - set(by_kind))
    checks.append(
        _pass("artifact_kinds", "Required release artifact kinds are listed", kinds=sorted(by_kind))
        if not missing_kinds
        else _blocking("artifact_kinds", "Required release artifact kinds are listed", missing=missing_kinds)
    )

    expected_checksum_files = {"release-artifacts.json"}
    valid_artifacts: dict[str, Path] = {}
    for kind, item in sorted(by_kind.items()):
        filename = item.get("filename")
        if not isinstance(filename, str) or Path(filename).name != filename:
            checks.append(_blocking(f"artifact:{kind}", f"Artifact {kind} filename is safe", filename=filename))
            continue
        expected_checksum_files.add(filename)
        path = release_dir / filename
        if not path.is_file():
            checks.append(_blocking(f"artifact:{kind}", f"Artifact {kind} exists", filename=filename))
            continue
        digest = _sha256_path(path)
        size = path.stat().st_size
        expected_digest = item.get("sha256")
        expected_size = item.get("size")
        valid = digest == expected_digest == checksums.get(filename) and size == expected_size
        checks.append(
            _pass(f"artifact:{kind}", f"Artifact {kind} hash and size match", filename=filename, size=size)
            if valid
            else _blocking(
                f"artifact:{kind}",
                f"Artifact {kind} hash and size match",
                filename=filename,
                expected_sha256=expected_digest,
                actual_sha256=digest,
                expected_size=expected_size,
                actual_size=size,
            )
        )
        if valid:
            valid_artifacts[str(kind)] = path

    manifest_checksum_ok = checksums.get("release-artifacts.json") == _sha256_path(manifest_path)
    exact_checksum_set = set(checksums) == expected_checksum_files
    checks.append(
        _pass("checksum_coverage", "Checksums cover exactly the release artifacts", files=sorted(checksums))
        if manifest_checksum_ok and exact_checksum_set
        else _blocking(
            "checksum_coverage",
            "Checksums cover exactly the release artifacts",
            expected=sorted(expected_checksum_files),
            actual=sorted(checksums),
            manifest_hash_matches=manifest_checksum_ok,
        )
    )

    sbom_path = valid_artifacts.get("cyclonedx_sbom")
    sbom = _load_json(sbom_path, "CycloneDX SBOM", checks) if sbom_path is not None else None
    sbom_summary = _sbom_checks(sbom, checks)

    package_reports: list[dict[str, Any]] = []
    zip_path = valid_artifacts.get("zip")
    tar_path = valid_artifacts.get("tar_gz")
    zip_members: dict[str, zipfile.ZipInfo] = {}
    tar_members: dict[str, tarfile.TarInfo] = {}
    if zip_path is not None:
        zip_members, errors = _zip_members(zip_path, root)
        checks.append(
            _pass("zip_safety", "ZIP members are safe", member_count=len(zip_members))
            if not errors
            else _blocking("zip_safety", "ZIP members are safe", violations=errors[:20])
        )
    if tar_path is not None:
        tar_members, errors = _tar_members(tar_path, root)
        checks.append(
            _pass("tar_safety", "tar.gz members are safe", member_count=len(tar_members))
            if not errors
            else _blocking("tar_safety", "tar.gz members are safe", violations=errors[:20])
        )
    parity = bool(zip_members) and set(zip_members) == set(tar_members)
    checks.append(
        _pass("member_parity", "ZIP and tar.gz contain identical members", member_count=len(zip_members))
        if parity
        else _blocking(
            "member_parity",
            "ZIP and tar.gz contain identical members",
            zip_only=sorted(set(zip_members) - set(tar_members))[:20],
            tar_only=sorted(set(tar_members) - set(zip_members))[:20],
        )
    )

    expected_count = manifest.get("package_file_count")
    expected_size = manifest.get("package_uncompressed_size")
    zip_size = sum(info.file_size for info in zip_members.values())
    tar_size = sum(info.size for info in tar_members.values())
    metadata_matches = (
        parity
        and isinstance(expected_count, int)
        and isinstance(expected_size, int)
        and len(zip_members) == expected_count
        and zip_size == expected_size
        and tar_size == expected_size
    )
    checks.append(
        _pass(
            "archive_metadata",
            "Archive member counts and uncompressed sizes match the release manifest",
            file_count=expected_count,
            uncompressed_size=expected_size,
        )
        if metadata_matches
        else _blocking(
            "archive_metadata",
            "Archive member counts and uncompressed sizes match the release manifest",
            expected_file_count=expected_count,
            zip_file_count=len(zip_members),
            tar_file_count=len(tar_members),
            expected_uncompressed_size=expected_size,
            zip_uncompressed_size=zip_size,
            tar_uncompressed_size=tar_size,
        )
    )

    if not any(check["status"] == "blocking" for check in checks) and zip_path and tar_path:
        scratch_parent = scratch_root
        with tempfile.TemporaryDirectory(prefix="decisionatlas-release-verify-", dir=scratch_parent) as temporary:
            temporary_path = Path(temporary)
            extractors: list[tuple[str, Path, dict[str, Any], Callable[..., None]]] = [
                ("zip", zip_path, zip_members, _extract_zip),
                ("tar_gz", tar_path, tar_members, _extract_tar),
            ]
            for kind, archive_path, members, extractor in extractors:
                destination = temporary_path / kind
                destination.mkdir(parents=True)
                extractor(archive_path, destination, members)
                package_root = destination / root
                digest, file_count, total_size = _content_digest(package_root)
                content_ok = (
                    digest == manifest.get("package_content_sha256")
                    and file_count == manifest.get("package_file_count")
                    and total_size == manifest.get("package_uncompressed_size")
                )
                checks.append(
                    _pass(f"content:{kind}", f"Extracted {kind} package content matches manifest", file_count=file_count)
                    if content_ok
                    else _blocking(
                        f"content:{kind}",
                        f"Extracted {kind} package content matches manifest",
                        actual_sha256=digest,
                        actual_file_count=file_count,
                        actual_size=total_size,
                    )
                )
                package_report = verify_package(package_root, generated_at=generated_at)
                package_reports.append(
                    {
                        "archive_kind": kind,
                        "status": package_report["status"],
                        "runnable_status": package_report.get("runnable_status"),
                        "checked_file_count": package_report.get("checked_file_count"),
                        "blocker_count": len(package_report.get("blockers", [])),
                    }
                )
                checks.append(
                    _pass(f"package:{kind}", f"Extracted {kind} package passes verifier", checked_file_count=package_report.get("checked_file_count"))
                    if package_report["status"] == "pass"
                    else _blocking(f"package:{kind}", f"Extracted {kind} package passes verifier", blocker_count=len(package_report.get("blockers", [])))
                )

    if extract_verified_to is not None and not any(check["status"] == "blocking" for check in checks):
        if extract_verified_to.exists() and (not extract_verified_to.is_dir() or any(extract_verified_to.iterdir())):
            checks.append(
                _blocking(
                    "retained_extraction",
                    "Verified archive extraction target is empty",
                    reason="target_exists_and_is_not_empty",
                )
            )
        elif zip_path is None:
            checks.append(_blocking("retained_extraction", "Verified ZIP is available for retained extraction"))
        else:
            extract_verified_to.mkdir(parents=True, exist_ok=True)
            _extract_zip(zip_path, extract_verified_to, zip_members)
            retained_root = extract_verified_to / root
            retained_report = verify_package(retained_root, generated_at=generated_at)
            checks.append(
                _pass(
                    "retained_extraction",
                    "Verified ZIP was safely extracted to the operator-selected directory",
                    package_root=f"<operator-selected>/{root}",
                )
                if retained_report["status"] == "pass"
                else _blocking(
                    "retained_extraction",
                    "Verified ZIP was safely extracted to the operator-selected directory",
                    blocker_count=len(retained_report.get("blockers", [])),
                )
            )

    return _report(release_dir, generated_at, checks, manifest, sbom_summary, package_reports)


def _report(
    release_dir: Path,
    generated_at: str | None,
    checks: list[dict[str, Any]],
    manifest: dict[str, Any] | None,
    sbom_summary: dict[str, int],
    package_reports: list[dict[str, Any]],
) -> dict[str, Any]:
    blockers = [check for check in checks if check["status"] == "blocking"]
    boundary = manifest.get("proof_boundary", {}) if manifest else {}
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at or datetime.now(UTC).isoformat(),
        "status": "blocking" if blockers else "pass",
        "release_directory": "<operator-selected-release-dir>",
        "version_label": manifest.get("version_label") if manifest else None,
        "commit": manifest.get("commit") if manifest else None,
        "archive_root": manifest.get("archive_root") if manifest else None,
        "package_content_sha256": manifest.get("package_content_sha256") if manifest else None,
        "host_proof_level": "independent_runner_release_artifact",
        "is_customer_controlled": False,
        "proof_boundary": boundary,
        "sbom": sbom_summary,
        "package_verification": package_reports,
        "checks": checks,
        "blockers": blockers,
        "warnings": [
            "SHA-256 does not authenticate the publisher; cryptographic signing is not provided.",
            "Independent release-artifact verification is not customer-controlled-host installation proof.",
        ],
    }


def _write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Self-Hosted Release Artifact Verification",
        "",
        f"- Status: `{report['status']}`",
        f"- Version: `{report.get('version_label')}`",
        f"- Commit: `{report.get('commit')}`",
        f"- Proof level: `{report['host_proof_level']}`",
        "- Customer controlled: `false`",
        f"- Blockers: `{len(report['blockers'])}`",
        "",
        "## Checks",
        "",
        "| Check | Status | Details |",
        "| --- | --- | --- |",
    ]
    for check in report["checks"]:
        details = json.dumps(check.get("details", {}), ensure_ascii=True, sort_keys=True)
        lines.append(f"| {check['label']} | {check['status']} | `{details}` |")
    lines.extend(["", "## Boundaries", ""])
    lines.extend(f"- {warning}" for warning in report["warnings"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify DecisionAtlas self-hosted release archives and metadata.")
    parser.add_argument("--release-dir", type=Path, required=True)
    parser.add_argument("--scratch-root", type=Path)
    parser.add_argument("--extract-verified-to", type=Path)
    parser.add_argument("--output-json", type=Path, default=Path(".tmp/self-hosted-release-artifact-verification.json"))
    parser.add_argument("--output-markdown", type=Path, default=Path(".tmp/self-hosted-release-artifact-verification.md"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = verify_release_artifacts(
            args.release_dir,
            scratch_root=args.scratch_root,
            extract_verified_to=args.extract_verified_to,
        )
    except (OSError, ValueError) as exc:
        print(f"Release artifact verification failed: {exc}", file=sys.stderr)
        return 1
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_bytes(_json_bytes(report))
    _write_markdown(args.output_markdown, report)
    print(f"Release artifact verification status: {report['status']}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
