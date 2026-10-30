"""File-backed SQLite tests for safe operator-controlled orphan reconciliation."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import json
from pathlib import Path

from alembic import command
from alembic.config import Config
import pytest
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session

from app.db.models import Artifact, ImportJob, Workspace
from app.jobs.recover_import_jobs import main
from app.repositories.import_jobs import ImportJobRepository, offline_recovery_snapshot


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
            snapshot = offline_recovery_snapshot(repo.get_by_job_id(job_id))
            with pytest.raises(ValueError, match="Stop all import workers"):
                repo.mark_interrupted_offline(
                    job_id, older_than=cutoff, expected_snapshot=snapshot,
                )
            session.rollback()
            job = repo.mark_interrupted_offline(
                job_id, older_than=cutoff, expected_snapshot=snapshot,
                workers_stopped=True,
            )
            session.commit()
            assert job.status == "failed"
            assert job.summary_json["failure_category"] == "worker_interrupted"
            assert job.summary_json["recovery"]["previous_status"] == job_id.removeprefix("stale-")
            assert job.summary_json["recovery"]["automatic_retry"] is False

            with pytest.raises(ValueError, match="Cannot recover job in status: failed"):
                repo.mark_interrupted_offline(
                    job_id, older_than=cutoff, expected_snapshot=snapshot,
                    workers_stopped=True,
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
            recent = offline_recovery_snapshot(repo.get_by_job_id("recent-running"))
            completed = offline_recovery_snapshot(repo.get_by_job_id("completed"))
            with pytest.raises(ValueError, match="newer than the recovery cutoff"):
                repo.mark_interrupted_offline(
                    "recent-running", older_than=cutoff,
                    expected_snapshot=recent, workers_stopped=True,
                )
            with pytest.raises(ValueError, match="Cannot recover job in status: succeeded"):
                repo.mark_interrupted_offline(
                    "completed", older_than=cutoff,
                    expected_snapshot=completed, workers_stopped=True,
                )
            session.rollback()
    finally:
        engine.dispose()


def test_cli_requires_exact_id_and_stopped_worker_assertion(tmp_path, monkeypatch) -> None:
    engine = _database(tmp_path, monkeypatch)
    try:
        with Session(engine) as session:
            snapshot = offline_recovery_snapshot(
                ImportJobRepository(session).get_by_job_id("stale-running")
            )
        for argv in (
            ["--apply"],
            ["--apply", "--job-id", "stale-running"],
            ["--apply", "--job-id", "stale-running", "--workers-stopped"],
            ["--apply", "--job-id", "stale-running", "--workers-stopped", "--snapshot", "wrong"],
        ):
            with pytest.raises(SystemExit) as exc:
                main(argv)
            assert exc.value.code == 2

        assert main([
            "--apply", "--job-id", "stale-running", "--workers-stopped",
            "--snapshot", snapshot, "--minimum-age-minutes", "60",
        ]) == 0
        with Session(engine) as session:
            repo = ImportJobRepository(session)
            assert repo.get_by_job_id("stale-running").status == "failed"
            assert repo.get_by_job_id("stale-paused").status == "paused"
        assert main([
            "--apply", "--job-id", "stale-running", "--workers-stopped",
            "--snapshot", snapshot,
        ]) == 1
    finally:
        engine.dispose()



def test_recovery_snapshot_must_match_the_exact_inspected_job(
    tmp_path, monkeypatch
) -> None:
    """A valid snapshot for a different job must never select this one."""
    engine = _database(tmp_path, monkeypatch)
    try:
        with Session(engine) as session:
            repo = ImportJobRepository(session)
            snapshot = offline_recovery_snapshot(repo.get_by_job_id("stale-paused"))
            with pytest.raises(ValueError, match="snapshot is missing or stale"):
                repo.mark_interrupted_offline(
                    "stale-running",
                    older_than=datetime.now(UTC) - timedelta(hours=1),
                    expected_snapshot=snapshot,
                    workers_stopped=True,
                )
            session.rollback()
        assert main([
            "--job-id", "stale-running", "--snapshot", snapshot,
            "--apply", "--workers-stopped",
        ]) == 1
        with Session(engine) as session:
            assert ImportJobRepository(session).get_by_job_id("stale-running").status == "running"
    finally:
        engine.dispose()


def test_snapshot_rejected_after_same_status_job_restarts(
    tmp_path, monkeypatch
) -> None:
    """Even running -> running with a new started_at must invalidate preview."""
    engine = _database(tmp_path, monkeypatch)
    try:
        with Session(engine) as session:
            repo = ImportJobRepository(session)
            old_job = repo.get_by_job_id("stale-running")
            snapshot = offline_recovery_snapshot(old_job)
            session.rollback()

        with Session(engine) as session:
            changed = ImportJobRepository(session).get_by_job_id("stale-running")
            changed.started_at += timedelta(hours=1)
            session.commit()

        with Session(engine) as session:
            repo = ImportJobRepository(session)
            with pytest.raises(ValueError, match="snapshot is missing or stale"):
                repo.mark_interrupted_offline(
                    "stale-running",
                    older_than=datetime.now(UTC) - timedelta(hours=1),
                    expected_snapshot=snapshot,
                    workers_stopped=True,
                )
            session.rollback()
            assert repo.get_by_job_id("stale-running").status == "running"
    finally:
        engine.dispose()


def test_cli_dry_run_exposes_snapshot_without_writing(
    tmp_path, monkeypatch, capsys,
) -> None:
    engine = _database(tmp_path, monkeypatch)
    try:
        assert main(["--job-id", "stale-running"]) == 0
        report = json.loads(capsys.readouterr().out)
        assert report["mode"] == "dry_run"
        assert len(report["candidates"]) == 1
        assert report["candidates"][0]["job_id"] == "stale-running"
        with Session(engine) as session:
            job = ImportJobRepository(session).get_by_job_id("stale-running")
            assert report["candidates"][0]["snapshot"] == offline_recovery_snapshot(job)
            assert job.status == "running"
    finally:
        engine.dispose()




def test_offline_cas_handles_sqlite_server_default_timestamp_precision(
    tmp_path, monkeypatch,
) -> None:
    """Old SQLite whole-second timestamps must not defeat valid recovery."""
    engine = _database(tmp_path, monkeypatch)
    try:
        with Session(engine) as session:
            repo = ImportJobRepository(session)
            job = repo.get_by_job_id("stale-queued")
            assert job is not None and job.started_at is None
            stale_snapshot = offline_recovery_snapshot(job)
            # SQLite datetime('now') uses the same whole-second serialization
            # as CURRENT_TIMESTAMP server defaults; SQLAlchemy equality binds
            # a Python datetime with .000000, which SQLite does not match.
            session.execute(
                text(
                    "UPDATE import_jobs SET created_at = datetime('now', '-2 days') "
                    "WHERE job_id = :job_id"
                ),
                {"job_id": "stale-queued"},
            )
            session.commit()
            session.refresh(job)
            assert job.created_at.microsecond == 0
            actual_snapshot = offline_recovery_snapshot(job)
            assert actual_snapshot != stale_snapshot
            assert session.scalar(
                select(ImportJob).where(ImportJob.created_at == job.created_at)
            ) is None

        with Session(engine) as session:
            repo = ImportJobRepository(session)
            cutoff = datetime.now(UTC) - timedelta(hours=1)
            with pytest.raises(ValueError, match="snapshot is missing or stale"):
                repo.mark_interrupted_offline(
                    "stale-queued", older_than=cutoff,
                    expected_snapshot=stale_snapshot, workers_stopped=True,
                )
            session.rollback()
            updated = repo.mark_interrupted_offline(
                "stale-queued", older_than=cutoff,
                expected_snapshot=actual_snapshot, workers_stopped=True,
            )
            session.commit()
            assert updated.status == "failed"
            assert session.scalar(select(Artifact)).source_id == "already-committed"
    finally:
        engine.dispose()
