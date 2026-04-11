from __future__ import annotations

from sqlalchemy import or_, select
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

    def get_by_repo_identity(self, *, owner_scope: str, repo_identity: str) -> Workspace | None:
        stmt = select(Workspace).where(
            Workspace.owner_scope == owner_scope,
            or_(
                Workspace.repo_identity == repo_identity,
                Workspace.repo_identity.is_(None) & (Workspace.repo_url == f"https://github.com/{repo_identity}"),
            ),
        )
        return self.session.scalar(stmt)

    def create(
        self,
        *,
        slug: str,
        name: str,
        repo_url: str | None,
        owner_scope: str,
        repo_identity: str | None,
        access_source_type: str = "public",
        access_source_ref: str | None = None,
    ) -> Workspace:
        workspace = Workspace(
            slug=slug,
            name=name,
            repo_url=repo_url,
            owner_scope=owner_scope,
            repo_identity=repo_identity,
            access_source_type=access_source_type,
            access_source_ref=access_source_ref,
        )
        self.session.add(workspace)
        self.session.flush()
        return workspace

    def bind_access_source(
        self,
        workspace: Workspace,
        *,
        owner_scope: str,
        repo_identity: str | None,
        access_source_type: str,
        access_source_ref: str | None,
    ) -> Workspace:
        workspace.owner_scope = owner_scope
        workspace.repo_identity = repo_identity
        workspace.access_source_type = access_source_type
        workspace.access_source_ref = access_source_ref
        self.session.flush()
        return workspace
