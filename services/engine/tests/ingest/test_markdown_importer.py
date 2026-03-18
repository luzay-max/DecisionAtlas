from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.models import Artifact, Workspace
from app.ingest.markdown_importer import MarkdownImporter


def test_markdown_importer_discovers_nested_docs_and_adrs(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "docs.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")

    docs_root = tmp_path / "repo"
    (docs_root / "docs").mkdir(parents=True)
    (docs_root / "docs" / "guide.md").write_text("---\ntitle: Demo\n---\n# Guide", encoding="utf-8")
    (docs_root / "docs" / "adr").mkdir()
    (docs_root / "docs" / "adr" / "0001-choice.md").write_text("# ADR", encoding="utf-8")

    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        session.add(Workspace(slug="demo-workspace", name="Demo", repo_url="https://github.com/org/repo"))
        session.commit()

    with Session(engine) as session:
        imported = MarkdownImporter(session).import_directory(
            workspace_slug="demo-workspace",
            root=docs_root,
            repo="org/repo",
        )

    with Session(engine) as session:
        artifacts = session.scalars(select(Artifact).order_by(Artifact.source_id)).all()

    assert imported == 2
    assert artifacts[0].source_id == "docs/adr/0001-choice.md"
    assert artifacts[1].content == "# Guide"
    assert artifacts[1].url == "https://github.com/org/repo/blob/main/docs/guide.md"
