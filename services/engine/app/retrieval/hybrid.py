from __future__ import annotations

from app.indexing.embedder import Embedder
from app.retrieval.full_text import RetrievalHit, full_text_search
from app.retrieval.vector_search import vector_search
from sqlalchemy.orm import Session

FULLTEXT_WEIGHT = 1.0
VECTOR_WEIGHT = 0.45


def _normalized_scores(hits: list[RetrievalHit]) -> dict[int, float]:
    if not hits:
        return {}
    max_score = max((hit.score for hit in hits), default=0.0)
    if max_score <= 0:
        return {}
    return {hit.decision_id: hit.score / max_score for hit in hits}


def hybrid_search(
    *,
    session: Session,
    workspace_slug: str,
    query: str,
    embedder: Embedder,
    review_state: str = "accepted",
) -> list[RetrievalHit]:
    full_text_hits = full_text_search(
        session=session,
        workspace_slug=workspace_slug,
        query=query,
        review_state=review_state,
    )
    vector_hits = vector_search(
        session=session,
        workspace_slug=workspace_slug,
        query=query,
        embedder=embedder,
        review_state=review_state,
    )

    full_text_scores = _normalized_scores(full_text_hits)
    vector_scores = _normalized_scores(vector_hits)
    combined: dict[int, RetrievalHit] = {}
    for hit in full_text_hits:
        hit.score = full_text_scores.get(hit.decision_id, 0.0) * FULLTEXT_WEIGHT
        combined[hit.decision_id] = hit

    for vector_hit in vector_hits:
        existing = combined.get(vector_hit.decision_id)
        weighted_score = vector_scores.get(vector_hit.decision_id, 0.0) * VECTOR_WEIGHT
        if existing is None:
            vector_hit.score = weighted_score
            combined[vector_hit.decision_id] = vector_hit
        else:
            existing.score += weighted_score

    return sorted(combined.values(), key=lambda item: item.score, reverse=True)
