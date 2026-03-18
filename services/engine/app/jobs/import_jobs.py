from __future__ import annotations

from uuid import uuid4

from app.config import get_settings
from app.db.session import get_db_session
from app.extractor.pipeline import CandidateExtractionPipeline
from app.ingest.github_client import GitHubClient
from app.ingest.github_importer import GitHubImporter
from app.indexing.index_artifact import index_artifact
from app.llm.provider_factory import build_runtime_providers
from app.observability.logging import build_log_context, get_logger
from app.repositories.artifacts import ArtifactRepository
from app.repositories.import_jobs import ImportJobRepository
from app.repositories.workspaces import WorkspaceRepository


def queue_github_import(*, workspace_slug: str, repo: str, mode: str = "full") -> dict[str, int | str | None]:
    settings = get_settings()
    session = get_db_session()
    job_id = str(uuid4())
    try:
        workspace = WorkspaceRepository(session).get_by_slug(workspace_slug)
        if workspace is None:
            raise ValueError(f"Workspace not found: {workspace_slug}")
        if mode not in {"full", "since_last_sync"}:
            raise ValueError(f"Unsupported import mode: {mode}")

        jobs = ImportJobRepository(session)
        job = jobs.create(job_id=job_id, workspace_id=workspace.id, repo=repo, mode=mode)
        session.commit()
        return serialize_import_job(job)
    finally:
        session.close()


def run_github_import(*, job_id: str, workspace_slug: str, repo: str, mode: str = "full") -> dict[str, int | str | None]:
    settings = get_settings()
    session = get_db_session()
    logger = get_logger()
    try:
        workspace = WorkspaceRepository(session).get_by_slug(workspace_slug)
        if workspace is None:
            raise ValueError(f"Workspace not found: {workspace_slug}")

        jobs = ImportJobRepository(session)
        jobs.mark_running(job_id)
        session.commit()

        since = None
        if mode == "since_last_sync":
            last_success = jobs.latest_success_for_repo(workspace.id, repo)
            if last_success is not None and last_success.job_id != job_id:
                since = last_success.finished_at or last_success.started_at or last_success.created_at

        importer = GitHubImporter(
            session,
            GitHubClient(
                token=getattr(settings, "github_token", None),
                max_pages=settings.github_import_max_pages,
            ),
        )
        runtime = build_runtime_providers(settings)
        logger.info(
            "github import started",
            extra=build_log_context(job_id=job_id, workspace_id=workspace.id),
        )
        imported_count = importer.import_repo(
            workspace_slug=workspace_slug,
            repo=repo,
            mode=mode,
            since=since,
        )
        artifacts = ArtifactRepository(session).list_by_workspace(workspace.id)
        for artifact in artifacts:
            index_artifact(
                session=session,
                artifact_id=artifact.id,
                content=artifact.content,
                embedder=runtime.embedder,
            )
        CandidateExtractionPipeline(session, runtime.extraction_provider).run(workspace_slug=workspace_slug)
        job = jobs.mark_succeeded(job_id, imported_count=imported_count)
        session.commit()
        logger.info(
            "github import completed",
            extra=build_log_context(job_id=job_id, workspace_id=workspace.id),
        )
        return serialize_import_job(job)
    except Exception as exc:
        jobs = ImportJobRepository(session)
        job = jobs.get_by_job_id(job_id)
        if job is not None:
            failed_job = jobs.mark_failed(job_id, error_message=str(exc))
            session.commit()
            return serialize_import_job(failed_job)
        raise
    finally:
        session.close()


def get_import_job_status(job_id: str) -> dict[str, int | str | None]:
    session = get_db_session()
    try:
        job = ImportJobRepository(session).get_by_job_id(job_id)
        if job is None:
            raise ValueError(f"Import job not found: {job_id}")
        return serialize_import_job(job)
    finally:
        session.close()


def serialize_import_job(job) -> dict[str, int | str | None]:
    return {
        "job_id": job.job_id,
        "repo": job.repo,
        "mode": job.mode,
        "status": job.status,
        "imported_count": job.imported_count,
        "error_message": job.error_message,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "finished_at": job.finished_at.isoformat() if job.finished_at else None,
    }
