from app.indexing.chunker import chunk_text


def test_chunk_text_preserves_order() -> None:
    content = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."

    chunks = chunk_text(content, max_chars=25)

    assert [chunk.content for chunk in chunks] == ["First paragraph.", "Second paragraph.", "Third paragraph."]
    assert all(chunk.chunk_role == "section" for chunk in chunks)


def test_chunk_text_skips_empty_content() -> None:
    assert chunk_text("   ") == []


def test_chunk_text_preserves_heading_context() -> None:
    content = "# Overview\nWhy this exists.\n\n## Tradeoffs\nWe accept extra complexity for better retrieval."

    chunks = chunk_text(content, max_chars=120)

    assert len(chunks) == 2
    assert chunks[0].section_title == "Overview"
    assert chunks[0].heading_path == ["Overview"]
    assert chunks[1].heading_path == ["Overview", "Tradeoffs"]
    assert chunks[1].boundary_kind == "structured_section"


def test_chunk_text_adds_overlap_for_large_sections() -> None:
    content = "# Rationale\n" + ("Alpha Beta Gamma Delta " * 20)

    chunks = chunk_text(content, max_chars=80, overlap_chars=20)

    assert len(chunks) > 1
    assert all(chunk.chunk_role == "slice" for chunk in chunks)
    assert all(chunk.boundary_kind == "overlap_slice" for chunk in chunks)
    assert chunks[0].content[-20:].strip()
    assert chunks[1].content[:20].strip()
