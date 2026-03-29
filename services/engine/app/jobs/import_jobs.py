from __future__ import annotations

from time import monotonic
from urllib.parse import urlparse
from uuid import uuid4

import httpx

from app.config import get_settings
from app.db.session import get_db_session
from app.extractor.pipeline import CandidateExtractionPipeline, ExtractionRunStats
from app.ingest.github_client import GitHubClient, GitHubNetworkError
from app.ingest.github_importer import GitHubImporter
from app.indexing.index_artifact import index_artifact
from app.llm.base import ProviderConfigurationError, ProviderRateLimitError, ProviderRequestError, ProviderResponseError, ProviderTimeoutError
from app.llm.provider_factory import build_runtime_providers
from app.observability.logging import build_log_context, get_logger
from app.outcomes.real_workspaces import summarize_imported_evidence
from app.repositories.artifacts import ArtifactRepository
from app.repositories.decisions import DecisionRepository
from app.repositories.import_jobs import ImportJobRepository
from app.repositories.source_refs import SourceRefRepository
from app.repositories.workspaces import WorkspaceRepository


def queue_github_import(*, workspace_slug: str | None, repo: str, mode: str = "full") -> dict[str, int | str | None]:
    session = get_db_session()
    job_id = str(uuid4())
    try:
        repo_ref, repo_url = _normalize_repo(repo)
        workspaces = WorkspaceRepository(session)
        workspace = _resolve_workspace(workspaces=workspaces, workspace_slug=workspace_slug, repo_ref=repo_ref, repo_url=repo_url)
        if mode not in {"full", "since_last_sync"}:
            raise ValueError(f"Unsupported import mode: {mode}")

        jobs = ImportJobRepository(session)
        job = jobs.create(job_id=job_id, workspace_id=workspace.id, repo=repo_ref, mode=mode)
        session.commit()
        return serialize_import_job(session=session, job=job)
    finally:
        session.close()


