from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.models import Artifact, Workspace
from app.ingest.github_importer import GitHubImporter
from app.ingest.github_types import GitHubArtifactPayload


class FakeGitHubClient:
    def fetch_issues(self, repo: str, *, since=None):
        return [
            GitHubArtifactPayload(
                artifact_type="issue",
                source_id="1",
                repo=repo,
                title="Issue A",
                content="Issue body",
                author="alice",
                url="https://example.com/issues/1",
                timestamp=None,
                metadata_json={"number": 1},
            )
        ]

    def fetch_pull_requests(self, repo: str, *, since=None):
        return [
            GitHubArtifactPayload(
                artifact_type="pr",
                source_id="2",
                repo=repo,
                title="PR A",
                content="PR body",
                author="bob",
                url="https://example.com/pulls/2",
                timestamp=None,
                metadata_json={"number": 2},
            )
        ]

    def fetch_commits(self, repo: str, *, since=None):
        return [
            GitHubArtifactPayload(
                artifact_type="commit",
                source_id="sha123",
                repo=repo,
                title="Commit title",
                content="Commit body",
                author="carol",
                url="https://example.com/commit/sha123",
                timestamp=None,
                metadata_json={},
            )
        ]


def test_github_importer_persists_artifacts(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "importer.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")

    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        workspace = Workspace(slug="demo-workspace", name="Demo", repo_url="https://github.com/org/repo")
        session.add(workspace)
        session.commit()

    with Session(engine) as session:
        importer = GitHubImporter(session, FakeGitHubClient())
        imported_count = importer.import_repo(workspace_slug="demo-workspace", repo="org/repo")

    with Session(engine) as session:
        artifacts = session.scalars(select(Artifact).order_by(Artifact.type)).all()

    assert imported_count == 3
    assert [artifact.type for artifact in artifacts] == ["commit", "issue", "pr"]
    assert artifacts[0].repo == "org/repo"
    assert artifacts[1].author == "alice"
    assert artifacts[2].source_id == "2"


def test_github_importer_is_idempotent_on_repeat_runs(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "importer-repeat.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")

    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        session.add(Workspace(slug="demo-workspace", name="Demo", repo_url="https://github.com/org/repo"))
        session.commit()

    with Session(engine) as session:
        importer = GitHubImporter(session, FakeGitHubClient())
        importer.import_repo(workspace_slug="demo-workspace", repo="org/repo")

    with Session(engine) as session:
        importer = GitHubImporter(session, FakeGitHubClient())
        importer.import_repo(workspace_slug="demo-workspace", repo="org/repo")

    with Session(engine) as session:
        artifacts = session.scalars(select(Artifact)).all()

    assert len(artifacts) == 3
