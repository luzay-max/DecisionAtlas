from __future__ import annotations

from datetime import datetime

from sqlalchemy import delete
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

    def get_by_id(self, alert_id: int) -> DriftAlert | None:
        stmt = select(DriftAlert).where(DriftAlert.id == alert_id)
        return self.session.scalar(stmt)

    def update_disposition(
        self,
        alert: DriftAlert,
        *,
        status: str,
        handled_by: str,
        handled_at: datetime,
        disposition_rationale: str | None,
    ) -> DriftAlert:
        alert.status = status
        alert.handled_by = handled_by
        alert.handled_at = handled_at
        alert.disposition_rationale = disposition_rationale
        self.session.flush()
        return alert

    def delete_by_workspace_and_type(self, workspace_id: int, alert_type: str) -> None:
        stmt = delete(DriftAlert).where(
            DriftAlert.workspace_id == workspace_id,
            DriftAlert.alert_type == alert_type,
        )
        self.session.execute(stmt)
        self.session.flush()

    def delete_by_workspace_and_types(self, workspace_id: int, alert_types: list[str] | tuple[str, ...]) -> None:
        if not alert_types:
            return
        stmt = delete(DriftAlert).where(
            DriftAlert.workspace_id == workspace_id,
            DriftAlert.alert_type.in_(tuple(alert_types)),
        )
        self.session.execute(stmt)
        self.session.flush()
