from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.models import Artifact, Workspace
from app.provenance import get_workspace_provenance


def _migrate(db_path: Path) -> None:
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")


def test_demo_workspace_is_classified_from_seeded_artifacts(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "demo-provenance.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    _migrate(db_path)
    engine = create_engine(f"sqlite:///{db_path}")

    with Session(engine) as session:
        workspace = Workspace(slug="demo-workspace", name="Demo", repo_url="https://github.com/org/repo")
        session.add(workspace)
        session.flush()
        session.add(
            Artifact(
                workspace_id=workspace.id,
                type="issue",
                source_id="seed-issue-1",
                repo="org/repo",
                title="Seeded demo item",
                content="seeded content",
                author="system",
                url=None,
                timestamp=None,
                metadata_json=None,
            )
        )
        session.commit()

        provenance = get_workspace_provenance(session=session, workspace=workspace)
        assert provenance.workspace_mode == "demo"


def test_imported_workspace_is_classified_from_non_seeded_artifacts(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "imported-provenance.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    _migrate(db_path)
    engine = create_engine(f"sqlite:///{db_path}")

    with Session(engine) as session:
        workspace = Workspace(slug="repo-workspace", name="Imported", repo_url="https://github.com/org/repo")
        session.add(workspace)
        session.flush()
        session.add(
            Artifact(
                workspace_id=workspace.id,
                type="issue",
                source_id="42",
                repo="org/repo",
                title="Imported issue",
                content="imported content",
                author="alice",
                url=None,
                timestamp=None,
                metadata_json=None,
            )
        )
        session.commit()

        provenance = get_workspace_provenance(session=session, workspace=workspace)
        assert provenance.workspace_mode == "imported"


def test_mixed_workspace_is_classified_when_seeded_and_imported_artifacts_exist(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "mixed-provenance.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    _migrate(db_path)
    engine = create_engine(f"sqlite:///{db_path}")

    with Session(engine) as session:
        workspace = Workspace(slug="demo-workspace", name="Mixed", repo_url="https://github.com/org/repo")
        session.add(workspace)
        session.flush()
        session.add_all(
            [
                Artifact(
                    workspace_id=workspace.id,
                    type="issue",
                    source_id="seed-issue-1",
                    repo="org/repo",
                    title="Seeded issue",
                    content="seeded content",
                    author="system",
                    url=None,
                    timestamp=None,
                    metadata_json=None,
                ),
                Artifact(
                    workspace_id=workspace.id,
                    type="pull_request",
                    source_id="7",
                    repo="org/repo",
                    title="Imported PR",
                    content="imported content",
                    author="alice",
                    url=None,
                    timestamp=None,
                    metadata_json=None,
                ),
            ]
        )
        session.commit()

        provenance = get_workspace_provenance(session=session, workspace=workspace)
        assert provenance.workspace_mode == "mixed"
