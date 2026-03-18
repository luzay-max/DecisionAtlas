from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import Artifact
from app.indexing.embedder import Embedder, FakeEmbedder
from app.repositories.decisions import DecisionRepository
from app.retrieval.hybrid import hybrid_search


@dataclass(frozen=True)
class SemanticCandidate:
    decision_id: int
    title: str
    problem: str
    chosen_option: str
    tradeoffs: str
    score: float
    created_at: datetime | None


def recall_related_decisions(
    *,
    session: Session,
    workspace_slug: str,
    artifact: Artifact,
    embedder: Embedder | None = None,
    limit: int = 3,
) -> list[SemanticCandidate]:
    query = _build_query(artifact)
    if not query:
        return []

    hits = hybrid_search(
        session=session,
        workspace_slug=workspace_slug,
        query=query,
        embedder=embedder or FakeEmbedder(),
        review_state="accepted",
    )
    decisions = DecisionRepository(session)
    candidates: list[SemanticCandidate] = []
    for hit in hits[:limit]:
        decision = decisions.get_by_id(hit.decision_id)
        if decision is None:
            continue
        candidates.append(
            SemanticCandidate(
                decision_id=hit.decision_id,
                title=hit.title,
                problem=hit.problem,
                chosen_option=hit.chosen_option,
                tradeoffs=hit.tradeoffs,
                score=hit.score,
                created_at=decision.created_at,
            )
        )
    return candidates


def _build_query(artifact: Artifact) -> str:
    parts = [artifact.title or "", artifact.content[:500]]
    return " ".join(part.strip() for part in parts if part and part.strip())
