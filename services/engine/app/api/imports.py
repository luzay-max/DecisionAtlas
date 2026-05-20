from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Query, Request
from pydantic import BaseModel

from app.auth import AuthContext, require_actor, require_scope_role, require_workspace_role
from app.db.session import get_db_session
from app.jobs.import_jobs import (
    ActiveImportConflict,
    bind_github_app_installation,
    bind_github_private_access_source,
    get_import_job_status,
    handle_github_webhook,
    lookup_github_workspace,
    RepositoryAccessError,
    queue_github_import,
    run_github_import,
)
from app.repositories.import_jobs import ImportJobRepository
from app.repositories.workspaces import WorkspaceRepository

router = APIRouter(prefix="/imports", tags=["imports"])


class GitHubImportRequest(BaseModel):
    workspace_slug: str | None = None
    repo: str
    mode: str = "full"
    owner_scope: str | None = None
    access_source_type: str | None = None
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
def import_github(
    request: GitHubImportRequest,
    background_tasks: BackgroundTasks,
    auth: AuthContext = Depends(require_actor),
) -> dict:
    try:
        require_scope_role(auth, owner_scope=auth.owner_scope, required_role="admin")
        if request.workspace_slug:
            session = get_db_session()
            try:
                require_workspace_role(session, auth, workspace_slug=request.workspace_slug, required_role="admin")
            finally:
                session.close()
        job = queue_github_import(
            workspace_slug=request.workspace_slug,
            repo=request.repo,
            mode=request.mode,
            owner_scope=auth.owner_scope,
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
    except ActiveImportConflict as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "message": str(exc),
                "active_import": exc.active_job,
            },
        ) from exc
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
def lookup_import_target(
    repo: str = Query(..., min_length=3),
    auth: AuthContext = Depends(require_actor),
) -> dict:
    try:
        return lookup_github_workspace(repo=repo, owner_scope=auth.owner_scope)
    except ValueError as exc:
        if "owner/repo" in str(exc) or "public GitHub" in str(exc) or "Repository URL" in str(exc):
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/github/installations/bind")
def bind_installation(
    request: GitHubInstallationBindingRequest,
    auth: AuthContext = Depends(require_actor),
) -> dict:
    try:
        require_scope_role(auth, owner_scope=auth.owner_scope, required_role="admin")
        return bind_github_app_installation(
            repo=request.repo,
            installation_id=request.installation_id,
            owner_scope=auth.owner_scope,
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
def bind_private_access(
    request: GitHubPrivateAccessBindingRequest,
    auth: AuthContext = Depends(require_actor),
) -> dict:
    try:
        require_scope_role(auth, owner_scope=auth.owner_scope, required_role="admin")
        return bind_github_private_access_source(
            repo=request.repo,
            token=request.token,
            owner_scope=auth.owner_scope,
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
def get_import_job(
    job_id: str,
    auth: AuthContext = Depends(require_actor),
) -> dict:
    session = get_db_session()
    try:
        job = ImportJobRepository(session).get_by_job_id(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail=f"Import job not found: {job_id}")
        workspace = WorkspaceRepository(session).get_by_id(job.workspace_id)
        if workspace is None:
            raise HTTPException(status_code=404, detail=f"Workspace not found for import job: {job_id}")
        require_workspace_role(session, auth, workspace_slug=workspace.slug, required_role="viewer", hide_not_found=True)
        return get_import_job_status(job_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    finally:
        session.close()
