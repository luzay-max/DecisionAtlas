from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event
import hashlib

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
import pytest

from app.db.models import Artifact, Workspace
from app.ingest.github_importer import GitHubImporter
from app.ingest.github_document_selection import select_high_signal_repository_documents
from app.ingest.github_types import GitHubArtifactPayload
from app.ingest.github_types import GitHubRepositoryFile
from app.repositories.import_jobs import ImportJobRepository


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
    for artifact in artifacts:
        capture = artifact.metadata_json["decisionatlas_capture"]
        assert capture["schema_version"] == 1
        assert capture["method"] in {"github_api", "github_contents_api"}
        assert capture["content_sha256"] == hashlib.sha256(artifact.content.encode("utf-8")).hexdigest()
        assert capture["captured_at"].endswith("+00:00")
    assert artifacts[1].metadata_json["blob_sha"] is None  # Fake fixture IDs are not real Git object IDs.



def test_importer_fails_closed_when_markdown_changes_after_tree_listing(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "importer-race.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")

    class MovingBranchClient(FakeGitHubClient):
        def list_repository_files(self, repo: str, *, ref: str | None = None):
            files = super().list_repository_files(repo, ref=ref)
            expected_content = b"# Earlier README"
            git_blob = hashlib.sha1(
                f"blob {len(expected_content)}\0".encode("ascii") + expected_content,
                usedforsecurity=False,
            ).hexdigest()
            files[0] = GitHubRepositoryFile(path="README.md", sha=git_blob, size=len(expected_content))
            return files

    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        session.add(Workspace(slug="demo-workspace", name="Demo", repo_url="https://github.com/org/repo"))
        session.commit()

    with Session(engine) as session:
        importer = GitHubImporter(session, MovingBranchClient())
        with pytest.raises(ValueError, match="changed between tree listing and content fetch"):
            importer.import_repo(workspace_slug="demo-workspace", repo="org/repo")
        session.rollback()

    with Session(engine) as session:
        assert session.scalar(select(Artifact.id)) is None
    engine.dispose()


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


def test_slow_markdown_prefetch_does_not_block_pause_write_on_sqlite(
    tmp_path: Path, monkeypatch
) -> None:
    """An admin can pause while network fetch is blocked, before source writes."""
    db_path = tmp_path / "prefetch-pause-control.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")

    engine = create_engine(f"sqlite:///{db_path}", connect_args={"timeout": 0.25})
    with Session(engine) as session:
        workspace = Workspace(
            slug="demo-workspace", name="Demo", repo_url="https://github.com/org/repo"
        )
        session.add(workspace)
        session.flush()
        job = ImportJobRepository(session).create(
            job_id="prefetch-pause-job", workspace_id=workspace.id,
            repo="org/repo", mode="full",
        )
        ImportJobRepository(session).mark_running(job.job_id)
        session.commit()

    entered_download = Event()
    allow_download = Event()

    class SlowGitHubClient(FakeGitHubClient):
        def fetch_markdown_document(self, repo: str, *, path: str, ref: str) -> str:
            if path == "README.md":
                entered_download.set()
                if not allow_download.wait(timeout=12):
                    raise TimeoutError("Test did not release document fetch")
            return super().fetch_markdown_document(repo, path=path, ref=ref)

    def perform_import():
        with Session(engine) as session:
            importer = GitHubImporter(session, SlowGitHubClient())
            return importer.import_repo(workspace_slug="demo-workspace", repo="org/repo")

    try:
        with ThreadPoolExecutor(max_workers=1) as workers:
            running = workers.submit(perform_import)
            try:
                assert entered_download.wait(timeout=5)
                # Must not wait for the slow remote document to release its lock.
                with Session(engine) as admin:
                    paused = ImportJobRepository(admin).mark_paused("prefetch-pause-job")
                    admin.commit()
                    assert paused.status == "paused"

                # The importer itself is not responsible for orchestration:
                # resume before allowing the document to finish.
                with Session(engine) as admin:
                    resumed = ImportJobRepository(admin).mark_resumed("prefetch-pause-job")
                    admin.commit()
                    assert resumed.status == "running"

                # No source writes have happened during the remote wait.
                with Session(engine) as inspector:
                    assert inspector.scalars(select(Artifact)).all() == []
            finally:
                allow_download.set()
            result = running.result(timeout=12)
            assert result.imported_count == 5

        with Session(engine) as session:
            assert len(session.scalars(select(Artifact)).all()) == 5
    finally:
        engine.dispose()


def test_remote_markdown_failure_leaves_no_imported_artifact_writes(
    tmp_path: Path, monkeypatch
) -> None:
    """Even issue/PR source writes should not begin before doc verification."""
    db_path = tmp_path / "doc-download-error.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"timeout": 0.25})

    with Session(engine) as session:
        session.add(Workspace(
            slug="demo-workspace", name="Demo", repo_url="https://github.com/org/repo"
        ))
        session.commit()

    class FailingDocs(FakeGitHubClient):
        def fetch_markdown_document(self, repo: str, *, path: str, ref: str) -> str:
            # A separate writer must still be able to write while this failure
            # is raised, proving importer has not flushed issue rows yet.
            if path == "README.md":
                with Session(engine) as independent:
                    independent.add(Workspace(
                        slug="concurrent-check", name="Write check",
                        repo_url="https://github.com/org/other",
                    ))
                    independent.commit()
                raise RuntimeError("synthetic GitHub Markdown download failure")
            return super().fetch_markdown_document(repo, path=path, ref=ref)

    try:
        with Session(engine) as session:
            importer = GitHubImporter(session, FailingDocs())
            with pytest.raises(RuntimeError, match="synthetic GitHub Markdown"):
                importer.import_repo(workspace_slug="demo-workspace", repo="org/repo")
            session.rollback()
        with Session(engine) as session:
            assert session.scalars(select(Artifact)).all() == []
            assert session.scalar(select(Workspace).where(Workspace.slug == "concurrent-check")) is not None
    finally:
        engine.dispose()
