"""Reproducers for issue #36: import worker status races and SQLite writer locks.

The strict xfails are intended safety contracts for work not yet implemented.
They must be removed when the worker lifecycle is fixed, not silently skipped.
All tests use a real file-backed SQLite database and isolated local sessions.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event

from alembic import command
from alembic.config import Config
import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.db.models import Artifact, Workspace
from app.jobs.import_jobs import queue_github_import, run_github_import
from app.repositories.import_jobs import ImportJobRepository


def _prepare_database(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "import-pause-lifecycle.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(config, "head")
    # A short busy timeout exposes contention quickly, instead of waiting for
    # the production SQLite engine's longer 30-second write timeout.
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"timeout": 0.15})
    with Session(engine) as session:
        workspace = Workspace(
            slug="github-pause-race", name="Pause race",
            repo_url="https://github.com/org/repo",
        )
        session.add(workspace)
        session.flush()
        repo = ImportJobRepository(session)
        repo.create(
            job_id="job-pause-race", workspace_id=workspace.id,
            repo="org/repo", mode="full",
        )
        workspace_id = workspace.id
        session.commit()
    return engine, workspace_id


def _status(engine) -> str:
    with Session(engine) as session:
        job = ImportJobRepository(session).get_by_job_id("job-pause-race")
        assert job is not None
        return job.status


def test_paused_queued_job_cannot_be_overwritten_by_late_worker_start(
    tmp_path: Path, monkeypatch
) -> None:
    engine, _ = _prepare_database(tmp_path, monkeypatch)
    try:
        with Session(engine) as session:
            ImportJobRepository(session).mark_paused("job-pause-race")
            session.commit()
        assert _status(engine) == "paused"

        with Session(engine) as session:
            try:
                ImportJobRepository(session).mark_running("job-pause-race")
            except ValueError:
                # A guarded worker start can reject the paused transition.
                session.rollback()
            else:
                session.commit()

        # Safety contract: background-task startup must not undo a pause.
        assert _status(engine) == "paused"
    finally:
        engine.dispose()


def test_completed_job_cannot_be_resurrected_by_duplicate_worker_start(
    tmp_path: Path, monkeypatch
) -> None:
    engine, _ = _prepare_database(tmp_path, monkeypatch)
    try:
        with Session(engine) as session:
            repo = ImportJobRepository(session)
            repo.mark_running("job-pause-race")
            repo.mark_succeeded("job-pause-race", imported_count=0)
            session.commit()
        assert _status(engine) == "succeeded"

        with Session(engine) as session:
            try:
                ImportJobRepository(session).mark_running("job-pause-race")
            except ValueError:
                session.rollback()
            else:
                session.commit()

        # Terminal state must remain terminal across duplicate tasks.
        assert _status(engine) == "succeeded"
    finally:
        engine.dispose()



def test_queued_pause_resume_worker_claims_exactly_once(
    tmp_path: Path, monkeypatch
) -> None:
    """A paused queued job is not started until resume re-queues its claim."""
    engine, _ = _prepare_database(tmp_path, monkeypatch)
    started = Event()
    class StopAfterStartImporter:
        def __init__(self, session, client):
            pass

        def import_repo(self, *, workspace_slug, repo, mode="full",
                        since=None, progress_callback=None):
            started.set()
            raise RuntimeError("synthetic stop after start")

    monkeypatch.setattr(
        "app.jobs.import_jobs.GitHubImporter", StopAfterStartImporter
    )
    monkeypatch.setattr(
        "app.jobs.import_jobs.build_runtime_providers",
        lambda settings: type("Providers", (), {
            "embedder": object(), "extraction_provider": object()
        })(),
    )
    with Session(engine) as session:
        ImportJobRepository(session).mark_paused("job-pause-race")
        session.commit()

    try:
        with ThreadPoolExecutor(max_workers=1) as workers:
            future = workers.submit(
                run_github_import, job_id="job-pause-race",
                workspace_slug="github-pause-race",
                repo="org/repo", mode="full",
            )
            assert not started.wait(timeout=0.3)
            assert _status(engine) == "paused"
            with Session(engine) as session:
                resumed = ImportJobRepository(session).mark_resumed("job-pause-race")
                assert resumed.status == "queued"
                session.commit()
            failed = future.result(timeout=12)
            assert started.is_set()
            assert failed["status"] == "failed"
        with Session(engine) as session:
            job = ImportJobRepository(session).get_by_job_id("job-pause-race")
            assert job is not None and job.started_at is not None
            assert job.status == "failed"
    finally:
        # Ensure a broken assertion does not leave a background task paused
        # indefinitely. The worker can only start after this cleanup.
        with Session(engine) as session:
            job = ImportJobRepository(session).get_by_job_id("job-pause-race")
            if job is not None and job.status == "paused":
                ImportJobRepository(session).mark_resumed("job-pause-race")
                session.commit()
        engine.dispose()


def test_uncommitted_artifact_write_blocks_separate_sqlite_pause_update(
    tmp_path: Path, monkeypatch
) -> None:
    """Demonstrate existing lock contention, not a successful pause contract.

    This is a deterministic two-connection reproduction; add a bounded
    multithreaded API+worker acceptance test before declaring issue #36 fixed.
    """
    engine, workspace_id = _prepare_database(tmp_path, monkeypatch)
    try:
        with Session(engine) as session:
            ImportJobRepository(session).mark_running("job-pause-race")
            session.commit()

        # Simulate a long import callback holding the same writer transaction
        # as its uncommitted Artifact(s).
        with Session(engine) as worker_session:
            worker_session.add(Artifact(
                workspace_id=workspace_id, type="issue", source_id="partial-write",
                repo="org/repo", title="Uncommitted", content="Unverified data",
            ))
            worker_session.flush()
            assert _status(engine) == "running"

            with Session(engine) as admin_session:
                try:
                    ImportJobRepository(admin_session).mark_paused("job-pause-race")
                    admin_session.commit()
                except OperationalError as exc:
                    assert "locked" in str(exc).lower()
                    admin_session.rollback()
                else:
                    pytest.fail(
                        "Expected SQLite lock contention while an Artifact write is uncommitted"
                    )
            # The writer has not committed or rolled back, so no state change
            # should be durable from the failed admin pause.
            worker_session.rollback()

        assert _status(engine) == "running"
        with Session(engine) as session:
            assert session.query(Artifact).count() == 0
    finally:
        engine.dispose()
