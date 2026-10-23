"""Prove that non-GitHub source payloads reuse the existing artifact pipeline."""
from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.models import Artifact, Workspace
from app.ingest.github_importer import GitHubImporter
from app.ingest.github_types import GitHubArtifactPayload, GitHubRepositoryFile


class StubProvider:
    def __init__(self, provider: str):
        self.provider = provider

    def fetch_issues(self, repo, *, since=None):
        return [GitHubArtifactPayload(
            artifact_type="issue", source_id=f"{self.provider}:issue:1", repo=repo,
            title="Architecture tradeoff", content="An issue with reasoning",
            author="maintainer", url=f"https://{self.provider}.com/{repo}/issues/1",
            timestamp=None, metadata_json={"provider": self.provider, "state": "closed"},
        )]

    def fetch_pull_requests(self, repo, *, since=None):
        return []

    def fetch_commits(self, repo, *, since=None):
        return []

    def get_default_branch(self, repo):
        return "main"

    def list_repository_files(self, repo, *, ref=None):
        return [GitHubRepositoryFile(path="docs/ADR-0001.md", sha="sha1", size=200)]

    def fetch_markdown_document(self, repo, *, path, ref):
        return "# Architecture\nUse a validated decision, not model guesswork."


@pytest.mark.parametrize(("provider", "repo", "expected_url"), [
    ("gitlab", "group/team/repo",
     "https://gitlab.com/group/team/repo/-/blob/main/docs/ADR-0001.md"),
    ("gitee", "group/repo",
     "https://gitee.com/group/repo/blob/main/docs/ADR-0001.md"),
])
def test_existing_importer_handles_other_providers_and_repeat_runs(
    tmp_path: Path, monkeypatch, provider: str, repo: str, expected_url: str,
) -> None:
    db = tmp_path / "provider.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db}")
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{db}")
    command.upgrade(config, "head")
    engine = create_engine(f"sqlite:///{db}")
    with Session(engine) as session:
        session.add(Workspace(
            slug="source-demo", name=repo, owner_scope="local-default",
            repo_identity=f"{provider}:{repo}", access_source_type=f"{provider}_public",
            repo_url=f"https://{provider}.com/{repo}",
        ))
        session.commit()
    for _ in range(2):
        with Session(engine) as session:
            result = GitHubImporter(session, StubProvider(provider)).import_repo(
                workspace_slug="source-demo", repo=repo, mode="full",
            )
            assert result.artifact_counts["doc"] == 1
    with Session(engine) as session:
        artifacts = session.scalars(select(Artifact)).all()
        assert len(artifacts) == 2
        doc = next(a for a in artifacts if a.type == "doc")
        assert doc.url == expected_url
        assert doc.metadata_json["source"] == f"{provider}_repo_doc"
        assert doc.metadata_json["signal_category"] == "decision"
        assert next(a for a in artifacts if a.type == "issue").source_id == f"{provider}:issue:1"
