from __future__ import annotations

from app.indexing.embedder import Embedder
from app.provenance import get_workspace_provenance
from app.repositories.decisions import DecisionRepository
from app.repositories.source_refs import SourceRefRepository
from app.repositories.workspaces import WorkspaceRepository
from app.retrieval.hybrid import hybrid_search
from app.retrieval.query_rewrite import rewrite_query
from sqlalchemy.orm import Session


def answer_why_question(
    *,
    session: Session,
    workspace_slug: str,
    question: str,
    embedder: Embedder,
) -> dict:
    workspace = WorkspaceRepository(session).get_by_slug(workspace_slug)
    if workspace is None:
        raise ValueError(f"Workspace not found: {workspace_slug}")
    provenance = get_workspace_provenance(session=session, workspace=workspace)
    rewritten = rewrite_query(question)
    hits = hybrid_search(
        session=session,
        workspace_slug=workspace_slug,
        query=rewritten,
        embedder=embedder,
        review_state="accepted",
    )
    if not hits:
        return {
            "status": "insufficient_evidence",
            "question": question,
            "answer": "Insufficient evidence. Review more artifacts or accept more decisions first.",
            "citations": [],
            "answer_context": {
                "workspace_mode": provenance.workspace_mode,
                "source_summary": provenance.source_summary,
            },
        }

    decisions = DecisionRepository(session)
    source_refs = SourceRefRepository(session)
    top_score = hits[0].score
    top_hits = [hit for hit in hits if hit.score >= (top_score * 0.5)][:2]
    citations = []
    answer_parts = []
    for hit in top_hits:
        decision = decisions.get_by_id(hit.decision_id)
        if decision is None:
            continue
        answer_parts.append(
            f"{decision.title}: {decision.chosen_option} Tradeoffs: {decision.tradeoffs}"
        )
        for source_ref in source_refs.list_by_decision(decision.id)[:2]:
            citations.append(
                {
                    "decision_id": decision.id,
                    "source_ref_id": source_ref.id,
                    "quote": source_ref.quote,
                    "url": source_ref.url,
                }
            )

    if len(citations) < 2:
        return {
            "status": "insufficient_evidence",
            "question": question,
            "answer": "Insufficient evidence. The matched decisions do not have enough supporting citations yet.",
            "citations": citations,
            "answer_context": {
                "workspace_mode": provenance.workspace_mode,
                "source_summary": provenance.source_summary,
            },
        }

    return {
        "status": "ok",
        "question": question,
        "answer": " ".join(answer_parts),
        "citations": citations[:4],
        "answer_context": {
            "workspace_mode": provenance.workspace_mode,
            "source_summary": provenance.source_summary,
        },
    }