def run_github_import(*, job_id: str, workspace_slug: str, repo: str, mode: str = "full") -> dict[str, int | str | None]:
    settings = get_settings()
    session = get_db_session()
    logger = get_logger()
    current_stage = "queued"
    try:
        workspace = WorkspaceRepository(session).get_by_slug(workspace_slug)
        if workspace is None:
            raise ValueError(f"Workspace not found: {workspace_slug}")

        jobs = ImportJobRepository(session)
        current_stage = "importing_artifacts"
        jobs.mark_running(job_id, stage=current_stage)
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
        import_result = importer.import_repo(
            workspace_slug=workspace_slug,
            repo=repo,
            mode=mode,
            since=since,
        )
        current_stage = "indexing_artifacts"
        jobs.update_stage(
            job_id,
            stage=current_stage,
            summary_json={
                "artifact_counts": import_result.artifact_counts,
                "document_summary": {
                    "selected": import_result.selected_document_count,
                    "imported": import_result.imported_document_count,
                    "skipped": import_result.skipped_document_counts,
                    "categories": import_result.selected_document_categories,
                },
            },
        )
        session.commit()

        artifacts = ArtifactRepository(session).list_by_workspace(workspace.id)
        for artifact in artifacts:
            index_artifact(
                session=session,
                artifact_id=artifact.id,
                content=artifact.content,
                embedder=runtime.embedder,
            )
        current_stage = "extracting_decisions"
        jobs.update_stage(
            job_id,
            stage=current_stage,
            summary_json={
                "extraction_summary": {
                    "shortlisted_artifacts": 0,
                    "screened_artifacts": 0,
                    "screened_in_artifacts": 0,
                    "screened_out_artifacts": 0,
                    "full_extraction_requests": 0,
                    "completed_full_extractions": 0,
                    "total_artifacts": 0,
                    "processed_artifacts": 0,
                    "created_candidates": 0,
                    "salvaged_candidates": 0,
                    "skipped_provider_400": 0,
                    "skipped_provider_timeout": 0,
                    "skipped_invalid_json": 0,
                    "selected_extraction_families": {},
                    "conversion_loss_reasons": {},
                    "elapsed_seconds": 0,
                    "estimated_remaining_seconds": None,
                    "average_full_extraction_latency_ms": None,
                    "current_artifact_title": None,
                    "current_phase": "screening",
                    "current_extraction_family": None,
                }
            },
        )
        session.commit()

        extraction_pipeline = CandidateExtractionPipeline(session, runtime.extraction_provider)
        progress_reporter = _build_extraction_progress_reporter(job_id=job_id)
        created_candidates = extraction_pipeline.run(
            workspace_slug=workspace_slug,
            progress_callback=progress_reporter,
        )
        source_refs = SourceRefRepository(session)
        decisions_repo = DecisionRepository(session)
        workspace_artifacts = ArtifactRepository(session).list_by_workspace(workspace.id)
        workspace_decisions = decisions_repo.list_by_workspace(workspace.id)
        evidence_summary = summarize_imported_evidence(
            workspace_artifacts,
            workspace_decisions,
            {decision.id: source_refs.list_by_decision(decision.id) for decision in workspace_decisions},
        )
        decision_counts = DecisionRepository(session).counts_by_review_state(workspace.id)
        has_decision_signal = created_candidates > 0 or any(
            decision_counts.get(state, 0) > 0 for state in ("candidate", "accepted", "superseded")
        )
        job = jobs.mark_succeeded(
            job_id,
            imported_count=import_result.imported_count,
            summary_json={
                "artifact_counts": import_result.artifact_counts,
                "document_summary": {
                    "selected": import_result.selected_document_count,
                    "imported": import_result.imported_document_count,
                    "skipped": import_result.skipped_document_counts,
                    "categories": import_result.selected_document_categories,
                },
                "extraction_summary": extraction_pipeline.last_run_stats.to_summary(),
                "evidence_summary": evidence_summary,
                "outcome": "ok" if has_decision_signal else "insufficient_evidence",
            },
        )
        session.commit()
        logger.info(
            "github import completed",
            extra=build_log_context(job_id=job_id, workspace_id=workspace.id),
        )
        return serialize_import_job(session=session, job=job)
    except Exception as exc:
        session.rollback()
        jobs = ImportJobRepository(session)
        job = jobs.get_by_job_id(job_id)
        if job is not None:
            failed_job = jobs.mark_failed(
                job_id,
                error_message=str(exc),
                stage=current_stage,
                failure_category=_classify_failure(exc),
            )
            session.commit()
            return serialize_import_job(session=session, job=failed_job)
        raise
    finally:
        session.close()


def get_import_job_status(job_id: str) -> dict[str, int | str | None]:
    session = get_db_session()
    try:
        job = ImportJobRepository(session).get_by_job_id(job_id)
        if job is None:
            raise ValueError(f"Import job not found: {job_id}")
        return serialize_import_job(session=session, job=job)
    finally:
        session.close()


def lookup_github_workspace(*, repo: str) -> dict[str, object | None]:
    session = get_db_session()
    try:
        repo_ref, repo_url = _normalize_repo(repo)
        workspace = WorkspaceRepository(session).get_by_repo_url(repo_url)
        if workspace is None:
            return {
                "repo": repo_ref,
                "repo_url": repo_url,
                "workspace_exists": False,
                "workspace_slug": None,
                "has_successful_import": False,
                "can_incremental_sync": False,
                "has_running_import": False,
                "latest_import": None,
            }

        jobs = ImportJobRepository(session)
        latest_job = jobs.latest_for_workspace(workspace.id)
        latest_success = jobs.latest_success_for_repo(workspace.id, repo_ref)
        latest_import = serialize_import_job(session=session, job=latest_job) if latest_job is not None else None
        has_running_import = latest_job is not None and latest_job.status in {"queued", "running"}
        return {
            "repo": repo_ref,
            "repo_url": repo_url,
            "workspace_exists": True,
            "workspace_slug": workspace.slug,
            "has_successful_import": latest_success is not None,
            "can_incremental_sync": latest_success is not None and not has_running_import,
            "has_running_import": has_running_import,
            "latest_import": latest_import,
        }
    finally:
        session.close()


