from __future__ import annotations


def chunk_text(content: str, *, max_chars: int = 400) -> list[str]:
    normalized = content.strip()
    if not normalized:
        return []

    paragraphs = [part.strip() for part in normalized.split("\n\n") if part.strip()]
    chunks: list[str] = []
    for paragraph in paragraphs:
        if len(paragraph) <= max_chars:
            chunks.append(paragraph)
            continue
        for start in range(0, len(paragraph), max_chars):
            chunks.append(paragraph[start : start + max_chars])
    return chunks
