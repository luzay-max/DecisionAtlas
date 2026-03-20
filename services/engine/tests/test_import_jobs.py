from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.models import Artifact, Workspace
from app.jobs.import_jobs import queue_github_import, run_github_import


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
