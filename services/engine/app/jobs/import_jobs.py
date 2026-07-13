from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone
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
from app.repository_access import (
    access_source_label as build_access_source_label,
    access_source_mode,
    access_source_provider,
    access_source_summary,
)
from app.repositories.artifacts import ArtifactRepository
from app.repositories.decisions import DecisionRepository
from app.repositories.github_installations import GitHubAppInstallationRepository
from app.repositories.github_token_access_sources import GitHubTokenAccessSourceRepository
from app.repositories.import_jobs import ImportJobRepository
from app.repositories.source_refs import SourceRefRepository
from app.repositories.workspaces import WorkspaceRepository


DEFAULT_OWNER_SCOPE = "local-default"
QUALIFYING_WEBHOOK_EVENTS = {"push", "pull_request", "issues"}
PRIVATE_ACCESS_AUTH_DETAIL = "GitHub token is unauthorized, expired, revoked, or lacks access to this repository."
PRIVATE_ACCESS_NOT_FOUND_DETAIL = "Repository was not found for the selected private access source."
PRIVATE_ACCESS_NETWORK_DETAIL = "GitHub provider or network failure while validating private repository access."


class RepositoryAccessError(ValueError):
    def __init__(self, message: str, *, failure_category: str) -> None:
        super().__init__(message)
        self.failure_category = failure_category


class ActiveImportConflict(ValueError):
    def __init__(self, *, active_job: dict[str, object | None]) -> None:
        super().__init__("An import is already queued or running for this workspace.")
        self.active_job = active_job


