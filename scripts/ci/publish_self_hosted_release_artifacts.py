from __future__ import annotations

import argparse
from datetime import UTC, datetime
import gzip
import hashlib
import json
import os
import platform
from pathlib import Path
import re
import sys
import tarfile
import tomllib
from typing import Any, Iterable
from urllib.parse import quote
import zipfile

from verify_self_hosted_package import verify_package


SCHEMA_VERSION = 1
CYCLONEDX_SPEC_VERSION = "1.6"
DEFAULT_OUTPUT_ROOT = Path(".tmp/self-hosted-release-artifacts")
VERSION_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
COMMIT_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
ZIP_MIN_EPOCH = 315532800


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")


def _safe_version(value: str) -> str:
    if not VERSION_PATTERN.fullmatch(value) or value in {".", ".."}:
        raise ValueError("Version label must use only letters, digits, dot, underscore, and hyphen.")
    return value


def _source_date_epoch(value: int | None) -> int:
    if value is not None:
        epoch = value
    else:
        raw = os.environ.get("SOURCE_DATE_EPOCH", "0")
        try:
            epoch = int(raw)
        except ValueError as exc:
            raise ValueError("SOURCE_DATE_EPOCH must be an integer.") from exc
    if epoch < 0:
        raise ValueError("source-date epoch must be non-negative.")
    return epoch


def _package_files(package_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(package_dir.rglob("*"), key=lambda item: item.relative_to(package_dir).as_posix()):
        relative = path.relative_to(package_dir)
        if path.is_symlink():
            raise ValueError(f"Release publication refuses symbolic link: {relative.as_posix()}")
        if path.is_file():
            files.append(path)
    return files


def _content_inventory(package_dir: Path, files: Iterable[Path]) -> tuple[list[dict[str, Any]], str, int]:
    inventory: list[dict[str, Any]] = []
    aggregate = hashlib.sha256()
    total_size = 0
    for path in files:
        relative = path.relative_to(package_dir).as_posix()
        size = path.stat().st_size
        digest = _sha256_path(path)
        inventory.append({"path": relative, "size": size, "sha256": digest})
        aggregate.update(relative.encode("utf-8"))
        aggregate.update(b"\0")
        aggregate.update(str(size).encode("ascii"))
        aggregate.update(b"\0")
        aggregate.update(digest.encode("ascii"))
        aggregate.update(b"\n")
        total_size += size
    return inventory, aggregate.hexdigest(), total_size


def _pnpm_components(lockfile: Path) -> list[dict[str, str]]:
    components: dict[str, dict[str, str]] = {}
    in_packages = False
    for line in lockfile.read_text(encoding="utf-8").splitlines():
        if line == "packages:":
            in_packages = True
            continue
        if in_packages and line and not line.startswith((" ", "\t")):
            break
        if not in_packages or not line.startswith("  ") or line.startswith("    ") or not line.rstrip().endswith(":"):
            continue
        key = line.strip()[:-1].strip("'\"").lstrip("/")
        key = key.split("(", 1)[0]
        split_at = key.rfind("@")
        if split_at <= 0:
            continue
        name = key[:split_at]
        version = key[split_at + 1 :]
        if not name or not version or version.startswith(("link:", "workspace:", "file:")):
            continue
        purl_name = quote(name, safe="/")
        purl = f"pkg:npm/{purl_name}@{version}"
        components[purl] = {
            "type": "library",
            "name": name,
            "version": version,
            "purl": purl,
            "bom-ref": purl,
        }
    return [components[key] for key in sorted(components)]


def _python_components(lockfile: Path) -> list[dict[str, str]]:
    data = tomllib.loads(lockfile.read_text(encoding="utf-8"))
    components: dict[str, dict[str, str]] = {}
    for item in data.get("package", []):
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        version = item.get("version")
        if not isinstance(name, str) or not isinstance(version, str) or not name or not version:
            continue
        normalized_name = re.sub(r"[-_.]+", "-", name).lower()
        purl = f"pkg:pypi/{quote(normalized_name)}@{version}"
        components[purl] = {
            "type": "library",
            "name": name,
            "version": version,
            "purl": purl,
            "bom-ref": purl,
        }
    return [components[key] for key in sorted(components)]


def build_sbom(
    *,
    package_dir: Path,
    version: str,
    commit: str,
    package_content_sha256: str,
) -> dict[str, Any]:
    pnpm_lock = package_dir / "pnpm-lock.yaml"
    uv_lock = package_dir / "services/engine/uv.lock"
    components = _pnpm_components(pnpm_lock) + _python_components(uv_lock)
    components.sort(key=lambda item: item["bom-ref"])
    app_ref = f"pkg:generic/decisionatlas@{quote(version)}"
    return {
        "bomFormat": "CycloneDX",
        "specVersion": CYCLONEDX_SPEC_VERSION,
        "serialNumber": f"urn:uuid:{_digest_uuid(package_content_sha256)}",
        "version": 1,
        "metadata": {
            "component": {
                "type": "application",
                "name": "DecisionAtlas",
                "version": version,
                "bom-ref": app_ref,
                "purl": app_ref,
                "properties": [
                    {"name": "decisionatlas:commit", "value": commit},
                    {"name": "decisionatlas:package-content-sha256", "value": package_content_sha256},
                ],
            },
            "properties": [
                {"name": "decisionatlas:lockfile:pnpm-lock.yaml:sha256", "value": _sha256_path(pnpm_lock)},
                {"name": "decisionatlas:lockfile:services/engine/uv.lock:sha256", "value": _sha256_path(uv_lock)},
                {"name": "decisionatlas:sbom-scope", "value": "locked-node-and-python-dependencies"},
            ],
        },
        "components": components,
    }


def _digest_uuid(hex_digest: str) -> str:
    value = bytearray.fromhex(hex_digest[:32])
    value[6] = (value[6] & 0x0F) | 0x50
    value[8] = (value[8] & 0x3F) | 0x80
    text = value.hex()
    return f"{text[:8]}-{text[8:12]}-{text[12:16]}-{text[16:20]}-{text[20:]}"


def _zip_datetime(epoch: int) -> tuple[int, int, int, int, int, int]:
    import datetime

    value = datetime.datetime.fromtimestamp(max(epoch, ZIP_MIN_EPOCH), tz=datetime.UTC)
    return value.year, value.month, value.day, value.hour, value.minute, value.second - (value.second % 2)


def _write_zip(*, archive: Path, package_dir: Path, files: list[Path], root_name: str, epoch: int) -> None:
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as target:
        for path in files:
            relative = path.relative_to(package_dir).as_posix()
            member = f"{root_name}/{relative}"
            info = zipfile.ZipInfo(member, date_time=_zip_datetime(epoch))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.flag_bits |= 0x800
            target.writestr(info, path.read_bytes(), compresslevel=9)


def _write_tar_gz(*, archive: Path, package_dir: Path, files: list[Path], root_name: str, epoch: int) -> None:
    with archive.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=epoch) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as target:
                for path in files:
                    relative = path.relative_to(package_dir).as_posix()
                    member = f"{root_name}/{relative}"
                    info = tarfile.TarInfo(member)
                    info.size = path.stat().st_size
                    info.mtime = epoch
                    info.mode = 0o644
                    info.uid = 0
                    info.gid = 0
                    info.uname = ""
                    info.gname = ""
                    with path.open("rb") as source:
                        target.addfile(info, source)


