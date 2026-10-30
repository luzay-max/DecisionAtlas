"""Regression contracts for issue #36: import lifecycle and SQLite writer locks.

Worker start, pause and resume transitions now use state-conditional updates.
The separate SQLite writer-lock contention is still intentionally reproduced.
All tests use a real file-backed SQLite database and isolated local sessions.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace
from threading import Event

from alembic import command
from alembic.config import Config
import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.db.models import Artifact, Workspace
from app.ingest.github_types import GitHubArtifactPayload, GitHubImportResult
from app.jobs.import_jobs import _wait_for_import_safe_checkpoint, run_github_import
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



def test_stale_pause_session_does_not_overwrite_committed_terminal_state(
    tmp_path: Path, monkeypatch
) -> None:
    """An admin with cached running state must not clobber a completed job."""
    engine, _ = _prepare_database(tmp_path, monkeypatch)
    try:
        with Session(engine) as session:
            ImportJobRepository(session).mark_running("job-pause-race")
            session.commit()

        with Session(engine) as stale_admin:
            repo = ImportJobRepository(stale_admin)
            cached = repo.get_by_job_id("job-pause-race")
            assert cached is not None and cached.status == "running"

            with Session(engine) as worker:
                ImportJobRepository(worker).mark_succeeded(
                    "job-pause-race", imported_count=3
                )
                worker.commit()

            with pytest.raises(ValueError, match="Cannot pause job in status: succeeded"):
                repo.mark_paused("job-pause-race")
            stale_admin.rollback()

        assert _status(engine) == "succeeded"
    finally:
        engine.dispose()


def test_stale_resume_session_does_not_resurrect_failed_job(
    tmp_path: Path, monkeypatch
) -> None:
    """A late resume must not turn a newly failed job back into running."""
    engine, _ = _prepare_database(tmp_path, monkeypatch)
    try:
        with Session(engine) as session:
            repo = ImportJobRepository(session)
            repo.mark_running("job-pause-race")
            repo.mark_paused("job-pause-race")
            session.commit()

        with Session(engine) as stale_admin:
            repo = ImportJobRepository(stale_admin)
            cached = repo.get_by_job_id("job-pause-race")
            assert cached is not None and cached.status == "paused"

            with Session(engine) as worker:
                ImportJobRepository(worker).mark_failed(
                    "job-pause-race",
                    error_message="Synthetic terminal worker failure",
                    stage="indexing_artifacts",
                    failure_category="analysis_execution_failed",
                )
                worker.commit()

            with pytest.raises(ValueError, match="Cannot resume job in status: failed"):
                repo.mark_resumed("job-pause-race")
            stale_admin.rollback()

        assert _status(engine) == "failed"
    finally:
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



def test_paused_during_github_fetch_waits_before_first_artifact_write(
    tmp_path: Path, monkeypatch
) -> None:
    """Actual importer must not hold SQLite's write lock while paused pre-write."""
    engine, _ = _prepare_database(tmp_path, monkeypatch)
    downloading = Event()
    release_download = Event()
    checkpoint_reached = Event()
    real_checkpoint = _wait_for_import_safe_checkpoint

    def observed_checkpoint(*, session, job_id):
        checkpoint_reached.set()
        return real_checkpoint(session=session, job_id=job_id)

    monkeypatch.setattr(
        "app.jobs.import_jobs._wait_for_import_safe_checkpoint",
        observed_checkpoint,
    )

    class ControlledClient:
        def __init__(self, *args, **kwargs):
            pass

        def fetch_issues(self, repo: str, *, since=None):
            downloading.set()
            if not release_download.wait(timeout=12):
                raise TimeoutError("Controlled GitHub fetch was not released")
            return [GitHubArtifactPayload(
                artifact_type="issue", source_id="test-issue", repo=repo,
                title="Evidence", content="Verified issue body", author="tester",
                url=None, timestamp=None, metadata_json={},
            )]

        def fetch_pull_requests(self, repo: str, *, since=None):
            return []

        def fetch_commits(self, repo: str, *, since=None):
            return []

        def get_default_branch(self, repo: str):
            return "main"

        def list_repository_files(self, repo: str, *, ref=None):
            return []

    monkeypatch.setattr("app.jobs.import_jobs.GitHubClient", ControlledClient)
    monkeypatch.setattr(
        "app.jobs.import_jobs.build_runtime_providers",
        lambda settings: type("Providers", (), {
            "embedder": object(), "extraction_provider": object(),
        })(),
    )

    def stop_after_source_commit(**kwargs):
        raise RuntimeError("Synthetic stop after the verified import commit")

    monkeypatch.setattr("app.jobs.import_jobs.index_artifact", stop_after_source_commit)

    try:
        with ThreadPoolExecutor(max_workers=1) as workers:
            future = workers.submit(
                run_github_import, job_id="job-pause-race",
                workspace_slug="github-pause-race", repo="org/repo", mode="full",
            )
            try:
                assert downloading.wait(timeout=5)
                with Session(engine) as admin:
                    ImportJobRepository(admin).mark_paused("job-pause-race")
                    admin.commit()
                release_download.set()
                assert checkpoint_reached.wait(timeout=5), (
                    "Worker did not reach the pre-write pause checkpoint"
                )
                # The worker reached the checkpoint BEFORE an Artifact INSERT.
                assert _status(engine) == "paused"
                with Session(engine) as inspector:
                    assert inspector.query(Artifact).count() == 0
                with Session(engine) as admin:
                    resumed = ImportJobRepository(admin).mark_resumed("job-pause-race")
                    assert resumed.status == "running"
                    admin.commit()
            finally:
                release_download.set()
                # Never leave a test background worker waiting after a failure.
                with Session(engine) as admin:
                    current = ImportJobRepository(admin).get_by_job_id("job-pause-race")
                    if current and current.status == "paused":
                        ImportJobRepository(admin).mark_resumed("job-pause-race")
                        admin.commit()
            outcome = future.result(timeout=12)
            assert outcome["status"] == "failed"
            assert outcome["summary"]["stage"] == "indexing_artifacts"

        with Session(engine) as inspector:
            artifacts = inspector.query(Artifact).all()
            assert len(artifacts) == 1
            assert artifacts[0].source_id == "test-issue"
    finally:
        engine.dispose()


