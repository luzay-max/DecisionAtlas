from __future__ import annotations

from dataclasses import dataclass
import re


HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")


@dataclass(slots=True)
class ChunkPayload:
    content: str
    heading_path: list[str]
    section_title: str | None
    chunk_role: str
    boundary_kind: str

    def to_record(self, *, chunk_index: int) -> dict:
        return {
            "chunk_index": chunk_index,
            "content": self.content,
            "metadata_json": {
                "heading_path": self.heading_path,
                "section_title": self.section_title,
                "chunk_role": self.chunk_role,
                "boundary_kind": self.boundary_kind,
            },
        }


def _normalized_blocks(content: str) -> list[str]:
    return [part.strip() for part in re.split(r"\n\s*\n", content) if part.strip()]


def _slice_with_overlap(content: str, *, max_chars: int, overlap_chars: int) -> list[str]:
    if len(content) <= max_chars:
        return [content]

    step = max(max_chars - overlap_chars, 1)
    chunks: list[str] = []
    start = 0
    while start < len(content):
        chunk = content[start : start + max_chars].strip()
        if chunk:
            chunks.append(chunk)
        if start + max_chars >= len(content):
            break
        start += step
    return chunks


def _flush_group(
    *,
    content_parts: list[str],
    heading_path: list[str],
    section_title: str | None,
    boundary_kind: str,
    chunks: list[ChunkPayload],
) -> None:
    if not content_parts:
        return
    content = "\n\n".join(part for part in content_parts if part).strip()
    if not content:
        return
    chunks.append(
        ChunkPayload(
            content=content,
            heading_path=list(heading_path),
            section_title=section_title,
            chunk_role="section",
            boundary_kind=boundary_kind,
        )
    )


def _chunk_section(
    *,
    text: str,
    heading_path: list[str],
    max_chars: int,
    overlap_chars: int,
) -> list[ChunkPayload]:
    blocks = _normalized_blocks(text)
    if not blocks:
        return []

    section_title = heading_path[-1] if heading_path else None
    chunks: list[ChunkPayload] = []
    current_parts: list[str] = []
    current_size = 0

    for block in blocks:
        block_size = len(block)
        separator = 2 if current_parts else 0
        if block_size > max_chars:
            _flush_group(
                content_parts=current_parts,
                heading_path=heading_path,
                section_title=section_title,
                boundary_kind="structured_section" if heading_path else "paragraph_group",
                chunks=chunks,
            )
            current_parts = []
            current_size = 0
            for slice_content in _slice_with_overlap(block, max_chars=max_chars, overlap_chars=overlap_chars):
                chunks.append(
                    ChunkPayload(
                        content=slice_content,
                        heading_path=list(heading_path),
                        section_title=section_title,
                        chunk_role="slice",
                        boundary_kind="overlap_slice",
                    )
                )
            continue

        if current_parts and (current_size + separator + block_size) > max_chars:
            _flush_group(
                content_parts=current_parts,
                heading_path=heading_path,
                section_title=section_title,
                boundary_kind="structured_section" if heading_path else "paragraph_group",
                chunks=chunks,
            )
            current_parts = [block]
            current_size = block_size
            continue

        current_parts.append(block)
        current_size += separator + block_size

    _flush_group(
        content_parts=current_parts,
        heading_path=heading_path,
        section_title=section_title,
        boundary_kind="structured_section" if heading_path else "paragraph_group",
        chunks=chunks,
    )
    return chunks


def _structured_sections(content: str) -> list[tuple[list[str], str]]:
    lines = content.splitlines()
    sections: list[tuple[list[str], str]] = []
    heading_path: list[str] = []
    current_path: list[str] = []
    current_lines: list[str] = []

    def flush() -> None:
        text = "\n".join(current_lines).strip()
        if text:
            sections.append((list(current_path), text))

    for line in lines:
        match = HEADING_PATTERN.match(line.strip())
        if match:
            flush()
            level = len(match.group(1))
            title = match.group(2).strip()
            heading_path = heading_path[: level - 1] + [title]
            current_path = list(heading_path)
            current_lines = [f"{'#' * level} {title}"]
            continue
        current_lines.append(line)

    flush()
    return sections


def chunk_text(content: str, *, max_chars: int = 400, overlap_chars: int = 80) -> list[ChunkPayload]:
    normalized = content.strip()
    if not normalized:
        return []

    sections = _structured_sections(normalized)
    chunks: list[ChunkPayload] = []
    for heading_path, text in sections:
        chunks.extend(
            _chunk_section(
                text=text,
                heading_path=heading_path,
                max_chars=max_chars,
                overlap_chars=overlap_chars,
            )
        )
    return chunks
