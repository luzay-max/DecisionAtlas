from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Decision


class DecisionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_candidate(
        self,
        *,
        workspace_id: int,
        title: str,
        problem: str,
        context: str | None,
        constraints: str | None,
        chosen_option: str,
        tradeoffs: str,
        confidence: float,
    ) -> Decision:
        decision = Decision(
            workspace_id=workspace_id,
            title=title,
            review_state="candidate",
            status="active",
            problem=problem,
            context=context,
            constraints=constraints,
            chosen_option=chosen_option,
            tradeoffs=tradeoffs,
            confidence=confidence,
        )
        self.session.add(decision)
        self.session.flush()
        return decision

    def list_by_workspace(self, workspace_id: int) -> list[Decision]:
        stmt = select(Decision).where(Decision.workspace_id == workspace_id).order_by(Decision.id)
        return list(self.session.scalars(stmt))

    def list_by_review_state(self, workspace_id: int, review_state: str | None = None) -> list[Decision]:
        stmt = select(Decision).where(Decision.workspace_id == workspace_id)
        if review_state is not None:
            stmt = stmt.where(Decision.review_state == review_state)
        stmt = stmt.order_by(Decision.id.desc())
        return list(self.session.scalars(stmt))

    def get_by_id(self, decision_id: int) -> Decision | None:
        stmt = select(Decision).where(Decision.id == decision_id)
        return self.session.scalar(stmt)

    def update_review_state(self, decision_id: int, review_state: str) -> Decision | None:
        decision = self.get_by_id(decision_id)
        if decision is None:
            return None
        decision.review_state = review_state
        if review_state == "superseded":
            decision.status = "superseded"
        self.session.flush()
        return decision

    def counts_by_review_state(self, workspace_id: int) -> dict[str, int]:
        decisions = self.list_by_workspace(workspace_id)
        counts: dict[str, int] = {}
        for decision in decisions:
            counts[decision.review_state] = counts.get(decision.review_state, 0) + 1
        return counts
