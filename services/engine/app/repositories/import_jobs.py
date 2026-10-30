from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import case, select, update
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

    def _require(self, job_id: str) -> ImportJob:
        job = self.get_by_job_id(job_id)
        if job is None:
            raise ValueError(f"Import job not found: {job_id}")
        return job