def serialize_import_job(*, session, job) -> dict[str, int | str | None]:
    workspace = WorkspaceRepository(session).get_by_id(job.workspace_id)
    return {
        "job_id": job.job_id,
        "workspace_slug": workspace.slug if workspace is not None else None,
        "repo": job.repo,
        "mode": job.mode,
        "status": job.status,
        "imported_count": job.imported_count,
        "summary": job.summary_json,
        "error_message": job.error_message,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "finished_at": job.finished_at.isoformat() if job.finished_at else None,
    }


def _normalize_repo(repo: str) -> tuple[str, str]:
    value = repo.strip()
    if value.startswith("http://") or value.startswith("https://"):
        parsed = urlparse(value)
        if parsed.netloc not in {"github.com", "www.github.com"}:
            raise ValueError("Only public GitHub repositories are supported")
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) < 2:
            raise ValueError("Repository URL must include owner and repo")
        owner, name = parts[0], parts[1]
    else:
        parts = [part for part in value.strip("/").split("/") if part]
        if len(parts) != 2:
            raise ValueError("Repository must use owner/repo format")
        owner, name = parts[0], parts[1]

    if name.endswith(".git"):
        name = name[:-4]
    repo_ref = f"{owner}/{name}"
    return repo_ref, f"https://github.com/{repo_ref}"


def _resolve_workspace(*, workspaces: WorkspaceRepository, workspace_slug: str | None, repo_ref: str, repo_url: str):
    if workspace_slug:
        workspace = workspaces.get_by_slug(workspace_slug)
        if workspace is None:
            raise ValueError(f"Workspace not found: {workspace_slug}")
        if workspace.repo_url and workspace.repo_url != repo_url:
            raise ValueError(
                f"Workspace {workspace_slug} is already linked to {workspace.repo_url} and cannot import {repo_ref}"
            )
        return workspace

    existing = workspaces.get_by_repo_url(repo_url)
    if existing is not None:
        return existing

    slug = _workspace_slug(repo_ref)
    existing_by_slug = workspaces.get_by_slug(slug)
    if existing_by_slug is not None:
        return existing_by_slug
    return workspaces.create(slug=slug, name=repo_ref, repo_url=repo_url)


def _workspace_slug(repo_ref: str) -> str:
    normalized = "".join(char.lower() if char.isalnum() else "-" for char in repo_ref)
    while "--" in normalized:
        normalized = normalized.replace("--", "-")
    return f"github-{normalized}".strip("-")[:120]


def _classify_failure(exc: Exception) -> str:
    if isinstance(exc, GitHubNetworkError):
        return "network_failure"
    if isinstance(exc, httpx.HTTPStatusError):
        status_code = exc.response.status_code
        if 400 <= status_code < 500:
            return "repository_access_failure"
    if isinstance(exc, (ProviderConfigurationError, ProviderTimeoutError, ProviderRateLimitError, ProviderRequestError, ProviderResponseError)):
        return "provider_failure"
    if "Workspace not found" in str(exc):
        return "workspace_not_found"
    if "owner/repo" in str(exc) or "public GitHub" in str(exc) or "Repository URL" in str(exc):
        return "invalid_repository"
    return "analysis_execution_failed"


def _build_extraction_progress_reporter(*, job_id: str):
    last_reported_processed = -1
    last_reported_at = 0.0

    def report(stats: ExtractionRunStats) -> None:
        nonlocal last_reported_processed, last_reported_at
        now = monotonic()
        should_report = (
            stats.processed_artifacts == 0
            or stats.processed_artifacts >= stats.total_artifacts
            or stats.processed_artifacts - last_reported_processed >= 5
            or now - last_reported_at >= 3.0
        )
        if not should_report:
            return

        progress_session = get_db_session()
        try:
            ImportJobRepository(progress_session).merge_summary(
                job_id,
                summary_json={
                    "extraction_summary": stats.to_summary(),
                },
            )
            progress_session.commit()
            last_reported_processed = stats.processed_artifacts
            last_reported_at = now
        finally:
            progress_session.close()

    return report
