from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import case, func, select, update
from sqlalchemy.orm import Session

ACTIVE_IMPORT_STATUSES = ("queued", "running", "paused")

from app.db.models import ImportJob


class ImportJobRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        *,
        job_id: str,
        workspace_id: int,
        repo: str,
        mode: str,
        sync_origin: str = "manual",
        trigger_event: str | None = None,
        trigger_delivery_id: str | None = None,
    ) -> ImportJob:
        job = ImportJob(
            job_id=job_id,
            workspace_id=workspace_id,
            repo=repo,
            mode=mode,
            status="queued",
            sync_origin=sync_origin,
            trigger_event=trigger_event,
            trigger_delivery_id=trigger_delivery_id,
            imported_count=0,
            summary_json={"stage": "queued"},
        )
        self.session.add(job)
        self.session.flush()
        return job

    def get_by_job_id(self, job_id: str) -> ImportJob | None:
        stmt = select(ImportJob).where(ImportJob.job_id == job_id)
        return self.session.scalar(stmt)

    def latest_for_workspace(self, workspace_id: int) -> ImportJob | None:
        stmt = (
            select(ImportJob)
            .where(ImportJob.workspace_id == workspace_id)
            .order_by(ImportJob.created_at.desc(), ImportJob.id.desc())
        )
        return self.session.scalar(stmt)

    def latest_success_for_repo(self, workspace_id: int, repo: str) -> ImportJob | None:
        stmt = (
            select(ImportJob)
            .where(
                ImportJob.workspace_id == workspace_id,
                ImportJob.repo == repo,
                ImportJob.status == "succeeded",
            )
            .order_by(ImportJob.finished_at.desc(), ImportJob.id.desc())
        )
        return self.session.scalar(stmt)

    def list_recent_for_workspace(self, workspace_id: int, *, limit: int = 5) -> list[ImportJob]:
        stmt = (
            select(ImportJob)
            .where(ImportJob.workspace_id == workspace_id)
            .order_by(ImportJob.created_at.desc(), ImportJob.id.desc())
            .limit(limit)
        )
        return list(self.session.scalars(stmt))

    def has_active_for_workspace(self, workspace_id: int) -> bool:
        stmt = select(ImportJob).where(
            ImportJob.workspace_id == workspace_id,
            ImportJob.status.in_(ACTIVE_IMPORT_STATUSES),
        )
        return self.session.scalar(stmt) is not None

    def latest_active_for_workspace(self, workspace_id: int) -> ImportJob | None:
        stmt = (
            select(ImportJob)
            .where(
                ImportJob.workspace_id == workspace_id,
                ImportJob.status.in_(ACTIVE_IMPORT_STATUSES),
            )
            .order_by(ImportJob.created_at.desc(), ImportJob.id.desc())
        )
        return self.session.scalar(stmt)

    def mark_running(self, job_id: str, *, stage: str = "importing_artifacts") -> ImportJob:
        """Atomically claim a queued job without overwriting paused/terminal state."""
        job = self._require(job_id)
        if job.status != "queued":
            raise ValueError(f"Cannot start job in status: {job.status}")
        summary = dict(job.summary_json or {})
        summary["stage"] = stage
        result = self.session.execute(
            update(ImportJob)
            .where(ImportJob.job_id == job_id, ImportJob.status == "queued")
            .values(
                status="running",
                started_at=datetime.now(UTC),
                error_message=None,
                summary_json=summary,
            )
        )
        if result.rowcount != 1:
            self.session.refresh(job)
            raise ValueError(f"Cannot start job in status: {job.status}")
        self.session.refresh(job)
        return job

    def update_stage(self, job_id: str, *, stage: str, summary_json: dict | None = None) -> ImportJob:
        job = self._require(job_id)
        summary = dict(job.summary_json or {})
        summary["stage"] = stage
        if summary_json:
            summary.update(summary_json)
        job.summary_json = summary
        self.session.flush()
        return job

    def merge_summary(self, job_id: str, *, summary_json: dict) -> ImportJob:
        job = self._require(job_id)
        summary = dict(job.summary_json or {})
        summary.update(summary_json)
        job.summary_json = summary
        self.session.flush()
        return job

    def mark_succeeded(self, job_id: str, *, imported_count: int, summary_json: dict | None = None) -> ImportJob:
        """Complete only a still-running job; never overwrite a late pause."""
        job = self._require(job_id)
        if job.status != "running":
            raise ValueError(f"Cannot complete job in status: {job.status}")
        summary = dict(job.summary_json or {})
        if summary_json:
            summary.update(summary_json)
        summary["stage"] = "completed"
        result = self.session.execute(
            update(ImportJob)
            .where(ImportJob.job_id == job_id, ImportJob.status == "running")
            .values(
                status="succeeded", imported_count=imported_count,
                summary_json=summary, finished_at=datetime.now(UTC),
            )
        )
        self.session.refresh(job)
        if result.rowcount != 1:
            raise ValueError(f"Cannot complete job in status: {job.status}")
        return job

    def mark_failed(
        self,
        job_id: str,
        *,
        error_message: str,
        stage: str,
        failure_category: str,
    ) -> ImportJob:
        job = self._require(job_id)
        if job.status not in ACTIVE_IMPORT_STATUSES:
            raise ValueError(f"Cannot fail job in status: {job.status}")
        summary = dict(job.summary_json or {})
        summary["stage"] = stage
        summary["failure_category"] = failure_category
        result = self.session.execute(
            update(ImportJob)
            .where(ImportJob.job_id == job_id, ImportJob.status.in_(ACTIVE_IMPORT_STATUSES))
            .values(
                status="failed", error_message=error_message,
                summary_json=summary, finished_at=datetime.now(UTC),
            )
        )
        self.session.refresh(job)
        if result.rowcount != 1:
            raise ValueError(f"Cannot fail job in status: {job.status}")
        return job


    def mark_paused(self, job_id: str) -> ImportJob:
        job = self._require(job_id)
        if job.status not in ("queued", "running"):
            raise ValueError(f"Cannot pause job in status: {job.status}")
        # The state may have changed in another session after _require().
        # Only update a still-active job, never resurrect a terminal one.
        result = self.session.execute(
            update(ImportJob)
            .where(ImportJob.job_id == job_id, ImportJob.status.in_(("queued", "running")))
            .values(status="paused")
        )
        self.session.refresh(job)
        if result.rowcount != 1:
            raise ValueError(f"Cannot pause job in status: {job.status}")
        return job

    def mark_resumed(self, job_id: str) -> ImportJob:
        job = self._require(job_id)
        if job.status != "paused":
            raise ValueError(f"Cannot resume job in status: {job.status}")
        # The database chooses queued for never-started work; a stale ORM
        # started_at value must not decide the state of a concurrent resume.
        result = self.session.execute(
            update(ImportJob)
            .where(ImportJob.job_id == job_id, ImportJob.status == "paused")
            .values(
                status=case(
                    (ImportJob.started_at.is_(None), "queued"),
                    else_="running",
                )
            )
        )
        self.session.refresh(job)
        if result.rowcount != 1:
            raise ValueError(f"Cannot resume job in status: {job.status}")
        return job

    def list_offline_recovery_candidates(
        self, *, older_than: datetime, limit: int = 20, job_id: str | None = None
    ) -> list[ImportJob]:
        """Inspect old active jobs only; age is NOT proof of worker death."""
        if limit < 1 or limit > 100:
            raise ValueError("Recovery inspection limit must be between 1 and 100")
        cutoff = _database_utc(older_than)
        stmt = select(ImportJob).where(
            ImportJob.status.in_(ACTIVE_IMPORT_STATUSES),
            func.coalesce(ImportJob.started_at, ImportJob.created_at) <= cutoff,
        )
        if job_id is not None:
            stmt = stmt.where(ImportJob.job_id == job_id)
        stmt = stmt.order_by(ImportJob.created_at, ImportJob.id).limit(limit)
        return list(self.session.scalars(stmt))

    def mark_interrupted_offline(
        self, job_id: str, *, older_than: datetime,
        workers_stopped: bool = False, interrupted_at: datetime | None = None,
    ) -> ImportJob:
        """Operator-only repair. Never call automatically on process startup.

        This CAS does not fence a still-running worker; it is safe ONLY once
        all worker processes using this database have been stopped externally.
        """
        if not workers_stopped:
            raise ValueError("Stop all import workers before offline recovery")
        cutoff = _database_utc(older_than)
        now = interrupted_at or datetime.now(UTC)
        job = self._require(job_id)
        if job.status not in ACTIVE_IMPORT_STATUSES:
            raise ValueError(f"Cannot recover job in status: {job.status}")
        age_anchor = _database_utc(job.started_at or job.created_at)
        if age_anchor > cutoff:
            raise ValueError("Import job is newer than the recovery cutoff")

        summary = dict(job.summary_json or {})
        summary["failure_category"] = "worker_interrupted"
        summary["recovery"] = {
            "method": "offline_operator_reconciliation",
            "previous_status": job.status,
            "recorded_at": now.astimezone(UTC).isoformat(),
            "automatic_retry": False,
        }
        # Preserve the previous stage, previously committed source rows and
        # original import metadata; do not auto-replay non-idempotent stages.
        result = self.session.execute(
            update(ImportJob)
            .where(
                ImportJob.job_id == job_id,
                ImportJob.status == job.status,
                func.coalesce(ImportJob.started_at, ImportJob.created_at) <= cutoff,
            )
            .values(
                status="failed",
                error_message=(
                    "Import worker interrupted; no automatic replay. "
                    "Verify stopped workers and start a new import to retry."
                ),
                summary_json=summary,
                finished_at=now,
            )
        )
        self.session.refresh(job)
        if result.rowcount != 1:
            raise ValueError("Job state changed during offline recovery")
        return job

    def _require(self, job_id: str) -> ImportJob:
        job = self.get_by_job_id(job_id)
        if job is None:
            raise ValueError(f"Import job not found: {job_id}")
        return job


def _database_utc(value: datetime) -> datetime:
    """Normalize UTC timestamps for the project's timezone-naive SQL columns."""
    if value.tzinfo is not None:
        return value.astimezone(UTC).replace(tzinfo=None)
    return value
