from __future__ import annotations

from datetime import UTC, datetime
import hashlib
import json
import os
import platform
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
from typing import Any, Callable, Iterable
from urllib.parse import quote

from publish_self_hosted_release_artifacts import build_sbom


SCHEMA_VERSION = 1
BUNDLE_TYPE = "decisionatlas-approved-offline-dependencies"
MANIFEST_FILENAME = "offline-dependency-bundle.json"
SBOM_FILENAME = "offline-dependency-bundle.cdx.json"
CHECKSUM_FILENAME = "SHA256SUMS"
REQUIRED_BINDINGS = (
    "manifest.json",
    "pnpm-lock.yaml",
    "services/engine/uv.lock",
    "apps/web/package.json",
    "docker-compose.yml",
)
REQUIRED_CATEGORIES = {
    "pnpm_store": "payload/pnpm/store",
    "uv_cache": "payload/uv/cache",
    "playwright_browsers": "payload/playwright/browsers",
    "container_images": "payload/containers/images.tar",
}
ALLOWED_CONTAINER_IMAGES = {
    "pgvector/pgvector:pg17",
    "redis:7.4-alpine",
}
FORBIDDEN_NAMES = {
    ".env",
    ".tmp",
    "node_modules",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "test-results",
}
SECRET_SUFFIXES = (".db", ".sqlite", ".log")
TOKEN_PATTERNS = (
    re.compile(r"github_pat_[A-Za-z0-9_]+"),
    re.compile(r"gh[opsu]_[A-Za-z0-9]+"),
    re.compile(r"(?i)(token|password|secret|api[_-]?key)\s*[=:]\s*\S+"),
)

CommandRunner = Callable[..., dict[str, Any]]


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path.name}")
    return value


def sanitize_text(value: str, *, replacements: dict[str, str] | None = None, limit: int = 4000) -> str:
    text = value
    for source, replacement in sorted((replacements or {}).items(), key=lambda item: len(item[0]), reverse=True):
        if source:
            text = text.replace(source, replacement).replace(source.replace("\\", "/"), replacement)
    for pattern in TOKEN_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return text[-limit:]


def run_command(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    timeout_seconds: int = 1800,
) -> dict[str, Any]:
    started = datetime.now(UTC)
    executable = shutil.which(command[0])
    resolved = [executable, *command[1:]] if executable else command
    try:
        completed = subprocess.run(
            resolved,
            cwd=cwd,
            env=env,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
        )
        return {
            "status": "pass" if completed.returncode == 0 else "blocking",
            "returncode": completed.returncode,
            "duration_seconds": round((datetime.now(UTC) - started).total_seconds(), 3),
            "stdout_tail": sanitize_text(completed.stdout or ""),
            "stderr_tail": sanitize_text(completed.stderr or ""),
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "status": "blocking",
            "returncode": None,
            "duration_seconds": round((datetime.now(UTC) - started).total_seconds(), 3),
            "error": sanitize_text(str(exc)),
        }


def uv_command(*arguments: str) -> list[str]:
    return ["uv", *arguments] if shutil.which("uv") else [sys.executable, "-m", "uv", *arguments]


def package_bindings(package_dir: Path) -> dict[str, str]:
    bindings: dict[str, str] = {}
    for relative in REQUIRED_BINDINGS:
        path = package_dir / relative
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"Required package binding is missing or unsafe: {relative}")
        bindings[relative] = sha256_path(path)
    return bindings


def compose_images(compose_path: Path) -> list[str]:
    images = []
    for line in compose_path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\s+image:\s*['\"]?([^'\"\s#]+)", line)
        if match:
            images.append(match.group(1))
    unique = sorted(set(images))
    if not unique:
        raise ValueError("docker-compose.yml does not declare any images.")
    unexpected = sorted(set(unique) - ALLOWED_CONTAINER_IMAGES)
    if unexpected:
        raise ValueError(f"Compose contains unapproved container images: {', '.join(unexpected)}")
    if set(unique) != ALLOWED_CONTAINER_IMAGES:
        missing = sorted(ALLOWED_CONTAINER_IMAGES - set(unique))
        raise ValueError(f"Compose is missing approved container images: {', '.join(missing)}")
    return unique


def safe_relative_path(value: str) -> PurePosixPath:
    if "\\" in value:
        raise ValueError(f"Backslash is not allowed in bundle paths: {value}")
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"Unsafe bundle path: {value}")
    names = {part.casefold() for part in path.parts}
    if names & {item.casefold() for item in FORBIDDEN_NAMES}:
        raise ValueError(f"Forbidden bundle path: {value}")
    if ".git" in names:
        uv_marker = value.startswith("payload/uv/cache/") and path.name.casefold() == ".git"
        if not uv_marker:
            raise ValueError(f"Git repository metadata is forbidden in bundle paths: {value}")
    if path.name.casefold().endswith(SECRET_SUFFIXES) or path.name.casefold().startswith(".env"):
        raise ValueError(f"Forbidden bundle file: {value}")
    return path


def category_for_path(relative: str) -> str | None:
    for category, prefix in REQUIRED_CATEGORIES.items():
        if relative == prefix or relative.startswith(f"{prefix}/"):
            return category
    return None


