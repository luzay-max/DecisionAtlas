from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.jobs.import_jobs import run_github_import

router = APIRouter(prefix="/imports", tags=["imports"])


class GitHubImportRequest(BaseModel):
    workspace_slug: str
    repo: str


@router.post("/github")
def import_github(request: GitHubImportRequest) -> dict[str, int | str]:
    try:
        return run_github_import(workspace_slug=request.workspace_slug, repo=request.repo)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
