from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.models import Artifact, ArtifactChunk, Workspace
from app.indexing.embedder import FakeEmbedder
from app.indexing.index_artifact import index_artifact


def test_index_artifact_replaces_chunks_idempotently(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "index.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}")

    with Session(engine) as session:
        workspace = Workspace(slug="demo-workspace", name="Demo", repo_url="https://github.com/org/repo")
        session.add(workspace)
        session.flush()
        artifact = Artifact(
            workspace_id=workspace.id,
            type="doc",
            source_id="docs/guide.md",
            repo="org/repo",
            title="Guide",
            content="Alpha\n\nBeta",
            author=None,
            url=None,
            timestamp=None,
            metadata_json=None,
        )
        session.add(artifact)
        session.commit()
        artifact_id = artifact.id

    with Session(engine) as session:
        indexed_count = index_artifact(
            session=session,
            artifact_id=artifact_id,
            content="Alpha\n\nBeta",
            embedder=FakeEmbedder(),
        )

    with Session(engine) as session:
        first_pass = session.scalars(select(ArtifactChunk).where(ArtifactChunk.artifact_id == artifact_id)).all()

    with Session(engine) as session:
        second_count = index_artifact(
            session=session,
            artifact_id=artifact_id,
            content="Alpha\n\nBeta",
            embedder=FakeEmbedder(),
        )

    with Session(engine) as session:
        second_pass = session.scalars(select(ArtifactChunk).where(ArtifactChunk.artifact_id == artifact_id)).all()

    assert indexed_count == 2
    assert second_count == 2
    assert len(first_pass) == 2
    assert len(second_pass) == 2
