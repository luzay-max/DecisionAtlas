from app.indexing.chunker import chunk_text


def test_chunk_text_preserves_order() -> None:
    content = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."

    chunks = chunk_text(content, max_chars=25)

    assert chunks == ["First paragraph.", "Second paragraph.", "Third paragraph."]


def test_chunk_text_skips_empty_content() -> None:
    assert chunk_text("   ") == []