def _write_markdown(path: Path, report: dict[str, Any]) -> None:
    artifacts = report["artifacts"]
    lines = [
        "# Self-Hosted Release Artifact Publication",
        "",
        f"- Status: `{report['status']}`",
        f"- Version: `{report['version_label']}`",
        f"- Commit: `{report['commit']}`",
        f"- Package content SHA-256: `{report['package_content_sha256']}`",
        f"- Proof level: `{report['host_proof_level']}`",
        "- Customer controlled: `false`",
        "",
        "## Artifacts",
        "",
        "| Kind | Filename | Size | SHA-256 |",
        "| --- | --- | ---: | --- |",
    ]
    for item in artifacts:
        lines.append(f"| {item['kind']} | `{item['filename']}` | {item['size']} | `{item['sha256']}` |")
    lines.extend(
        [
            "",
            "## SBOM",
            "",
            f"- Components: `{report['sbom']['component_count']}`",
            f"- npm: `{report['sbom']['npm_component_count']}`",
            f"- PyPI: `{report['sbom']['pypi_component_count']}`",
            "",
            "## Boundaries",
            "",
            "- SHA-256 checks integrity relative to a trusted manifest source; cryptographic signing is not provided.",
            "- The SBOM covers locked Node and Python dependencies, not OS packages, container images, runtime plugins, or vulnerability analysis.",
            "- Archives do not include dependency caches; installation needs network access or an operator-supplied approved cache.",
            "- Independent publication evidence is not customer-controlled-host installation proof.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def publish_release_artifacts(
    *,
    package_dir: Path,
    output_root: Path,
    source_date_epoch: int | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    package_report = verify_package(package_dir, generated_at=generated_at)
    if package_report["status"] != "pass":
        raise ValueError("Input self-hosted package does not pass offline verification.")

    package_manifest = json.loads((package_dir / "manifest.json").read_text(encoding="utf-8"))
    version = _safe_version(str(package_manifest.get("version_label", "")))
    commit = str(package_manifest.get("commit", ""))
    if not COMMIT_PATTERN.fullmatch(commit):
        raise ValueError("Package commit is missing or unsafe.")
    if package_manifest.get("package_path") != ".":
        raise ValueError("Package manifest must use sanitized package_path '.'. Rebuild the package before publishing.")

    epoch = _source_date_epoch(source_date_epoch)
    files = _package_files(package_dir)
    inventory, content_digest, total_size = _content_inventory(package_dir, files)
    root_name = f"decisionatlas-self-hosted-{version}"
    output_dir = output_root / version
    output_dir.mkdir(parents=True, exist_ok=True)
    for existing in output_dir.iterdir():
        if existing.is_file():
            existing.unlink()
        else:
            raise ValueError(f"Release output contains unexpected directory: {existing.name}")

    zip_name = f"{root_name}.zip"
    tar_name = f"{root_name}.tar.gz"
    sbom_name = f"{root_name}.cdx.json"
    zip_path = output_dir / zip_name
    tar_path = output_dir / tar_name
    sbom_path = output_dir / sbom_name

    _write_zip(archive=zip_path, package_dir=package_dir, files=files, root_name=root_name, epoch=epoch)
    _write_tar_gz(archive=tar_path, package_dir=package_dir, files=files, root_name=root_name, epoch=epoch)
    sbom = build_sbom(
        package_dir=package_dir,
        version=version,
        commit=commit,
        package_content_sha256=content_digest,
    )
    sbom_path.write_bytes(_json_bytes(sbom))

    release_artifacts = []
    for kind, path in (("zip", zip_path), ("tar_gz", tar_path), ("cyclonedx_sbom", sbom_path)):
        release_artifacts.append(
            {"kind": kind, "filename": path.name, "size": path.stat().st_size, "sha256": _sha256_path(path)}
        )
    release_manifest = {
        "schema_version": SCHEMA_VERSION,
        "project": "DecisionAtlas",
        "version_label": version,
        "commit": commit,
        "archive_root": root_name,
        "source_date_epoch": epoch,
        "package_file_count": len(inventory),
        "package_uncompressed_size": total_size,
        "package_content_sha256": content_digest,
        "artifacts": release_artifacts,
        "sbom": {
            "format": "CycloneDX",
            "spec_version": CYCLONEDX_SPEC_VERSION,
            "filename": sbom_name,
            "component_count": len(sbom["components"]),
        },
        "proof_boundary": {
            "host_proof_level": "release_artifact_publication",
            "is_customer_controlled": False,
            "cryptographic_signing": "not_provided",
            "vulnerability_analysis": "not_provided",
            "dependency_cache": "not_included",
            "customer_host_installation": "requires_separate_sanitized_external_evidence",
        },
    }
    manifest_path = output_dir / "release-artifacts.json"
    manifest_path.write_bytes(_json_bytes(release_manifest))

    checksum_paths = [zip_path, tar_path, sbom_path, manifest_path]
    checksums_path = output_dir / "SHA256SUMS"
    checksums_path.write_text(
        "".join(f"{_sha256_path(path)}  {path.name}\n" for path in sorted(checksum_paths, key=lambda item: item.name)),
        encoding="utf-8",
    )

    npm_count = sum(1 for item in sbom["components"] if item["purl"].startswith("pkg:npm/"))
    pypi_count = sum(1 for item in sbom["components"] if item["purl"].startswith("pkg:pypi/"))
    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at or datetime.now(UTC).isoformat(),
        "status": "pass",
        "version_label": version,
        "commit": commit,
        "output_directory": output_dir.as_posix(),
        "archive_root": root_name,
        "source_date_epoch": epoch,
        "package_file_count": len(inventory),
        "package_uncompressed_size": total_size,
        "package_content_sha256": content_digest,
        "artifacts": release_artifacts,
        "checksum_filename": checksums_path.name,
        "release_manifest_filename": manifest_path.name,
        "sbom": {
            "filename": sbom_name,
            "component_count": len(sbom["components"]),
            "npm_component_count": npm_count,
            "pypi_component_count": pypi_count,
        },
        "host_proof_level": "release_artifact_publication",
        "is_customer_controlled": False,
        "toolchain": {"python": platform.python_version(), "platform": platform.system().lower()},
        "blockers": [],
        "warnings": [
            "Cryptographic signing is not provided.",
            "Dependency caches and customer-controlled-host installation proof are not included.",
        ],
    }
    return report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish portable DecisionAtlas self-hosted release artifacts.")
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--source-date-epoch", type=int)
    parser.add_argument("--output-json", type=Path, default=Path(".tmp/self-hosted-release-publication.json"))
    parser.add_argument("--output-markdown", type=Path, default=Path(".tmp/self-hosted-release-publication.md"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = publish_release_artifacts(
            package_dir=args.package,
            output_root=args.output_root,
            source_date_epoch=args.source_date_epoch,
        )
    except (OSError, ValueError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
        print(f"Release artifact publication failed: {exc}", file=sys.stderr)
        return 1
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_bytes(_json_bytes(report))
    _write_markdown(args.output_markdown, report)
    print(f"Release artifacts written to {report['output_directory']}")
    print(f"Publication status: {report['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
