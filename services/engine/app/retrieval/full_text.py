from __future__ import annotations

from dataclasses import dataclass
import re

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


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "before",
    "by",
    "did",
    "do",
    "does",
    "for",
    "how",
    "in",
    "is",
    "it",
    "its",
    "need",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "use",
    "was",
    "why",
}

TERM_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)?")


def _tokenize(text: str) -> list[str]:
    return TERM_PATTERN.findall(text.lower())


def full_text_search(*, session: Session, workspace_slug: str, query: str, review_state: str = "accepted") -> list[RetrievalHit]:
    workspace = WorkspaceRepository(session).get_by_slug(workspace_slug)
    if workspace is None:
        raise ValueError(f"Workspace not found: {workspace_slug}")

    query_terms = [term for term in _tokenize(query) if term not in STOP_WORDS]
    if not query_terms:
        query_terms = _tokenize(query)
    decisions = DecisionRepository(session).list_by_review_state(workspace.id, review_state)
    hits: list[RetrievalHit] = []
    for decision in decisions:
        fields = {
            "title": decision.title.lower(),
            "problem": decision.problem.lower(),
            "chosen_option": decision.chosen_option.lower(),
            "tradeoffs": decision.tradeoffs.lower(),
            "context": (decision.context or "").lower(),
            "constraints": (decision.constraints or "").lower(),
        }
        score = 0.0
        matched_terms = 0
        for term in query_terms:
            field_matches = (
                fields["title"].count(term) * 4
                + fields["chosen_option"].count(term) * 3
                + fields["problem"].count(term) * 2
                + fields["tradeoffs"].count(term)
                + fields["context"].count(term)
                + fields["constraints"].count(term)
            )
            if field_matches > 0:
                matched_terms += 1
                score += float(field_matches)

        score += matched_terms * 2.0
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
