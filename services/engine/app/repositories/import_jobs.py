from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

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
    ) -> ImportJob:
        job = ImportJob(
            job_id=job_id,
            workspace_id=workspace_id,
            repo=repo,
            mode=mode,
            status="queued",
            imported_count=0,
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

    def mark_running(self, job_id: str) -> ImportJob:
        job = self._require(job_id)
        job.status = "running"
        job.started_at = datetime.utcnow()
        job.error_message = None
        self.session.flush()
        return job

    def mark_succeeded(self, job_id: str, *, imported_count: int) -> ImportJob:
        job = self._require(job_id)
        job.status = "succeeded"
        job.imported_count = imported_count
        job.finished_at = datetime.utcnow()
        self.session.flush()
        return job

    def mark_failed(self, job_id: str, *, error_message: str) -> ImportJob:
        job = self._require(job_id)
        job.status = "failed"
        job.error_message = error_message
        job.finished_at = datetime.utcnow()
        self.session.flush()
        return job

    def _require(self, job_id: str) -> ImportJob:
        job = self.get_by_job_id(job_id)
        if job is None:
            raise ValueError(f"Import job not found: {job_id}")
        return job
