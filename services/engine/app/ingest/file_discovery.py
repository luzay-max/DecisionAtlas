from __future__ import annotations

from pathlib import Path


def discover_markdown_files(root: Path) -> list[Path]:
    extensions = {".md", ".mdx"}
    return sorted(path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in extensions)


def discover_adr_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.md") if "adr" in {part.lower() for part in path.parts})
