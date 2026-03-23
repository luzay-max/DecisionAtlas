from __future__ import annotations

from app.indexing.embedder import Embedder
from app.outcomes.real_workspaces import build_imported_drift_status, build_imported_workspace_readiness
from app.provenance import get_workspace_provenance
from app.repositories.decisions import DecisionRepository
from app.repositories.drift_alerts import DriftAlertRepository
from app.repositories.import_jobs import ImportJobRepository
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
    decisions = DecisionRepository(session)
    decision_counts = decisions.counts_by_review_state(workspace.id)
    latest_job = ImportJobRepository(session).latest_for_workspace(workspace.id)
    accepted_decisions = decisions.list_by_review_state(workspace.id, "accepted")
    drift_status = build_imported_drift_status(
        candidate_count=decision_counts.get("candidate", 0),
        accepted_count=decision_counts.get("accepted", 0),
        latest_import_finished_at=latest_job.finished_at if latest_job is not None else None,
        latest_accepted_change_at=max((decision.updated_at for decision in accepted_decisions), default=None),
        latest_import_summary=latest_job.summary_json if latest_job is not None else None,
        alert_count=len(DriftAlertRepository(session).list_recent_by_workspace(workspace.id)),
    )
    workspace_readiness = (
        build_imported_workspace_readiness(
            latest_import_status=latest_job.status if latest_job is not None else None,
            latest_import_summary=latest_job.summary_json if latest_job is not None else None,
            decision_counts=decision_counts,
            drift_status=drift_status,
        )
        if provenance.workspace_mode != "demo"
        else None
    )
    context = {
        "workspace_mode": provenance.workspace_mode,
        "source_summary": provenance.source_summary,
        "workspace_readiness": workspace_readiness,
    }
    if provenance.workspace_mode != "demo" and decision_counts.get("accepted", 0) == 0:
        status = "review_required" if decision_counts.get("candidate", 0) > 0 else "evidence_limited"
        answer = (
            "Accepted imported decisions are required before why-search is trustworthy. Review candidate decisions first."
            if status == "review_required"
            else "This imported workspace does not yet have enough accepted decision evidence for a trustworthy why-answer."
        )
        return {
            "status": status,
            "question": question,
            "answer": answer,
            "citations": [],
            "answer_context": context,
        }
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
            "answer_context": context,
        }

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
            "answer_context": context,
        }

    return {
        "status": "ok",
        "question": question,
        "answer": " ".join(answer_parts),
        "citations": citations[:4],
        "answer_context": context,
    }
