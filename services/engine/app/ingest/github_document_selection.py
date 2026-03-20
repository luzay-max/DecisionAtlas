from __future__ import annotations

from collections import Counter
from pathlib import PurePosixPath

from app.ingest.github_types import GitHubRepositoryFile

TOP_LEVEL_MARKDOWN_FILES = {
    "readme.md",
    "readme.mdx",
    "architecture.md",
    "decisions.md",
    "changelog.md",
    "contributing.md",
}
TOP_LEVEL_PREFIXES = ("release_notes",)
EXCLUDED_PATH_PARTS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "vendor",
    "vendors",
    "__pycache__",
}
HIGH_SIGNAL_DIRECTORY_PARTS = {"docs", "adr", "adrs", "rfcs"}


def select_high_signal_repository_documents(
    files: list[GitHubRepositoryFile],
) -> tuple[list[GitHubRepositoryFile], dict[str, int]]:
    selected: list[GitHubRepositoryFile] = []
    skipped = Counter(
        {
            "non_markdown": 0,
            "generated_or_vendor_path": 0,
            "outside_high_signal_paths": 0,
        }
    )

    for file in files:
        reason = _skip_reason(file.path)
        if reason is None:
            selected.append(file)
        else:
            skipped[reason] += 1

    return selected, dict(skipped)


def _skip_reason(path_value: str) -> str | None:
    path = PurePosixPath(path_value)
    name = path.name.lower()
    suffix = path.suffix.lower()
    parts = {part.lower() for part in path.parts[:-1]}

    if parts & EXCLUDED_PATH_PARTS:
        return "generated_or_vendor_path"
    if suffix not in {".md", ".mdx"}:
        return "non_markdown"
    if len(path.parts) == 1 and (name in TOP_LEVEL_MARKDOWN_FILES or any(name.startswith(prefix) for prefix in TOP_LEVEL_PREFIXES)):
        return None
    if parts & HIGH_SIGNAL_DIRECTORY_PARTS:
        return None
    return "outside_high_signal_paths"
