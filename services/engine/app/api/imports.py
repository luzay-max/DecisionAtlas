from __future__ import annotations

from fastapi import BackgroundTasks
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.jobs.import_jobs import get_import_job_status, queue_github_import, run_github_import

router = APIRouter(prefix="/imports", tags=["imports"])


class GitHubImportRequest(BaseModel):
    workspace_slug: str
    repo: str
    mode: str = "full"


@router.post("/github")
def import_github(request: GitHubImportRequest, background_tasks: BackgroundTasks) -> dict:
    try:
        job = queue_github_import(workspace_slug=request.workspace_slug, repo=request.repo, mode=request.mode)
        background_tasks.add_task(
            run_github_import,
            job_id=str(job["job_id"]),
            workspace_slug=request.workspace_slug,
            repo=request.repo,
            mode=request.mode,
        )
        return job
    except ValueError as exc:
        if "Unsupported import mode" in str(exc):
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{job_id}")
def get_import_job(job_id: str) -> dict:
    try:
        return get_import_job_status(job_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
