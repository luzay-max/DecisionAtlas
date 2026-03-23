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

    def mark_running(self, job_id: str, *, stage: str = "importing_artifacts") -> ImportJob:
        job = self._require(job_id)
        job.status = "running"
        job.started_at = datetime.utcnow()
        job.error_message = None
        summary = dict(job.summary_json or {})
        summary["stage"] = stage
        job.summary_json = summary
        self.session.flush()
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
        job = self._require(job_id)
        job.status = "succeeded"
        job.imported_count = imported_count
        summary = dict(job.summary_json or {})
        if summary_json:
            summary.update(summary_json)
        summary["stage"] = "completed"
        job.summary_json = summary
        job.finished_at = datetime.utcnow()
        self.session.flush()
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
        job.status = "failed"
        job.error_message = error_message
        summary = dict(job.summary_json or {})
        summary["stage"] = stage
        summary["failure_category"] = failure_category
        job.summary_json = summary
        job.finished_at = datetime.utcnow()
        self.session.flush()
        return job

    def _require(self, job_id: str) -> ImportJob:
        job = self.get_by_job_id(job_id)
        if job is None:
            raise ValueError(f"Import job not found: {job_id}")
        return job
