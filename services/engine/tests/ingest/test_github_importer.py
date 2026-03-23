from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.models import Artifact, Workspace
from app.ingest.github_importer import GitHubImporter
from app.ingest.github_document_selection import select_high_signal_repository_documents
from app.ingest.github_types import GitHubArtifactPayload
from app.ingest.github_types import GitHubRepositoryFile


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

    def get_default_branch(self, repo: str) -> str:
        return "main"

    def list_repository_files(self, repo: str, *, ref: str | None = None):
        return [
            GitHubRepositoryFile(path="README.md", sha="readme-sha", size=120),
            GitHubRepositoryFile(path="docs/adr/0001-choice.md", sha="adr-sha", size=80),
            GitHubRepositoryFile(path="src/main.py", sha="code-sha", size=20),
            GitHubRepositoryFile(path="package-lock.json", sha="lock-sha", size=50),
        ]

    def fetch_markdown_document(self, repo: str, *, path: str, ref: str) -> str:
        return {
            "README.md": "# Demo Repo",
            "docs/adr/0001-choice.md": "# ADR",
        }[path]


def test_document_selection_prefers_high_signal_markdown_paths() -> None:
    selected, skipped = select_high_signal_repository_documents(
        [
            GitHubRepositoryFile(path="README.md", sha="1", size=10),
            GitHubRepositoryFile(path="docs/guide.md", sha="2", size=10),
            GitHubRepositoryFile(path="MIGRATION_GUIDE.md", sha="4", size=10),
            GitHubRepositoryFile(path="src/index.ts", sha="3", size=10),
            GitHubRepositoryFile(path="vendor/ARCHITECTURE.md", sha="4", size=10),
        ]
    )

    assert [item.path for item in selected] == ["README.md", "docs/guide.md", "MIGRATION_GUIDE.md"]
    assert skipped["non_markdown"] == 1
    assert skipped["generated_or_vendor_path"] == 1


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
        import_result = importer.import_repo(workspace_slug="demo-workspace", repo="org/repo")

    with Session(engine) as session:
        artifacts = session.scalars(select(Artifact).order_by(Artifact.type)).all()

    assert import_result.imported_count == 5
    assert import_result.artifact_counts == {"issue": 1, "pr": 1, "commit": 1, "doc": 2}
    assert import_result.selected_document_count == 2
    assert import_result.selected_document_categories == {"general": 1, "decision": 1}
    assert import_result.skipped_document_counts["non_markdown"] == 2
    assert [artifact.type for artifact in artifacts] == ["commit", "doc", "doc", "issue", "pr"]
    assert artifacts[0].repo == "org/repo"
    assert artifacts[1].source_id == "README.md"
    assert artifacts[1].metadata_json["signal_category"] == "general"
    assert artifacts[1].url == "https://github.com/org/repo/blob/main/README.md"
    assert artifacts[3].author == "alice"
    assert artifacts[4].source_id == "2"


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

    assert len(artifacts) == 5