def queue_github_import(
    *,
    workspace_slug: str | None,
    repo: str,
    mode: str = "full",
    owner_scope: str | None = None,
    access_source_type: str | None = None,
    access_source_ref: str | None = None,
    sync_origin: str | None = None,
    trigger_event: str | None = None,
    trigger_delivery_id: str | None = None,
) -> dict[str, int | str | None]:
    session = get_db_session()
    job_id = str(uuid4())
    try:
        repo_ref, repo_url = _normalize_repo(repo)
        effective_owner_scope = _owner_scope(owner_scope)
        resolved_access_source_type, resolved_access_source_ref = _default_access_source_for_repo(
            session=session,
            owner_scope=effective_owner_scope,
            repo_ref=repo_ref,
            access_source_type=access_source_type,
            access_source_ref=access_source_ref,
        )
        preflight_validated = False
        if resolved_access_source_type == "github_token":
            try:
                _preflight_repository_access(
                    session=session,
                    repo_ref=repo_ref,
                    owner_scope=effective_owner_scope,
                    access_source_type=resolved_access_source_type,
                    access_source_ref=resolved_access_source_ref,
                )
                preflight_validated = True
            except RepositoryAccessError:
                session.commit()
                raise
        workspaces = WorkspaceRepository(session)
        workspace = _resolve_workspace(
            workspaces=workspaces,
            workspace_slug=workspace_slug,
            owner_scope=effective_owner_scope,
            repo_ref=repo_ref,
            repo_url=repo_url,
            access_source_type=resolved_access_source_type,
            access_source_ref=resolved_access_source_ref,
        )
        if not preflight_validated:
            _preflight_repository_access(
                session=session,
                repo_ref=repo_ref,
                owner_scope=workspace.owner_scope,
                access_source_type=workspace.access_source_type,
                access_source_ref=workspace.access_source_ref,
            )
        if mode not in {"full", "since_last_sync"}:
            raise ValueError(f"Unsupported import mode: {mode}")

        jobs = ImportJobRepository(session)
        active_job = jobs.latest_active_for_workspace(workspace.id)
        if active_job is not None:
            raise ActiveImportConflict(active_job=serialize_import_job(session=session, job=active_job))
        job = jobs.create(
            job_id=job_id,
            workspace_id=workspace.id,
            repo=repo_ref,
            mode=mode,
            sync_origin=sync_origin or _default_sync_origin(mode=mode, access_source_type=workspace.access_source_type),
            trigger_event=trigger_event,
            trigger_delivery_id=trigger_delivery_id,
        )
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
            _github_client_for_workspace(
                session=session,
                workspace=workspace,
                settings=settings,
                repo=repo,
            ),
        )
        runtime = build_runtime_providers(settings)
        logger.info(
            "github import started",
            extra=build_log_context(job_id=job_id, workspace_id=workspace.id),
        )
        
        last_progress_time = monotonic()
        def on_progress(count: int):
            nonlocal last_progress_time
            now = monotonic()
            
            # Check pause status
            latest_job = jobs.get_by_job_id(job_id)
            if latest_job and latest_job.status == "paused":
                while True:
                    session.refresh(latest_job)
                    if latest_job.status != "paused":
                        break
                    import time
                    time.sleep(2.0)
            if latest_job and latest_job.status == "cancelled":
                raise Exception("Import cancelled")

            # Update DB at most once per second to avoid flooding
            if now - last_progress_time > 1.0:
                jobs.update_stage(job_id, stage=current_stage, summary_json={"imported_count": count})
                session.commit()
                last_progress_time = monotonic()

        import_result = importer.import_repo(
            workspace_slug=workspace_slug,
            repo=repo,
            mode=mode,
            since=since,
            progress_callback=on_progress,
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
                    "recovery_extraction_attempts": 0,
                    "total_artifacts": 0,
                    "processed_artifacts": 0,
                    "created_candidates": 0,
                    "salvaged_candidates": 0,
                    "recovered_candidates": 0,
                    "thin_source_ref_decisions": 0,
                    "skipped_provider_400": 0,
                    "skipped_provider_timeout": 0,
                    "skipped_invalid_json": 0,
                    "selected_extraction_families": {},
                    "conversion_loss_reasons": {},
                    "sparse_recovery_status": "not_evaluated",
                    "sparse_recovery_skip_reason": None,
                    "sparse_recovery_eligible_artifacts": 0,
                    "sparse_recovery_attempted_artifacts": 0,
                    "sparse_recovery_model_attempts": 0,
                    "sparse_recovery_recovered_candidates": 0,
                    "sparse_recovery_evidence_families": {},
                    "sparse_recovery_rejection_reasons": {},
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


def lookup_github_workspace(*, repo: str, owner_scope: str | None = None) -> dict[str, object | None]:
    session = get_db_session()
    try:
        repo_ref, repo_url = _normalize_repo(repo)
        effective_owner_scope = _owner_scope(owner_scope)
        workspace = WorkspaceRepository(session).get_by_repo_identity(owner_scope=effective_owner_scope, repo_identity=repo_ref)
        if workspace is None:
            token_source = GitHubTokenAccessSourceRepository(session).get_by_owner_scope_and_repo_identity(
                owner_scope=effective_owner_scope,
                repo_identity=repo_ref,
            )
            if token_source is not None:
                return {
                    "owner_scope": effective_owner_scope,
                    "repo": repo_ref,
                    "repo_url": repo_url,
                    "workspace_exists": False,
                    "workspace_slug": None,
                    "has_successful_import": False,
                    "can_incremental_sync": False,
                    "has_running_import": False,
                    "latest_import": None,
                    "active_import": None,
                    "latest_sync_origin": None,
                    "latest_sync_at": None,
                    "last_import_summary": None,
                    "provider": access_source_provider("github_token"),
                    "access_mode": access_source_mode("github_token"),
                    "access_source_type": "github_token",
                    "access_source_label": build_access_source_label(
                        access_source_type="github_token",
                        access_source_ref=token_source.source_ref,
                        display_label=token_source.display_label,
                    ),
                    "access_source_status": token_source.authorization_status,
                    "access_source_status_detail": token_source.last_error,
                    "access_requirement": None,
                    "access_requirement_detail": None,
                }
            try:
                _preflight_repository_access(
                    session=session,
                    repo_ref=repo_ref,
                    owner_scope=effective_owner_scope,
                    access_source_type="public",
                    access_source_ref=None,
                )
            except RepositoryAccessError as exc:
                return {
                    "owner_scope": effective_owner_scope,
                    "repo": repo_ref,
                    "repo_url": repo_url,
                    "workspace_exists": False,
                    "workspace_slug": None,
                    "has_successful_import": False,
                    "can_incremental_sync": False,
                    "has_running_import": False,
                    "latest_import": None,
                    "active_import": None,
                    "latest_sync_origin": None,
                    "latest_sync_at": None,
                    "last_import_summary": None,
                    "provider": access_source_provider("public"),
                    "access_mode": access_source_mode("public"),
                    "access_source_type": "public",
                    "access_source_label": "Public GitHub access",
                    "access_requirement": exc.failure_category,
                    "access_requirement_detail": str(exc),
                }
            return {
                "owner_scope": effective_owner_scope,
                "repo": repo_ref,
                "repo_url": repo_url,
                "workspace_exists": False,
                "workspace_slug": None,
                "has_successful_import": False,
                "can_incremental_sync": False,
                "has_running_import": False,
                "latest_import": None,
                "active_import": None,
                "latest_sync_origin": None,
                "latest_sync_at": None,
                "last_import_summary": None,
                "provider": access_source_provider("public"),
                "access_mode": access_source_mode("public"),
                "access_source_type": "public",
                "access_source_label": "Public GitHub access",
                "access_requirement": None,
                "access_requirement_detail": None,
            }

        jobs = ImportJobRepository(session)
        latest_job = jobs.latest_for_workspace(workspace.id)
        latest_success = jobs.latest_success_for_repo(workspace.id, repo_ref)
        latest_import = serialize_import_job(session=session, job=latest_job) if latest_job is not None else None
        has_running_import = latest_job is not None and latest_job.status in {"queued", "running"}
        active_import = latest_import if has_running_import else None
        source_summary = access_source_summary(
            session=session,
            owner_scope=workspace.owner_scope,
            access_source_type=workspace.access_source_type,
            access_source_ref=workspace.access_source_ref,
        )
        return {
            "owner_scope": workspace.owner_scope,
            "repo": repo_ref,
            "repo_url": repo_url,
            "workspace_exists": True,
            "workspace_slug": workspace.slug,
            "has_successful_import": latest_success is not None,
            "can_incremental_sync": latest_success is not None and not has_running_import,
            "has_running_import": has_running_import,
            "latest_import": latest_import,
            "active_import": active_import,
            "latest_sync_origin": _serialized_sync_origin(latest_import),
            "latest_sync_at": _serialized_sync_timestamp(latest_import),
            "last_import_summary": _serialized_import_summary(latest_import),
            "provider": source_summary["provider"],
            "access_mode": source_summary["access_mode"],
            "access_source_type": workspace.access_source_type,
            "access_source_label": source_summary["access_source_label"],
            "access_source_status": source_summary["access_source_status"],
            "access_source_status_detail": source_summary["access_source_status_detail"],
            "access_requirement": None,
            "access_requirement_detail": None,
        }
    finally:
        session.close()


def bind_github_app_installation(
    *,
    repo: str,
    installation_id: str,
    owner_scope: str | None = None,
    account_login: str | None = None,
    account_type: str | None = None,
    workspace_slug: str | None = None,
) -> dict[str, object | None]:
    session = get_db_session()
    try:
        effective_owner_scope = _owner_scope(owner_scope)
        repo_ref, repo_url = _normalize_repo(repo)
        GitHubAppInstallationRepository(session).upsert(
            owner_scope=effective_owner_scope,
            installation_id=installation_id,
            account_login=account_login,
            account_type=account_type,
        )
        workspace = _resolve_workspace(
            workspaces=WorkspaceRepository(session),
            workspace_slug=workspace_slug,
            owner_scope=effective_owner_scope,
            repo_ref=repo_ref,
            repo_url=repo_url,
            access_source_type="github_app_installation",
            access_source_ref=installation_id,
        )
        session.commit()
        jobs = ImportJobRepository(session)
        latest_job = jobs.latest_for_workspace(workspace.id)
        latest_success = jobs.latest_success_for_repo(workspace.id, repo_ref)
        has_running_import = latest_job is not None and latest_job.status in {"queued", "running"}
        latest_import = serialize_import_job(session=session, job=latest_job) if latest_job is not None else None
        return {
            "owner_scope": workspace.owner_scope,
            "repo": repo_ref,
            "repo_url": repo_url,
            "workspace_exists": True,
            "workspace_slug": workspace.slug,
            "has_successful_import": latest_success is not None,
            "can_incremental_sync": latest_success is not None and not has_running_import,
            "has_running_import": has_running_import,
            "latest_import": latest_import,
            "active_import": latest_import if has_running_import else None,
            "latest_sync_origin": _serialized_sync_origin(latest_import),
            "latest_sync_at": _serialized_sync_timestamp(latest_import),
            "last_import_summary": _serialized_import_summary(latest_import),
            "provider": access_source_provider(workspace.access_source_type),
            "access_mode": access_source_mode(workspace.access_source_type),
            "access_source_type": workspace.access_source_type,
            "access_source_label": build_access_source_label(
                access_source_type=workspace.access_source_type,
                access_source_ref=workspace.access_source_ref,
            ),
        }
    finally:
        session.close()


def bind_github_private_access_source(
    *,
    repo: str,
    token: str,
    owner_scope: str | None = None,
    source_ref: str | None = None,
    source_label: str | None = None,
    workspace_slug: str | None = None,
) -> dict[str, object | None]:
    session = get_db_session()
    try:
        effective_owner_scope = _owner_scope(owner_scope)
        repo_ref, repo_url = _normalize_repo(repo)
        validated_at = datetime.now(timezone.utc)
        try:
            metadata = GitHubClient(token=token, max_pages=get_settings().github_import_max_pages).get_repository_metadata(repo_ref)
        except (httpx.HTTPStatusError, GitHubNetworkError) as exc:
            category, _status, detail = _classify_private_access_validation_failure(exc, repo_ref=repo_ref)
            raise RepositoryAccessError(detail, failure_category=category) from exc

        source_key = (source_ref or repo_ref).strip()
        display_label = (source_label or repo_ref).strip()
        source_record = GitHubTokenAccessSourceRepository(session).upsert(
            owner_scope=effective_owner_scope,
            source_ref=source_key,
            display_label=display_label,
            repo_identity=repo_ref,
            token_secret=token,
            authorization_status="authorized",
            last_error=None,
            validated_at=validated_at,
        )
        workspace = _resolve_workspace(
            workspaces=WorkspaceRepository(session),
            workspace_slug=workspace_slug,
            owner_scope=effective_owner_scope,
            repo_ref=repo_ref,
            repo_url=repo_url,
            access_source_type="github_token",
            access_source_ref=source_record.source_ref,
        )
        session.commit()
        jobs = ImportJobRepository(session)
        latest_job = jobs.latest_for_workspace(workspace.id)
        latest_success = jobs.latest_success_for_repo(workspace.id, repo_ref)
        has_running_import = latest_job is not None and latest_job.status in {"queued", "running"}
        latest_import = serialize_import_job(session=session, job=latest_job) if latest_job is not None else None
        return {
            "owner_scope": workspace.owner_scope,
            "repo": repo_ref,
            "repo_url": repo_url,
            "repo_private": bool(metadata.get("private")),
            "workspace_exists": True,
            "workspace_slug": workspace.slug,
            "has_successful_import": latest_success is not None,
            "can_incremental_sync": latest_success is not None and not has_running_import,
            "has_running_import": has_running_import,
            "latest_import": latest_import,
            "active_import": latest_import if has_running_import else None,
            "latest_sync_origin": _serialized_sync_origin(latest_import),
            "latest_sync_at": _serialized_sync_timestamp(latest_import),
            "last_import_summary": _serialized_import_summary(latest_import),
            "provider": access_source_provider(workspace.access_source_type),
            "access_mode": access_source_mode(workspace.access_source_type),
            "access_source_type": workspace.access_source_type,
            "access_source_label": build_access_source_label(
                access_source_type=workspace.access_source_type,
                access_source_ref=workspace.access_source_ref,
                display_label=source_record.display_label,
            ),
            "access_source_status": source_record.authorization_status,
            "access_source_status_detail": source_record.last_error,
        }
    finally:
        session.close()


def handle_github_webhook(
    *,
    event_name: str,
    delivery_id: str | None,
    body: bytes,
    signature: str | None = None,
) -> dict[str, object | None]:
    settings = get_settings()
    _validate_webhook_signature(body=body, signature=signature, secret=settings.github_app_webhook_secret)
    payload = json.loads(body.decode("utf-8") or "{}")
    installation_id = _extract_installation_id(payload)
    repo = _extract_repo_full_name(payload)
    action = payload.get("action")

    result: dict[str, object | None] = {
        "event": event_name,
        "delivery_id": delivery_id,
        "action": action,
        "repo": repo,
        "installation_id": installation_id,
        "status": "ignored",
    }
    if event_name not in QUALIFYING_WEBHOOK_EVENTS:
        result["reason"] = "unsupported_event"
        return result
    if installation_id is None or repo is None:
        result["reason"] = "missing_installation_or_repo"
        return result

    session = get_db_session()
    try:
        owner_scope = _resolve_owner_scope_for_installation(session=session, installation_id=installation_id)
        if owner_scope is None:
            result["reason"] = "unresolved_owner_scope"
            return result

        repo_ref, repo_url = _normalize_repo(repo)
        workspaces = WorkspaceRepository(session)
        workspace = workspaces.get_by_repo_identity(owner_scope=owner_scope, repo_identity=repo_ref)
        if workspace is None or workspace.access_source_type != "github_app_installation" or workspace.access_source_ref != installation_id:
            result["reason"] = "unresolved_workspace"
            result["owner_scope"] = owner_scope
            return result

        jobs = ImportJobRepository(session)
        if jobs.has_active_for_workspace(workspace.id):
            result["status"] = "ignored"
            result["reason"] = "active_sync_exists"
            result["workspace_slug"] = workspace.slug
            result["owner_scope"] = owner_scope
            return result
    finally:
        session.close()

    job = queue_github_import(
        workspace_slug=workspace.slug,
        repo=repo,
        mode="since_last_sync",
        owner_scope=owner_scope,
        access_source_type="github_app_installation",
        access_source_ref=installation_id,
        sync_origin="webhook",
        trigger_event=event_name,
        trigger_delivery_id=delivery_id,
    )
    return {
        **result,
        "status": "queued",
        "workspace_slug": job["workspace_slug"],
        "owner_scope": owner_scope,
        "job_id": job["job_id"],
        "sync_origin": job.get("sync_origin"),
        "trigger_event": job.get("trigger_event"),
        "queued_job": job,
    }


def serialize_import_job(*, session, job) -> dict[str, int | str | None]:
    workspace = WorkspaceRepository(session).get_by_id(job.workspace_id)
    return {
        "job_id": job.job_id,
        "workspace_slug": workspace.slug if workspace is not None else None,
        "repo": job.repo,
        "mode": job.mode,
        "status": job.status,
        "sync_origin": job.sync_origin,
        "trigger_event": job.trigger_event,
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


def _resolve_workspace(
    *,
    workspaces: WorkspaceRepository,
    workspace_slug: str | None,
    owner_scope: str,
    repo_ref: str,
    repo_url: str,
    access_source_type: str | None,
    access_source_ref: str | None,
):
    if workspace_slug:
        workspace = workspaces.get_by_slug(workspace_slug)
        if workspace is None:
            raise ValueError(f"Workspace not found: {workspace_slug}")
        if workspace.repo_url and workspace.repo_url != repo_url:
            raise ValueError(
                f"Workspace {workspace_slug} is already linked to {workspace.repo_url} and cannot import {repo_ref}"
            )
        return workspaces.bind_access_source(
            workspace,
            owner_scope=workspace.owner_scope or owner_scope,
            repo_identity=workspace.repo_identity or repo_ref,
            access_source_type=access_source_type or workspace.access_source_type or "public",
            access_source_ref=access_source_ref or workspace.access_source_ref,
        )

    existing = workspaces.get_by_repo_identity(owner_scope=owner_scope, repo_identity=repo_ref)
    if existing is not None:
        return workspaces.bind_access_source(
            existing,
            owner_scope=owner_scope,
            repo_identity=repo_ref,
            access_source_type=access_source_type or existing.access_source_type or "public",
            access_source_ref=access_source_ref or existing.access_source_ref,
        )

    slug = _workspace_slug(repo_ref, owner_scope=owner_scope)
    existing_by_slug = workspaces.get_by_slug(slug)
    if existing_by_slug is not None:
        return workspaces.bind_access_source(
            existing_by_slug,
            owner_scope=owner_scope,
            repo_identity=repo_ref,
            access_source_type=access_source_type or existing_by_slug.access_source_type or "public",
            access_source_ref=access_source_ref,
        )
    return workspaces.create(
        slug=slug,
        name=repo_ref,
        repo_url=repo_url,
        owner_scope=owner_scope,
        repo_identity=repo_ref,
        access_source_type=access_source_type or "public",
        access_source_ref=access_source_ref,
    )


def _default_access_source_for_repo(
    *,
    session,
    owner_scope: str,
    repo_ref: str,
    access_source_type: str | None,
    access_source_ref: str | None,
) -> tuple[str | None, str | None]:
    if access_source_type or access_source_ref:
        return access_source_type, access_source_ref
    token_source = GitHubTokenAccessSourceRepository(session).get_by_owner_scope_and_repo_identity(
        owner_scope=owner_scope,
        repo_identity=repo_ref,
    )
    if token_source is not None:
        return "github_token", token_source.source_ref
    return access_source_type, access_source_ref


def _workspace_slug(repo_ref: str, *, owner_scope: str) -> str:
    normalized = "".join(char.lower() if char.isalnum() else "-" for char in repo_ref)
    while "--" in normalized:
        normalized = normalized.replace("--", "-")
    if owner_scope == _owner_scope(None):
        return f"github-{normalized}".strip("-")[:120]
    scope_normalized = "".join(char.lower() if char.isalnum() else "-" for char in owner_scope)
    while "--" in scope_normalized:
        scope_normalized = scope_normalized.replace("--", "-")
    return f"github-{scope_normalized}-{normalized}".strip("-")[:120]


def _classify_failure(exc: Exception) -> str:
    if isinstance(exc, RepositoryAccessError):
        return exc.failure_category
    if isinstance(exc, GitHubNetworkError):
        return "network_failure"
    if isinstance(exc, httpx.HTTPStatusError):
        status_code = exc.response.status_code
        if status_code >= 500:
            return "network_failure"
        if 400 <= status_code < 500:
            return "repository_access_failure"
    if isinstance(exc, (ProviderConfigurationError, ProviderTimeoutError, ProviderRateLimitError, ProviderRequestError, ProviderResponseError)):
        return "provider_failure"
    if "Workspace not found" in str(exc):
        return "workspace_not_found"
    if "owner/repo" in str(exc) or "public GitHub" in str(exc) or "Repository URL" in str(exc):
        return "invalid_repository"
    return "analysis_execution_failed"


def _owner_scope(owner_scope: str | None) -> str:
    settings = get_settings()
    return owner_scope or getattr(settings, "default_owner_scope", DEFAULT_OWNER_SCOPE)


def _default_sync_origin(*, mode: str, access_source_type: str | None) -> str:
    if access_source_type == "github_app_installation":
        return "installation_manual_incremental" if mode == "since_last_sync" else "installation_manual_full"
    if access_source_type == "github_token":
        return "private_manual_incremental" if mode == "since_last_sync" else "private_manual_full"
    return "manual_incremental" if mode == "since_last_sync" else "manual_full"


def _serialized_sync_origin(latest_import: dict | None) -> str | None:
    if not latest_import:
        return None
    origin = latest_import.get("sync_origin")
    return str(origin) if origin else None


def _serialized_sync_timestamp(latest_import: dict | None) -> str | None:
    if not latest_import:
        return None
    finished_at = latest_import.get("finished_at")
    started_at = latest_import.get("started_at")
    return str(finished_at or started_at) if finished_at or started_at else None


def _serialized_import_summary(latest_import: dict | None) -> dict | None:
    if not latest_import:
        return None
    summary = latest_import.get("summary")
    return summary if isinstance(summary, dict) else None


def _access_source_label(access_source_type: str, access_source_ref: str | None) -> str:
    return build_access_source_label(access_source_type=access_source_type, access_source_ref=access_source_ref)


def _extract_installation_id(payload: dict) -> str | None:
    installation = payload.get("installation") or {}
    installation_id = installation.get("id")
    return str(installation_id) if installation_id is not None else None


def _extract_repo_full_name(payload: dict) -> str | None:
    repository = payload.get("repository") or {}
    full_name = repository.get("full_name")
    return str(full_name) if full_name else None


def _resolve_owner_scope_for_installation(*, session, installation_id: str) -> str | None:
    record = GitHubAppInstallationRepository(session).get_by_installation_id(installation_id)
    return record.owner_scope if record is not None else None


def _token_for_workspace(*, session, workspace, settings) -> str | None:
    if workspace.access_source_type == "github_token":
        if not workspace.access_source_ref:
            raise RepositoryAccessError(
                f"Private repository access source is not configured for {workspace.repo_identity or workspace.repo_url or workspace.slug}.",
                failure_category="credential_required",
            )
        record = GitHubTokenAccessSourceRepository(session).get_by_owner_scope_and_source_ref(
            owner_scope=workspace.owner_scope,
            source_ref=workspace.access_source_ref,
        )
        if record is None:
            raise RepositoryAccessError(
                f"Private repository access source is not configured for {workspace.repo_identity or workspace.repo_url or workspace.slug}.",
                failure_category="credential_required",
            )
        return record.token_secret
    return getattr(settings, "github_token", None)


def _github_client_for_workspace(*, session, workspace, settings, repo: str) -> GitHubClient:
    token = _token_for_workspace(session=session, workspace=workspace, settings=settings)
    client = GitHubClient(token=token, max_pages=settings.github_import_max_pages)
    if workspace.access_source_type not in {None, "public"} or not token:
        return client
    try:
        client.get_repository_metadata(repo)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code not in {401, 403}:
            raise
        return GitHubClient(token=None, max_pages=settings.github_import_max_pages)
    return client


def _preflight_repository_access(
    *,
    session,
    repo_ref: str,
    owner_scope: str,
    access_source_type: str,
    access_source_ref: str | None,
) -> None:
    settings = get_settings()
    if access_source_type == "github_token":
        _validate_private_access_source(
            session=session,
            repo_ref=repo_ref,
            owner_scope=owner_scope,
            access_source_ref=access_source_ref,
            max_pages=settings.github_import_max_pages,
        )
        return

    token = getattr(settings, "github_token", None) if access_source_type == "github_app_installation" else None
    try:
        metadata = GitHubClient(token=token, max_pages=settings.github_import_max_pages).get_repository_metadata(repo_ref)
    except httpx.HTTPStatusError as exc:
        if access_source_type == "github_app_installation":
            raise RepositoryAccessError(
                f"Installation-backed repository authorization failed for {repo_ref}.",
                failure_category="authorization_failed",
            ) from exc
        raise RepositoryAccessError(
            f"Repository {repo_ref} is not publicly reachable. Configure private repository access if this repository is private.",
            failure_category="credential_required",
        ) from exc
    except GitHubNetworkError as exc:
        raise RepositoryAccessError(
            f"GitHub provider or network failure while checking repository access for {repo_ref}.",
            failure_category="network_failure",
        ) from exc

    if access_source_type == "public" and metadata.get("private"):
        raise RepositoryAccessError(
            f"Repository {repo_ref} is private. Configure an owner-authorized access source before importing it.",
            failure_category="credential_required",
        )


def _validate_private_access_source(
    *,
    session,
    repo_ref: str,
    owner_scope: str,
    access_source_ref: str | None,
    max_pages: int,
) -> None:
    if not access_source_ref:
        raise RepositoryAccessError(
            f"Private repository access source is not configured for {repo_ref}.",
            failure_category="credential_required",
        )
    repository = GitHubTokenAccessSourceRepository(session)
    record = repository.get_by_owner_scope_and_source_ref(owner_scope=owner_scope, source_ref=access_source_ref)
    if record is None:
        raise RepositoryAccessError(
            f"Private repository access source is not configured for {repo_ref}.",
            failure_category="credential_required",
        )
    if record.repo_identity != repo_ref:
        raise RepositoryAccessError(
            f"Private repository source {record.source_ref} is not authorized for {repo_ref}.",
            failure_category="authorization_failed",
        )
    validated_at = datetime.now(timezone.utc)
    try:
        GitHubClient(token=record.token_secret, max_pages=max_pages).get_repository_metadata(repo_ref)
        repository.mark_authorized(record, validated_at=validated_at)
    except (httpx.HTTPStatusError, GitHubNetworkError) as exc:
        category, status, detail = _classify_private_access_validation_failure(exc, repo_ref=repo_ref)
        repository.mark_status(record, status=status, validated_at=validated_at, error_message=detail)
        raise RepositoryAccessError(detail, failure_category=category) from exc


def _classify_private_access_validation_failure(exc: Exception, *, repo_ref: str) -> tuple[str, str, str]:
    if isinstance(exc, GitHubNetworkError):
        return "network_failure", "provider_failure", f"{PRIVATE_ACCESS_NETWORK_DETAIL} Retry validation for {repo_ref}."
    if isinstance(exc, httpx.HTTPStatusError):
        status_code = exc.response.status_code
        if status_code in {401, 403}:
            return "authorization_failed", "unauthorized", PRIVATE_ACCESS_AUTH_DETAIL
        if status_code == 404:
            return "repository_not_found", "repository_not_found", f"Repository {repo_ref} was not found for the selected private access source."
        if 400 <= status_code < 500:
            return "validation_failed", "invalid", f"GitHub rejected private repository access validation for {repo_ref}."
    return "provider_failure", "provider_failure", f"{PRIVATE_ACCESS_NETWORK_DETAIL} Retry validation for {repo_ref}."


def _validate_webhook_signature(*, body: bytes, signature: str | None, secret: str | None) -> None:
    if not secret:
        return
    if not signature or not signature.startswith("sha256="):
        raise ValueError("Missing GitHub webhook signature")
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    expected = f"sha256={digest}"
    if not hmac.compare_digest(expected, signature):
        raise ValueError("Invalid GitHub webhook signature")


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
            jobs_repo = ImportJobRepository(progress_session)
            
            # Check pause status
            latest_job = jobs_repo.get_by_job_id(job_id)
            if latest_job and latest_job.status == "paused":
                while True:
                    progress_session.refresh(latest_job)
                    if latest_job.status != "paused":
                        break
                    import time
                    time.sleep(2.0)
            if latest_job and latest_job.status == "cancelled":
                raise Exception("Import cancelled")

            jobs_repo.merge_summary(
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