def test_safe_checkpoint_releases_its_read_transaction_before_resume(
    tmp_path: Path, monkeypatch
) -> None:
    """A paused checkpoint polls without pinning a transaction or SQLite writer."""
    engine, _ = _prepare_database(tmp_path, monkeypatch)
    entered = Event()
    polling_while_paused = Event()
    exit_checkpoint = Event()
    import time as clock

    real_sleep = clock.sleep

    def observed_sleep(duration):
        polling_while_paused.set()
        return real_sleep(duration)

    monkeypatch.setattr("app.jobs.import_jobs.time.sleep", observed_sleep)

    with Session(engine) as admin:
        repo = ImportJobRepository(admin)
        repo.mark_running("job-pause-race")
        repo.mark_paused("job-pause-race")
        admin.commit()

    def wait_for_checkpoint():
        with Session(engine) as worker:
            entered.set()
            _wait_for_import_safe_checkpoint(
                session=worker, job_id="job-pause-race",
            )
            exit_checkpoint.set()

    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(wait_for_checkpoint)
            try:
                assert entered.wait(timeout=5)
                assert polling_while_paused.wait(timeout=5), (
                    "Worker never observed the paused status"
                )
                with Session(engine) as admin:
                    # SQLite busy timeout is 150ms: this independent control
                    # write cannot succeed if the worker holds a writer lock.
                    resumed = ImportJobRepository(admin).mark_resumed("job-pause-race")
                    assert resumed.status == "running"
                    admin.commit()
                future.result(timeout=5)
                assert exit_checkpoint.is_set()
            finally:
                with Session(engine) as admin:
                    current = ImportJobRepository(admin).get_by_job_id("job-pause-race")
                    if current and current.status == "paused":
                        ImportJobRepository(admin).mark_resumed("job-pause-race")
                        admin.commit()
    finally:
        engine.dispose()



def test_stale_completion_cannot_override_pause_or_existing_terminal_state(
    tmp_path: Path, monkeypatch
) -> None:
    """A worker holding a stale ORM 'running' job cannot erase an admin pause."""
    engine, _ = _prepare_database(tmp_path, monkeypatch)
    try:
        with Session(engine) as worker:
            repo = ImportJobRepository(worker)
            repo.mark_running("job-pause-race")
            worker.commit()
            cached = repo.get_by_job_id("job-pause-race")
            assert cached is not None and cached.status == "running"

            with Session(engine) as admin:
                ImportJobRepository(admin).mark_paused("job-pause-race")
                admin.commit()

            with pytest.raises(ValueError, match="Cannot complete job in status: paused"):
                repo.mark_succeeded("job-pause-race", imported_count=7)
            worker.rollback()

        assert _status(engine) == "paused"
        with Session(engine) as admin:
            ImportJobRepository(admin).mark_resumed("job-pause-race")
            admin.commit()
        with Session(engine) as worker:
            ImportJobRepository(worker).mark_succeeded("job-pause-race", imported_count=7)
            worker.commit()
        assert _status(engine) == "succeeded"

        with Session(engine) as duplicate:
            with pytest.raises(ValueError, match="Cannot complete job in status: succeeded"):
                ImportJobRepository(duplicate).mark_succeeded(
                    "job-pause-race", imported_count=8
                )
            duplicate.rollback()
        assert _status(engine) == "succeeded"
    finally:
        engine.dispose()


