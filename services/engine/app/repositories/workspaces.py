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
