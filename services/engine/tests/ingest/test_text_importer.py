from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.models import Artifact, Workspace
from app.ingest.text_importer import TextImporter


class FakePandocAdapter:
    def __init__(self, content: str | None):
        self.content = content

    def convert_to_markdown(self, path: Path) -> str | None:
        return self.content


def _prepare_db(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "text.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        session.add(Workspace(slug="demo-workspace", name="Demo", repo_url="https://github.com/org/repo"))
        session.commit()
    return engine


def test_text_importer_imports_txt_as_meeting_note(tmp_path: Path, monkeypatch) -> None:
    engine = _prepare_db(tmp_path, monkeypatch)
    note = tmp_path / "meeting.txt"
    note.write_text("meeting notes", encoding="utf-8")

    with Session(engine) as session:
        imported = TextImporter(session).import_file(workspace_slug="demo-workspace", file_path=note)

    with Session(engine) as session:
        artifact = session.scalar(select(Artifact))

    assert imported == 1
    assert artifact is not None
    assert artifact.type == "meeting_note"


def test_text_importer_skips_docx_when_pandoc_unavailable(tmp_path: Path, monkeypatch) -> None:
    engine = _prepare_db(tmp_path, monkeypatch)
    docx = tmp_path / "report.docx"
    docx.write_bytes(b"placeholder")

    with Session(engine) as session:
        imported = TextImporter(session, pandoc_adapter=FakePandocAdapter(None)).import_file(
            workspace_slug="demo-workspace",
            file_path=docx,
        )

    assert imported == 0


def test_text_importer_imports_docx_when_pandoc_available(tmp_path: Path, monkeypatch) -> None:
    engine = _prepare_db(tmp_path, monkeypatch)
    docx = tmp_path / "report.docx"
    docx.write_bytes(b"placeholder")

    with Session(engine) as session:
        imported = TextImporter(session, pandoc_adapter=FakePandocAdapter("# Converted")).import_file(
            workspace_slug="demo-workspace",
            file_path=docx,
        )

    with Session(engine) as session:
        artifact = session.scalar(select(Artifact))

    assert imported == 1
    assert artifact is not None
    assert artifact.content == "# Converted"
