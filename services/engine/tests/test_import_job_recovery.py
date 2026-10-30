"""File-backed SQLite tests for safe operator-controlled orphan reconciliation."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

from alembic import command
from alembic.config import Config
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.models import Artifact, Workspace
from app.jobs.recover_import_jobs import main
from app.repositories.import_jobs import ImportJobRepository


def _database(tmp_path: Path, monkeypatch):
    path = tmp_path / "recovery.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{path}")
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{path}")
    command.upgrade(config, "head")
    engine = create_engine(f"sqlite:///{path}")
    with Session(engine) as session:
        workspace = Workspace(
            slug="orphan-recovery", name="Orphan recovery",
            repo_url="https://github.com/org/repo",
        )
        session.add(workspace)
        session.flush()
        jobs = ImportJobRepository(session)
        old = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=2)
        for job_id, status in (
            ("stale-running", "running"),
            ("stale-paused", "paused"),
            ("stale-queued", "queued"),
            ("recent-running", "running"),
            ("completed", "succeeded"),
        ):
            job = jobs.create(
                job_id=job_id, workspace_id=workspace.id,
                repo="org/repo", mode="full",
            )
            if status != "queued":
                jobs.mark_running(job_id)
            if status == "paused":
                jobs.mark_paused(job_id)
            if status == "succeeded":
                jobs.mark_succeeded(job_id, imported_count=1)
            if job_id.startswith("stale"):
                job.created_at = old
                if status != "queued":
                    job.started_at = old
        session.add(Artifact(
            workspace_id=workspace.id, type="issue", source_id="already-committed",
            repo="org/repo", title="Source", content="Preserve me",
        ))
        session.commit()
    return engine


def test_offline_recovery_inspection_is_read_only(tmp_path, monkeypatch) -> None:
    engine = _database(tmp_path, monkeypatch)
    try:
        with Session(engine) as session:
            jobs = ImportJobRepository(session)
            candidates = jobs.list_offline_recovery_candidates(
                older_than=datetime.now(UTC) - timedelta(hours=1),
            )
            assert {item.job_id for item in candidates} == {
                "stale-running", "stale-paused", "stale-queued",
            }
        assert main(["--minimum-age-minutes", "60"]) == 0
        with Session(engine) as session:
            jobs = ImportJobRepository(session)
            assert jobs.get_by_job_id("stale-running").status == "running"
            assert jobs.get_by_job_id("stale-paused").status == "paused"
    finally:
        engine.dispose()


@pytest.mark.parametrize("job_id", ["stale-running", "stale-paused", "stale-queued"])
def test_explicit_offline_reconciliation_marks_one_old_active_job_failed(
    tmp_path, monkeypatch, job_id
) -> None:
    engine = _database(tmp_path, monkeypatch)
    try:
        with Session(engine) as session:
            repo = ImportJobRepository(session)
            cutoff = datetime.now(UTC) - timedelta(hours=1)
            with pytest.raises(ValueError, match="Stop all import workers"):
                repo.mark_interrupted_offline(job_id, older_than=cutoff)
            session.rollback()
            job = repo.mark_interrupted_offline(
                job_id, older_than=cutoff, workers_stopped=True,
            )
            session.commit()
            assert job.status == "failed"
            assert job.summary_json["failure_category"] == "worker_interrupted"
            assert job.summary_json["recovery"]["previous_status"] == job_id.removeprefix("stale-")
            assert job.summary_json["recovery"]["automatic_retry"] is False

            with pytest.raises(ValueError, match="Cannot recover job in status: failed"):
                repo.mark_interrupted_offline(
                    job_id, older_than=cutoff, workers_stopped=True,
                )
            session.rollback()
        with Session(engine) as session:
            assert session.scalar(select(Artifact)).source_id == "already-committed"
            assert ImportJobRepository(session).get_by_job_id("recent-running").status == "running"
            assert ImportJobRepository(session).get_by_job_id("completed").status == "succeeded"
    finally:
        engine.dispose()


def test_recovery_does_not_mark_recent_or_terminal_job(tmp_path, monkeypatch) -> None:
    engine = _database(tmp_path, monkeypatch)
    try:
        with Session(engine) as session:
            repo = ImportJobRepository(session)
            cutoff = datetime.now(UTC) - timedelta(hours=1)
            with pytest.raises(ValueError, match="newer than the recovery cutoff"):
                repo.mark_interrupted_offline(
                    "recent-running", older_than=cutoff, workers_stopped=True,
                )
            with pytest.raises(ValueError, match="Cannot recover job in status: succeeded"):
                repo.mark_interrupted_offline(
                    "completed", older_than=cutoff, workers_stopped=True,
                )
            session.rollback()
    finally:
        engine.dispose()


def test_cli_requires_exact_id_and_stopped_worker_assertion(tmp_path, monkeypatch) -> None:
    engine = _database(tmp_path, monkeypatch)
    try:
        for argv in (["--apply"], ["--apply", "--job-id", "stale-running"]):
            with pytest.raises(SystemExit) as exc:
                main(argv)
            assert exc.value.code == 2

        assert main([
            "--apply", "--job-id", "stale-running", "--workers-stopped",
            "--minimum-age-minutes", "60",
        ]) == 0
        with Session(engine) as session:
            repo = ImportJobRepository(session)
            assert repo.get_by_job_id("stale-running").status == "failed"
            assert repo.get_by_job_id("stale-paused").status == "paused"
        assert main([
            "--apply", "--job-id", "stale-running", "--workers-stopped",
        ]) == 1
    finally:
        engine.dispose()
