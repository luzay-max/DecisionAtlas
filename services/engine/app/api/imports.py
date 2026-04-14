from __future__ import annotations

from fastapi import BackgroundTasks, Header, Query, Request
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.jobs.import_jobs import (
    bind_github_app_installation,
    bind_github_private_access_source,
    get_import_job_status,
    handle_github_webhook,
    lookup_github_workspace,
    RepositoryAccessError,
    queue_github_import,
    run_github_import,
)

router = APIRouter(prefix="/imports", tags=["imports"])


class GitHubImportRequest(BaseModel):
    workspace_slug: str | None = None
    repo: str
    mode: str = "full"
    owner_scope: str | None = None
    access_source_type: str = "public"
    access_source_ref: str | None = None


class GitHubInstallationBindingRequest(BaseModel):
    repo: str
    installation_id: str
    owner_scope: str | None = None
    account_login: str | None = None
    account_type: str | None = None
    workspace_slug: str | None = None


class GitHubPrivateAccessBindingRequest(BaseModel):
    repo: str
    token: str
    owner_scope: str | None = None
    source_ref: str | None = None
    source_label: str | None = None
    workspace_slug: str | None = None


@router.post("/github")
def import_github(request: GitHubImportRequest, background_tasks: BackgroundTasks) -> dict:
    try:
        job = queue_github_import(
            workspace_slug=request.workspace_slug,
            repo=request.repo,
            mode=request.mode,
            owner_scope=request.owner_scope,
            access_source_type=request.access_source_type,
            access_source_ref=request.access_source_ref,
        )
        background_tasks.add_task(
            run_github_import,
            job_id=str(job["job_id"]),
            workspace_slug=str(job["workspace_slug"]),
            repo=str(job["repo"]),
            mode=request.mode,
        )
        return job
    except RepositoryAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        if (
            "Unsupported import mode" in str(exc)
            or "owner/repo" in str(exc)
            or "public GitHub" in str(exc)
            or "Repository URL" in str(exc)
            or "cannot import" in str(exc)
        ):
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/lookup")
def lookup_import_target(repo: str = Query(..., min_length=3)) -> dict:
    try:
        return lookup_github_workspace(repo=repo)
    except ValueError as exc:
        if "owner/repo" in str(exc) or "public GitHub" in str(exc) or "Repository URL" in str(exc):
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/github/installations/bind")
def bind_installation(request: GitHubInstallationBindingRequest) -> dict:
    try:
        return bind_github_app_installation(
            repo=request.repo,
            installation_id=request.installation_id,
            owner_scope=request.owner_scope,
            account_login=request.account_login,
            account_type=request.account_type,
            workspace_slug=request.workspace_slug,
        )
    except RepositoryAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        if "owner/repo" in str(exc) or "public GitHub" in str(exc) or "Repository URL" in str(exc) or "cannot import" in str(exc):
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/github/private-access/bind")
def bind_private_access(request: GitHubPrivateAccessBindingRequest) -> dict:
    try:
        return bind_github_private_access_source(
            repo=request.repo,
            token=request.token,
            owner_scope=request.owner_scope,
            source_ref=request.source_ref,
            source_label=request.source_label,
            workspace_slug=request.workspace_slug,
        )
    except RepositoryAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        if "owner/repo" in str(exc) or "public GitHub" in str(exc) or "Repository URL" in str(exc) or "cannot import" in str(exc):
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/github/webhook")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_github_event: str = Header(...),
    x_github_delivery: str | None = Header(None),
    x_hub_signature_256: str | None = Header(None),
) -> dict:
    try:
        body = await request.body()
        result = handle_github_webhook(
            event_name=x_github_event,
            delivery_id=x_github_delivery,
            body=body,
            signature=x_hub_signature_256,
        )
        queued_job = result.pop("queued_job", None)
        if isinstance(queued_job, dict):
            background_tasks.add_task(
                run_github_import,
                job_id=str(queued_job["job_id"]),
                workspace_slug=str(queued_job["workspace_slug"]),
                repo=str(queued_job["repo"]),
                mode="since_last_sync",
            )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{job_id}")
def get_import_job(job_id: str) -> dict:
    try:
        return get_import_job_status(job_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
