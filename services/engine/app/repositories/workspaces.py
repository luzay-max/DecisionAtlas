from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Workspace


class WorkspaceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_slug(self, slug: str) -> Workspace | None:
        stmt = select(Workspace).where(Workspace.slug == slug)
        return self.session.scalar(stmt)

    def get_by_id(self, workspace_id: int) -> Workspace | None:
        stmt = select(Workspace).where(Workspace.id == workspace_id)
        return self.session.scalar(stmt)

    def get_by_repo_url(self, repo_url: str) -> Workspace | None:
        stmt = select(Workspace).where(Workspace.repo_url == repo_url)
        return self.session.scalar(stmt)

    def create(self, *, slug: str, name: str, repo_url: str | None) -> Workspace:
        workspace = Workspace(slug=slug, name=name, repo_url=repo_url)
        self.session.add(workspace)
        self.session.flush()
        return workspace
