from __future__ import annotations

from app.indexing.embedder import Embedder
from app.retrieval.full_text import RetrievalHit, full_text_search
from app.retrieval.vector_search import vector_search
from sqlalchemy.orm import Session


def hybrid_search(
    *,
    session: Session,
    workspace_slug: str,
    query: str,
    embedder: Embedder,
    review_state: str = "accepted",
) -> list[RetrievalHit]:
    combined: dict[int, RetrievalHit] = {}
    for hit in full_text_search(session=session, workspace_slug=workspace_slug, query=query, review_state=review_state):
        combined[hit.decision_id] = hit

    for vector_hit in vector_search(
        session=session,
        workspace_slug=workspace_slug,
        query=query,
        embedder=embedder,
        review_state=review_state,
    ):
        existing = combined.get(vector_hit.decision_id)
        if existing is None:
            vector_hit.score = vector_hit.score * 0.001
            combined[vector_hit.decision_id] = vector_hit
        else:
            existing.score += vector_hit.score * 0.001

    return sorted(combined.values(), key=lambda item: item.score, reverse=True)
