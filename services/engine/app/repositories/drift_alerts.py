from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import DriftAlert


class DriftAlertRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_or_update(
        self,
        *,
        workspace_id: int,
        artifact_id: int | None,
        decision_id: int | None,
        alert_type: str,
        summary: str,
        status: str,
    ) -> tuple[DriftAlert, bool]:
        stmt = select(DriftAlert).where(
            DriftAlert.workspace_id == workspace_id,
            DriftAlert.artifact_id == artifact_id,
            DriftAlert.decision_id == decision_id,
            DriftAlert.alert_type == alert_type,
        )
        alert = self.session.scalar(stmt)
        created = alert is None
        if alert is None:
            alert = DriftAlert(
                workspace_id=workspace_id,
                artifact_id=artifact_id,
                decision_id=decision_id,
                alert_type=alert_type,
                summary=summary,
                status=status,
            )
            self.session.add(alert)
        else:
            alert.summary = summary
            alert.status = status

        self.session.flush()
        return alert, created

    def list_by_workspace(self, workspace_id: int, limit: int | None = None) -> list[DriftAlert]:
        stmt = select(DriftAlert).where(DriftAlert.workspace_id == workspace_id).order_by(DriftAlert.created_at.desc())
        if limit is not None:
            stmt = stmt.limit(limit)
        return list(self.session.scalars(stmt))

    def list_recent_by_workspace(self, workspace_id: int, limit: int = 5) -> list[DriftAlert]:
        return self.list_by_workspace(workspace_id, limit=limit)
