from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.models import Artifact, Workspace
from app.ingest.github_types import GitHubImportResult
from app.jobs.import_jobs import queue_github_import, run_github_import
from app.llm.base import ExtractionRequest, ProviderTimeoutError


def test_run_github_import_rolls_back_partial_artifacts_on_failure(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "import-job-failure.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")

    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        session.add(Workspace(slug="github-org-repo", name="org/repo", repo_url="https://github.com/org/repo"))
        session.commit()

    class FailingImporter:
        def __init__(self, session, client) -> None:
            self.session = session

        def import_repo(self, *, workspace_slug: str, repo: str, mode: str = "full", since=None):
            workspace = self.session.scalar(select(Workspace).where(Workspace.slug == workspace_slug))
            assert workspace is not None
            self.session.add(
                Artifact(
                    workspace_id=workspace.id,
                    type="issue",
                    source_id="partial-1",
                    repo=repo,
                    title="Partial artifact",
                    content="This should be rolled back",
                    author="alice",
                    url="https://github.com/org/repo/issues/1",
                    timestamp=None,
                    metadata_json=None,
                )
            )
            self.session.flush()
            raise ValueError("Unsupported GitHub content encoding for CHANGELOG.md")

    monkeypatch.setattr("app.jobs.import_jobs.GitHubImporter", FailingImporter)
    monkeypatch.setattr(
        "app.jobs.import_jobs.build_runtime_providers",
        lambda settings: SimpleNamespace(embedder=object(), extraction_provider=object()),
    )

    queued_job = queue_github_import(workspace_slug="github-org-repo", repo="org/repo", mode="full")
    result = run_github_import(
        job_id=str(queued_job["job_id"]),
        workspace_slug="github-org-repo",
        repo="org/repo",
        mode="full",
    )

    assert result["status"] == "failed"
    assert result["imported_count"] == 0
    assert result["summary"]["stage"] == "importing_artifacts"
    assert result["summary"]["failure_category"] == "analysis_execution_failed"

    with Session(engine) as session:
        artifacts = session.scalars(select(Artifact)).all()

    assert artifacts == []


def test_run_github_import_succeeds_when_extraction_provider_times_out(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "import-job-timeout.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")

    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        session.add(Workspace(slug="github-org-repo", name="org/repo", repo_url="https://github.com/org/repo"))
        session.commit()

    class TimeoutImporter:
        def __init__(self, session, client) -> None:
            self.session = session

        def import_repo(self, *, workspace_slug: str, repo: str, mode: str = "full", since=None):
            workspace = self.session.scalar(select(Workspace).where(Workspace.slug == workspace_slug))
            assert workspace is not None
            self.session.add(
                Artifact(
                    workspace_id=workspace.id,
                    type="doc",
                    source_id="docs/architecture.md",
                    repo=repo,
                    title="Architecture",
                    content="We decided to use Redis as a cache because latency mattered.",
                    author=None,
                    url="https://github.com/org/repo/blob/main/docs/architecture.md",
                    timestamp=None,
                    metadata_json={"path": "docs/architecture.md", "signal_category": "architecture"},
                )
            )
            self.session.commit()
            return GitHubImportResult(
                imported_count=1,
                artifact_counts={"issue": 0, "pr": 0, "commit": 0, "doc": 1},
                selected_document_count=1,
                imported_document_count=1,
                skipped_document_counts={"non_markdown": 0},
                selected_document_categories={"architecture": 1},
            )

    class FakeEmbedder:
        def embed(self, chunks):
            return [[0.1, 0.2, 0.3] for _ in chunks]

    class TimeoutProvider:
        def extract_candidate(self, request: ExtractionRequest) -> str | None:
            raise ProviderTimeoutError("Timed out while calling extraction provider")

    monkeypatch.setattr("app.jobs.import_jobs.GitHubImporter", TimeoutImporter)
    monkeypatch.setattr(
        "app.jobs.import_jobs.build_runtime_providers",
        lambda settings: SimpleNamespace(embedder=FakeEmbedder(), extraction_provider=TimeoutProvider()),
    )

    queued_job = queue_github_import(workspace_slug="github-org-repo", repo="org/repo", mode="full")
    result = run_github_import(
        job_id=str(queued_job["job_id"]),
        workspace_slug="github-org-repo",
        repo="org/repo",
        mode="full",
    )

    assert result["status"] == "succeeded"
    assert result["summary"]["stage"] == "completed"
    assert result["summary"]["outcome"] == "insufficient_evidence"
    assert result["summary"]["extraction_summary"]["created_candidates"] == 0
    assert result["summary"]["extraction_summary"]["skipped_provider_timeout"] == 1
    assert result["summary"]["extraction_summary"]["total_artifacts"] == 1
    assert result["summary"]["extraction_summary"]["processed_artifacts"] == 1