def test_stale_failure_cannot_replace_success_or_duplicate_terminal_state(
    tmp_path: Path, monkeypatch
) -> None:
    engine, _ = _prepare_database(tmp_path, monkeypatch)
    try:
        with Session(engine) as stale_worker:
            repo = ImportJobRepository(stale_worker)
            repo.mark_running("job-pause-race")
            stale_worker.commit()
            cached = repo.get_by_job_id("job-pause-race")
            assert cached is not None

            with Session(engine) as winner:
                ImportJobRepository(winner).mark_succeeded(
                    "job-pause-race", imported_count=2,
                )
                winner.commit()

            with pytest.raises(ValueError, match="Cannot fail job in status: succeeded"):
                repo.mark_failed(
                    "job-pause-race", error_message="late worker exception",
                    stage="extracting_decisions", failure_category="analysis_execution_failed",
                )
            stale_worker.rollback()
        assert _status(engine) == "succeeded"
    finally:
        engine.dispose()


def test_worker_paused_at_final_checkpoint_cannot_mark_success_until_resume(
    tmp_path: Path, monkeypatch
) -> None:
    """A real run pauses during extraction completion and stays paused at finalization."""
    engine, _ = _prepare_database(tmp_path, monkeypatch)
    reached_final_checkpoint = Event()
    real_checkpoint = _wait_for_import_safe_checkpoint
    checkpoint_count = 0

    def observed_checkpoint(*, session, job_id):
        nonlocal checkpoint_count
        checkpoint_count += 1
        if checkpoint_count == 4:
            reached_final_checkpoint.set()
        return real_checkpoint(session=session, job_id=job_id)

    class EmptyImporter:
        def __init__(self, session, client):
            self.session = session

        def import_repo(self, *, workspace_slug, repo, mode="full",
                        since=None, progress_callback=None):
            assert progress_callback is not None
            progress_callback(0)
            return GitHubImportResult(
                imported_count=0,
                artifact_counts={"issue": 0, "pr": 0, "commit": 0, "doc": 0},
                selected_document_count=0, imported_document_count=0,
                skipped_document_counts={}, selected_document_categories={},
            )

    class PausingExtractionPipeline:
        def __init__(self, session, provider):
            self.last_run_stats = SimpleNamespace(to_summary=lambda: {})

        def run(self, *, workspace_slug, progress_callback=None):
            with Session(engine) as admin:
                ImportJobRepository(admin).mark_paused("job-pause-race")
                admin.commit()
            return 0

    monkeypatch.setattr("app.jobs.import_jobs.GitHubImporter", EmptyImporter)
    monkeypatch.setattr(
        "app.jobs.import_jobs.CandidateExtractionPipeline", PausingExtractionPipeline
    )
    monkeypatch.setattr(
        "app.jobs.import_jobs._wait_for_import_safe_checkpoint", observed_checkpoint,
    )
    monkeypatch.setattr(
        "app.jobs.import_jobs.build_runtime_providers",
        lambda settings: SimpleNamespace(embedder=object(), extraction_provider=object()),
    )
    try:
        with ThreadPoolExecutor(max_workers=1) as worker:
            future = worker.submit(
                run_github_import, job_id="job-pause-race",
                workspace_slug="github-pause-race",
                repo="org/repo", mode="full",
            )
            try:
                assert reached_final_checkpoint.wait(timeout=8)
                assert _status(engine) == "paused"
                assert not future.done(), "Worker must not complete before admin resume"
                with Session(engine) as admin:
                    job = ImportJobRepository(admin).mark_resumed("job-pause-race")
                    assert job.status == "running"
                    admin.commit()
            finally:
                with Session(engine) as admin:
                    current = ImportJobRepository(admin).get_by_job_id("job-pause-race")
                    if current is not None and current.status == "paused":
                        ImportJobRepository(admin).mark_resumed("job-pause-race")
                        admin.commit()
            result = future.result(timeout=12)
            assert result["status"] == "succeeded"
        assert _status(engine) == "succeeded"
    finally:
        engine.dispose()
