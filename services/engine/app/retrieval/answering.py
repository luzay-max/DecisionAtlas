from __future__ import annotations

from app.db.models import Decision
from app.indexing.embedder import Embedder
from app.outcomes.real_workspaces import build_imported_drift_status, build_imported_workspace_readiness
from app.provenance import get_workspace_provenance
from app.repositories.decisions import DecisionRepository
from app.repositories.drift_alerts import DriftAlertRepository
from app.repositories.import_jobs import ImportJobRepository
from app.repositories.source_refs import SourceRefRepository
from app.repositories.workspaces import WorkspaceRepository
from app.retrieval.hybrid import hybrid_search
from app.retrieval.query_rewrite import is_broad_why_query, rewrite_query, significant_query_terms
from sqlalchemy.orm import Session


def _decision_text(decision: Decision) -> str:
    return " ".join(
        part
        for part in [
            decision.title,
            decision.problem,
            decision.chosen_option,
            decision.tradeoffs,
            decision.context or "",
            decision.constraints or "",
        ]
        if part
    ).lower()


def _decision_query_overlap(decision: Decision, query_terms: list[str]) -> int:
    haystack = _decision_text(decision)
    return sum(1 for term in query_terms if term in haystack)


def _decision_topic_overlap(primary: Decision, secondary: Decision) -> int:
    primary_terms = set(significant_query_terms(_decision_text(primary)))
    secondary_terms = set(significant_query_terms(_decision_text(secondary)))
    return len(primary_terms.intersection(secondary_terms))


def _format_main_answer(decision: Decision) -> str:
    return f"{decision.title}: {decision.chosen_option} Tradeoffs: {decision.tradeoffs}"


def _format_supporting_answer(decision: Decision) -> str:
    return f"{decision.chosen_option} Tradeoffs: {decision.tradeoffs}"


def _build_answer_payload(
    *,
    status: str,
    question: str,
    answer: str,
    context: dict,
    citations: list[dict],
    primary_decision: Decision | None = None,
    supporting_context: list[dict] | None = None,
) -> dict:
    payload = {
        "status": status,
        "question": question,
        "answer": answer,
        "citations": citations,
        "answer_context": context,
    }
    if primary_decision is not None:
        payload["primary_decision"] = {
            "decision_id": primary_decision.id,
            "title": primary_decision.title,
        }
    if supporting_context is not None:
        payload["supporting_context"] = supporting_context
    return payload


def _pick_primary_and_supporting_decisions(
    *,
    decisions: DecisionRepository,
    hits: list,
    query: str,
) -> tuple[Decision | None, list[Decision]]:
    if not hits:
        return None, []

    query_terms = significant_query_terms(query)
    is_broad_query = is_broad_why_query(query)
    primary = decisions.get_by_id(hits[0].decision_id)
    if primary is None:
        return None, []

    primary_score = hits[0].score
    primary_overlap = max(_decision_query_overlap(primary, query_terms), 1)
    supporting: list[Decision] = []

    if not is_broad_query:
        return primary, supporting

    for hit in hits[1:3]:
        if hit.score < (primary_score * 0.75):
            continue
        candidate = decisions.get_by_id(hit.decision_id)
        if candidate is None:
            continue
        candidate_overlap = _decision_query_overlap(candidate, query_terms)
        topic_overlap = _decision_topic_overlap(primary, candidate)
        if candidate_overlap < 1:
            continue
        if topic_overlap < 1:
            continue
        supporting.append(candidate)
        break

    return primary, supporting


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
        return _build_answer_payload(
            status="insufficient_evidence",
            question=question,
            answer="Insufficient evidence. Review more artifacts or accept more decisions first.",
            context=context,
            citations=[],
        )

    source_refs = SourceRefRepository(session)
    primary_decision, supporting_decisions = _pick_primary_and_supporting_decisions(
        decisions=decisions,
        hits=hits,
        query=rewritten,
    )
    if primary_decision is None:
        return _build_answer_payload(
            status="insufficient_evidence",
            question=question,
            answer="Insufficient evidence. Review more artifacts or accept more decisions first.",
            context=context,
            citations=[],
        )

    citations = []
    for source_ref in source_refs.list_by_decision(primary_decision.id)[:2]:
        citations.append(
            {
                "decision_id": primary_decision.id,
                "source_ref_id": source_ref.id,
                "quote": source_ref.quote,
                "url": source_ref.url,
            }
        )

    supporting_context = []
    for decision in supporting_decisions:
        supporting_context.append(
            {
                "decision_id": decision.id,
                "title": decision.title,
                "answer": _format_supporting_answer(decision),
            }
        )
        if len(citations) >= 2:
            continue
        for source_ref in source_refs.list_by_decision(decision.id)[:2]:
            citations.append(
                {
                    "decision_id": decision.id,
                    "source_ref_id": source_ref.id,
                    "quote": source_ref.quote,
                    "url": source_ref.url,
                }
            )

    if not citations:
        return _build_answer_payload(
            status="insufficient_evidence",
            question=question,
            answer="Insufficient evidence. The matched decisions do not have enough supporting citations yet.",
            context=context,
            citations=[],
        )

    answer_status = "ok"
    if provenance.workspace_mode != "demo" and len(citations) < 2:
        answer_status = "limited_support"
    elif len(citations) < 2:
        return _build_answer_payload(
            status="insufficient_evidence",
            question=question,
            answer="Insufficient evidence. The matched decisions do not have enough supporting citations yet.",
            context=context,
            citations=citations,
            primary_decision=primary_decision,
            supporting_context=supporting_context,
        )

    answer_text = _format_main_answer(primary_decision)

    return _build_answer_payload(
        status=answer_status,
        question=question,
        answer=answer_text,
        context=context,
        citations=citations[:4],
        primary_decision=primary_decision,
        supporting_context=supporting_context,
    )
