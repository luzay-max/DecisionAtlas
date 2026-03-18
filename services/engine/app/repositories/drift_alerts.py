from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import DriftAlert


class DriftAlertRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_recent_by_workspace(self, workspace_id: int, limit: int = 5) -> list[DriftAlert]:
        stmt = (
            select(DriftAlert)
            .where(DriftAlert.workspace_id == workspace_id)
            .order_by(DriftAlert.created_at.desc())
            .limit(limit)
        )
        return list(self.session.scalars(stmt))
