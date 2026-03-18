from __future__ import annotations

from app.indexing.embedder import Embedder
from app.repositories.decisions import DecisionRepository
from app.repositories.workspaces import WorkspaceRepository
from app.retrieval.full_text import RetrievalHit
from sqlalchemy.orm import Session


def _similarity(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


def vector_search(
    *,
    session: Session,
    workspace_slug: str,
    query: str,
    embedder: Embedder,
    review_state: str = "accepted",
) -> list[RetrievalHit]:
    workspace = WorkspaceRepository(session).get_by_slug(workspace_slug)
    if workspace is None:
      raise ValueError(f"Workspace not found: {workspace_slug}")

    decisions = DecisionRepository(session).list_by_review_state(workspace.id, review_state)
    if not decisions:
        return []

    query_embedding = embedder.embed([query])[0]
    decision_texts = [
        " ".join([decision.title, decision.problem, decision.chosen_option, decision.tradeoffs])
        for decision in decisions
    ]
    decision_embeddings = embedder.embed(decision_texts)

    hits = []
    for decision, embedding in zip(decisions, decision_embeddings):
        score = _similarity(query_embedding, embedding)
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