def inventory_payload(bundle_dir: Path) -> tuple[list[dict[str, Any]], str, int]:
    payload = bundle_dir / "payload"
    if not payload.is_dir() or payload.is_symlink():
        raise ValueError("Offline bundle payload directory is missing or unsafe.")
    inventory: list[dict[str, Any]] = []
    aggregate = hashlib.sha256()
    total_size = 0
    seen_casefold: set[str] = set()
    for path in sorted(payload.rglob("*"), key=lambda item: item.relative_to(bundle_dir).as_posix()):
        relative = path.relative_to(bundle_dir).as_posix()
        if path.is_symlink():
            raise ValueError(f"Offline bundle refuses symbolic link: {relative}")
        if not path.is_file():
            continue
        safe_relative_path(relative)
        folded = relative.casefold()
        if folded in seen_casefold:
            raise ValueError(f"Case-colliding bundle path: {relative}")
        seen_casefold.add(folded)
        category = category_for_path(relative)
        if category is None:
            raise ValueError(f"Payload file is outside approved categories: {relative}")
        size = path.stat().st_size
        digest = sha256_path(path)
        entry = {"path": relative, "category": category, "size": size, "sha256": digest}
        inventory.append(entry)
        aggregate.update(json.dumps(entry, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        aggregate.update(b"\n")
        total_size += size
    return inventory, aggregate.hexdigest(), total_size


def category_summaries(inventory: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    summaries = {
        category: {"path": path, "file_count": 0, "size": 0}
        for category, path in REQUIRED_CATEGORIES.items()
    }
    for item in inventory:
        summary = summaries[str(item["category"])]
        summary["file_count"] += 1
        summary["size"] += int(item["size"])
    return summaries


def platform_contract(tool_versions: dict[str, str]) -> dict[str, Any]:
    return {
        "os": platform.system().lower(),
        "architecture": platform.machine().lower(),
        "python": f"{sys.version_info.major}.{sys.version_info.minor}",
        "node": major_version(tool_versions.get("node", "")),
        "pnpm": tool_versions.get("pnpm"),
        "uv": tool_versions.get("uv"),
        "playwright": tool_versions.get("playwright"),
        "docker": tool_versions.get("docker"),
    }


def major_version(value: str) -> str | None:
    match = re.search(r"(?:^|\D)(\d+)(?:\.\d+)?", value)
    return match.group(1) if match else None


def container_components(images: list[dict[str, Any]]) -> list[dict[str, Any]]:
    components: list[dict[str, Any]] = []
    for item in images:
        reference = str(item["reference"])
        image_id = str(item["image_id"])
        digest = image_id.removeprefix("sha256:")
        purl = f"pkg:oci/{quote(reference, safe='/')}?repository_url=docker.io"
        components.append(
            {
                "type": "container",
                "name": reference,
                "version": digest[:16] or "unknown",
                "purl": purl,
                "bom-ref": f"{purl}#{digest}",
                "hashes": [{"alg": "SHA-256", "content": digest}] if re.fullmatch(r"[0-9a-fA-F]{64}", digest) else [],
                "properties": [{"name": "decisionatlas:container-image-id", "value": image_id}],
            }
        )
    return components


def build_offline_sbom(
    *,
    package_dir: Path,
    package_manifest: dict[str, Any],
    payload_digest: str,
    images: list[dict[str, Any]],
) -> dict[str, Any]:
    sbom = build_sbom(
        package_dir=package_dir,
        version=str(package_manifest.get("version_label", "unknown")),
        commit=str(package_manifest.get("commit", "unknown")),
        package_content_sha256=payload_digest,
    )
    sbom["components"] = sorted(
        [*sbom.get("components", []), *container_components(images)],
        key=lambda item: str(item.get("bom-ref", "")),
    )
    sbom["metadata"]["properties"].extend(
        [
            {"name": "decisionatlas:sbom-scope", "value": "offline-node-python-browser-and-container-dependencies"},
            {"name": "decisionatlas:offline-payload-sha256", "value": payload_digest},
        ]
    )
    return sbom


def write_checksums(bundle_dir: Path, paths: Iterable[Path]) -> None:
    lines = [f"{sha256_path(path)}  {path.relative_to(bundle_dir).as_posix()}" for path in sorted(paths)]
    (bundle_dir / CHECKSUM_FILENAME).write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_checksums(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", raw)
        if not match:
            raise ValueError("SHA256SUMS is malformed.")
        relative = match.group(2)
        safe_relative_path(relative)
        if relative in entries:
            raise ValueError(f"Duplicate checksum entry: {relative}")
        entries[relative] = match.group(1)
    return entries


def current_tool_versions(package_dir: Path, runner: CommandRunner = run_command) -> dict[str, str]:
    commands = {
        "node": ["node", "--version"],
        "pnpm": ["pnpm", "--version"],
        "uv": uv_command("--version"),
        "docker": ["docker", "version", "--format", "{{.Client.Version}}"],
    }
    versions: dict[str, str] = {}
    for name, command in commands.items():
        result = runner(command, cwd=package_dir, timeout_seconds=120)
        if result.get("status") != "pass":
            raise ValueError(f"Required tool is unavailable: {name}")
        output = str(result.get("stdout_tail", "")).strip().splitlines()[-1]
        match = re.search(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", output)
        if not match:
            raise ValueError(f"Required tool did not report a semantic version: {name}")
        versions[name] = match.group(0)
    web_package = load_json(package_dir / "apps/web/package.json")
    playwright_spec = web_package.get("devDependencies", {}).get("@playwright/test")
    if not isinstance(playwright_spec, str) or not re.search(r"\d+\.\d+\.\d+", playwright_spec):
        raise ValueError("Package does not declare a bounded Playwright version.")
    versions["playwright"] = re.search(r"\d+\.\d+\.\d+", playwright_spec).group(0)
    return versions


def generated_at(value: str | None = None) -> str:
    return value or datetime.now(UTC).isoformat()


def reset_owned_directory(path: Path, owned_root: Path) -> None:
    resolved = path.resolve()
    parent = owned_root.resolve()
    if resolved == parent or parent not in resolved.parents:
        raise ValueError(f"Refusing to reset path outside owned root: {path}")
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
