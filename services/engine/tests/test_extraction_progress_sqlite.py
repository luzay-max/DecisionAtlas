"""Reproduce a real GitHub pilot's SQLite concurrent-writer failure without network."""
from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.models import Decision, ImportJob, Workspace
from app.extractor.pipeline import ExtractionRunStats
from app.jobs.import_jobs import _build_extraction_progress_reporter
from app.repositories.import_jobs import ImportJobRepository


def test_extraction_progress_commits_with_candidate_transaction(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "progress-lock.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(config, "head")

    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as setup:
        workspace = Workspace(slug="github-pallets-click", name="pallets/click", repo_url="https://github.com/pallets/click")
        setup.add(workspace)
        setup.flush()
        ImportJobRepository(setup).create(
            job_id="real-public-progress", workspace_id=workspace.id, repo="pallets/click", mode="full"
        )
        workspace_id = workspace.id
        setup.commit()

    # Simulate a live extraction: candidate row has been INSERTed but is uncommitted.
    # A reporter opening its own SQLite connection and writing job summary would
    # block on the main transaction, then raise "database is locked".
    with Session(engine) as extraction:
        extraction.add(Decision(
            workspace_id=workspace_id,
            title="Migrate parameter spec",
            problem="Different audiences need different identifiers",
            chosen_option="Introduce Parameter.spec",
            tradeoffs="Deprecate older display name",
            confidence=0.7,
            review_state="candidate",
        ))
        extraction.flush()
        reporter = _build_extraction_progress_reporter(
            job_id="real-public-progress", session=extraction
        )
        reporter(ExtractionRunStats(total_artifacts=5, processed_artifacts=1, screened_artifacts=1))
        assert extraction.scalar(select(Decision).where(Decision.workspace_id == workspace_id)) is not None

    # Both progress metadata and candidate row have been committed together.
    with Session(engine) as verify:
        job = ImportJobRepository(verify).get_by_job_id("real-public-progress")
        assert job is not None
        assert job.summary_json["extraction_summary"]["processed_artifacts"] == 1
        assert verify.scalar(select(Decision).where(Decision.workspace_id == workspace_id)) is not None
    engine.dispose()


def test_paused_import_remains_active_for_deduplication(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "paused-active.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(config, "head")

    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        workspace = Workspace(slug="github-pallets-click", name="pallets/click")
        session.add(workspace)
        session.flush()
        jobs = ImportJobRepository(session)
        jobs.create(job_id="paused-import", workspace_id=workspace.id, repo="pallets/click", mode="full")
        jobs.mark_paused("paused-import")
        session.commit()
        assert jobs.has_active_for_workspace(workspace.id)
        assert jobs.latest_active_for_workspace(workspace.id).job_id == "paused-import"
    engine.dispose()
