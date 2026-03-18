from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import SourceRef


class SourceRefRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        *,
        decision_id: int,
        artifact_id: int,
        span_start: int | None,
        span_end: int | None,
        quote: str,
        url: str | None,
        relevance_score: float | None,
    ) -> SourceRef:
        source_ref = SourceRef(
            decision_id=decision_id,
            artifact_id=artifact_id,
            span_start=span_start,
            span_end=span_end,
            quote=quote,
            url=url,
            relevance_score=relevance_score,
        )
        self.session.add(source_ref)
        self.session.flush()
        return source_ref

    def list_by_decision(self, decision_id: int) -> list[SourceRef]:
        stmt = select(SourceRef).where(SourceRef.decision_id == decision_id).order_by(SourceRef.id)
        return list(self.session.scalars(stmt))

    def exists_for_artifact(self, artifact_id: int) -> bool:
        stmt = select(SourceRef.id).where(SourceRef.artifact_id == artifact_id).limit(1)
        return self.session.scalar(stmt) is not None
