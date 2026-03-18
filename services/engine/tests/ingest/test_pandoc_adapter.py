from __future__ import annotations

from pathlib import Path

from app.ingest.pandoc_adapter import PandocAdapter


def test_pandoc_adapter_returns_none_when_unavailable(monkeypatch) -> None:
    monkeypatch.setattr("app.ingest.pandoc_adapter.shutil.which", lambda _: None)

    adapter = PandocAdapter()

    assert adapter.convert_to_markdown(Path("report.docx")) is None
