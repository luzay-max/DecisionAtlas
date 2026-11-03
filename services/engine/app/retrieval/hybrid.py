from __future__ import annotations

from sqlalchemy.orm import Session

from app.indexing.embedder import Embedder, FakeEmbedder
from app.llm.base import ProviderError
from app.retrieval.full_text import RetrievalHit, full_text_search
from app.retrieval.vector_search import vector_search

FULLTEXT_WEIGHT = 1.0
VECTOR_WEIGHT = 0.65


def _normalized_scores(hits: list[RetrievalHit]) -> dict[int, float]:
    if not hits:
        return {}
    max_score = max((hit.score for hit in hits), default=0.0)
    if max_score <= 0:
        return {}
    return {hit.decision_id: hit.score / max_score for hit in hits}


def hybrid_search_with_mode(
    *,
    session: Session,
    workspace_slug: str,
    query: str,
    embedder: Embedder,
    review_state: str = "accepted",
) -> tuple[list[RetrievalHit], str]:
    """Return hits and an honest per-query retrieval mode.

    FakeEmbedder is intentionally not a semantic source. Provider failures
    fall back to the already-authorized, accepted-only lexical hits; no
    synthetic vector results or fabricated citations are added.
    """
    full_text_hits = full_text_search(
        session=session,
        workspace_slug=workspace_slug,
        query=query,
        review_state=review_state,
    )
    if isinstance(embedder, FakeEmbedder):
        return full_text_hits, "lexical_only"

    try:
        vector_hits = vector_search(
            session=session,
            workspace_slug=workspace_slug,
            query=query,
            embedder=embedder,
            review_state=review_state,
        )
    except ProviderError:
        # Fail visibly to lexical-only mode rather than fail the entire
        # public evidence query or silently claim successful semantic search.
        return full_text_hits, "lexical_fallback"

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

    return sorted(combined.values(), key=lambda item: item.score, reverse=True), "hybrid"


def hybrid_search(
    *,
    session: Session,
    workspace_slug: str,
    query: str,
    embedder: Embedder,
    review_state: str = "accepted",
) -> list[RetrievalHit]:
    # Retain the existing API for agent tools/older callers. The Why route
    # uses hybrid_search_with_mode so it can disclose fallback explicitly.
    hits, _ = hybrid_search_with_mode(
        session=session,
        workspace_slug=workspace_slug,
        query=query,
        embedder=embedder,
        review_state=review_state,
    )
    return hits
