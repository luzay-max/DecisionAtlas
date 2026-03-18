from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.repositories.decisions import DecisionRepository
from app.repositories.workspaces import WorkspaceRepository


@dataclass(slots=True)
class RetrievalHit:
    decision_id: int
    title: str
    problem: str
    chosen_option: str
    tradeoffs: str
    score: float


def full_text_search(*, session: Session, workspace_slug: str, query: str, review_state: str = "accepted") -> list[RetrievalHit]:
    workspace = WorkspaceRepository(session).get_by_slug(workspace_slug)
    if workspace is None:
        raise ValueError(f"Workspace not found: {workspace_slug}")

    query_terms = [term for term in query.lower().split() if term]
    decisions = DecisionRepository(session).list_by_review_state(workspace.id, review_state)
    hits: list[RetrievalHit] = []
    for decision in decisions:
        haystack = " ".join(
            [
                decision.title,
                decision.problem,
                decision.chosen_option,
                decision.tradeoffs,
                decision.context or "",
                decision.constraints or "",
            ]
        ).lower()
        score = float(sum(haystack.count(term) for term in query_terms))
        if score <= 0:
            continue
        hits.append(
            RetrievalHit(
                decision_id=decision.id,
                title=decision.title,
                problem=decision.problem,
                chosen_option=decision.chosen_option,
                tradeoffs=decision.tradeoffs,
                score=score,
            )
        )
    return sorted(hits, key=lambda item: item.score, reverse=True)
