from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ReviewAuditEvent

RATIONALE_LIMIT = 1000


def bounded_rationale(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    if not stripped:
        return None
    return stripped[:RATIONALE_LIMIT]


class ReviewAuditRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_event(
        self,
        *,
        owner_scope: str,
        workspace_id: int | None,
        actor_id: int | None,
        actor_username: str,
        actor_role: str,
        target_type: str,
        target_id: int,
        action: str,
        previous_state: dict | None,
        new_state: dict | None,
        rationale: str | None = None,
        metadata: dict | None = None,
    ) -> ReviewAuditEvent:
        event = ReviewAuditEvent(
            owner_scope=owner_scope,
            workspace_id=workspace_id,
            actor_id=actor_id,
            actor_username=actor_username,
            actor_role=actor_role,
            target_type=target_type,
            target_id=target_id,
            action=action,
            previous_state_json=previous_state,
            new_state_json=new_state,
            rationale=bounded_rationale(rationale),
            metadata_json=metadata,
        )
        self.session.add(event)
        self.session.flush()
        return event

    def list_for_target(
        self,
        *,
        owner_scope: str,
        target_type: str,
        target_id: int,
        limit: int = 20,
    ) -> list[ReviewAuditEvent]:
        stmt = (
            select(ReviewAuditEvent)
            .where(
                ReviewAuditEvent.owner_scope == owner_scope,
                ReviewAuditEvent.target_type == target_type,
                ReviewAuditEvent.target_id == target_id,
            )
            .order_by(ReviewAuditEvent.created_at.desc(), ReviewAuditEvent.id.desc())
            .limit(limit)
        )
        return list(self.session.scalars(stmt))


def serialize_review_audit_event(event: ReviewAuditEvent) -> dict:
    return {
        "id": event.id,
        "owner_scope": event.owner_scope,
        "workspace_id": event.workspace_id,
        "actor_id": event.actor_id,
        "actor_username": event.actor_username,
        "actor_role": event.actor_role,
        "target_type": event.target_type,
        "target_id": event.target_id,
        "action": event.action,
        "previous_state": event.previous_state_json,
        "new_state": event.new_state_json,
        "rationale": event.rationale,
        "metadata": event.metadata_json,
        "created_at": event.created_at.isoformat() if event.created_at else None,
    }
