from __future__ import annotations

import math

from app.db.models import Decision
from app.indexing.embedder import Embedder
from app.outcomes.real_workspaces import build_imported_drift_status, build_imported_workspace_readiness
from app.provenance import get_workspace_provenance
from app.repositories.artifact_chunks import ArtifactChunkRepository
from app.repositories.artifacts import ArtifactRepository
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


def _sentence(value: str | None, *, prefix: str | None = None) -> str:
    text = " ".join((value or "").split()).strip()
    if not text:
        return ""
    if prefix:
        text = f"{prefix}: {text}"
    return text if text.endswith((".", "!", "?")) else f"{text}."


def _format_main_answer(decision: Decision, *, supporting_evidence: str | None = None) -> str:
    parts = [
        _sentence(f"{decision.title}: {decision.chosen_option}"),
        _sentence(decision.problem, prefix="Problem"),
        _sentence(decision.tradeoffs, prefix="Tradeoffs"),
    ]
    if supporting_evidence:
        parts.append(_sentence(supporting_evidence, prefix="Supporting evidence"))
    return " ".join(part for part in parts if part)


def _format_supporting_answer(decision: Decision) -> str:
    parts = [_sentence(decision.chosen_option), _sentence(decision.tradeoffs, prefix="Tradeoffs")]
    return " ".join(part for part in parts if part)


def _normalize_quote(text: str) -> str:
    return " ".join(text.lower().split())


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm <= 0 or right_norm <= 0:
        return 0.0
    return dot / (left_norm * right_norm)


def _supporting_decision_terms(decision: Decision) -> set[str]:
    return set(significant_query_terms(" ".join(filter(None, [decision.title, decision.problem, decision.chosen_option]))))


def _artifact_supporting_terms(title: str | None) -> set[str]:
    return set(significant_query_terms(title or ""))


def _chunk_structural_terms(chunk) -> tuple[set[str], set[str]]:
    metadata = chunk.metadata_json if isinstance(chunk.metadata_json, dict) else {}
    heading_path = metadata.get("heading_path") or []
    if not isinstance(heading_path, list):
        heading_path = []
    section_title = metadata.get("section_title") or ""
    return (
        set(significant_query_terms(" ".join(str(item) for item in heading_path if item))),
        set(significant_query_terms(str(section_title))),
    )


def _chunk_structural_bonus(chunk, *, query_terms: set[str], decision_terms: set[str]) -> float:
    metadata = chunk.metadata_json if isinstance(chunk.metadata_json, dict) else {}
    heading_terms, section_terms = _chunk_structural_terms(chunk)
    heading_overlap = len(heading_terms.intersection(query_terms | decision_terms))
    section_overlap = len(section_terms.intersection(query_terms | decision_terms))
    chunk_role = str(metadata.get("chunk_role") or "")
    boundary_kind = str(metadata.get("boundary_kind") or "")

    bonus = (heading_overlap * 2.0) + (section_overlap * 1.5)
    if chunk_role == "section":
        bonus += 0.4
    if boundary_kind == "structured_section":
        bonus += 0.6
    return bonus


def _chunk_supporting_citations(
    *,
    session: Session,
    embedder: Embedder,
    decision: Decision,
    query: str,
    existing_quotes: set[str],
    artifact_ids: list[int],
    limit: int,
) -> list[dict]:
    if not artifact_ids or limit <= 0:
        return []

    chunk_repository = ArtifactChunkRepository(session)
    artifact_repository = ArtifactRepository(session)
    chunks = chunk_repository.list_for_artifacts(artifact_ids)
    if not chunks:
        return []

    query_embedding = embedder.embed([query])[0]
    query_terms = set(significant_query_terms(query))
    decision_terms = _supporting_decision_terms(decision)
    chunk_texts_to_embed: list[str] = []
    chunk_indices_to_embed: list[int] = []
    chunk_embeddings: dict[int, list[float]] = {}

    for index, chunk in enumerate(chunks):
        if chunk.embedding:
            chunk_embeddings[index] = [float(value) for value in chunk.embedding]
        else:
            chunk_texts_to_embed.append(chunk.content)
            chunk_indices_to_embed.append(index)

    if chunk_texts_to_embed:
        for index, embedding in zip(chunk_indices_to_embed, embedder.embed(chunk_texts_to_embed)):
            chunk_embeddings[index] = embedding

    ranked_chunks: list[tuple[float, dict]] = []
    for index, chunk in enumerate(chunks):
        content = " ".join(chunk.content.split()).strip()
        if len(content) < 24:
            continue
        normalized_content = _normalize_quote(content)
        if normalized_content in existing_quotes:
            continue

        lowered = content.lower()
        query_overlap = sum(1 for term in query_terms if term in lowered)
        decision_overlap = sum(1 for term in decision_terms if term in lowered)
        if query_overlap == 0 and decision_overlap < 2:
            continue

        artifact = artifact_repository.get_by_id(chunk.artifact_id)
        if artifact is None:
            continue

        artifact_overlap = sum(1 for term in _artifact_supporting_terms(artifact.title) if term in lowered)
        if query_overlap == 0 and (decision_overlap + artifact_overlap) < 2:
            continue

        score = (query_overlap * 3.0) + float(decision_overlap)
        score += artifact_overlap * 1.5
        score += _chunk_structural_bonus(chunk, query_terms=query_terms, decision_terms=decision_terms)
        score += _cosine_similarity(query_embedding, chunk_embeddings.get(index, []))
        ranked_chunks.append(
            (
                score,
                {
                    "decision_id": decision.id,
                    "quote": content,
                    "url": artifact.url,
                },
            )
        )

    ranked_chunks.sort(key=lambda item: item[0], reverse=True)
    citations: list[dict] = []
    for _, citation in ranked_chunks:
        normalized_quote = _normalize_quote(citation["quote"])
        if normalized_quote in existing_quotes:
            continue
        citations.append(citation)
        existing_quotes.add(normalized_quote)
        if len(citations) >= limit:
            break
    return citations


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
    recent_sync_jobs = ImportJobRepository(session).list_recent_for_workspace(workspace.id, limit=5)
    workspace_readiness = (
        build_imported_workspace_readiness(
            latest_import_status=latest_job.status if latest_job is not None else None,
            latest_import_summary=latest_job.summary_json if latest_job is not None else None,
            latest_import=latest_job,
            recent_sync_jobs=recent_sync_jobs,
            decision_counts=decision_counts,
            drift_status=drift_status,
            access_source_type=workspace.access_source_type,
            access_source_ref=workspace.access_source_ref,
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
    primary_source_refs = source_refs.list_by_decision(primary_decision.id)
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

    if len(citations) < 2:
        existing_quotes = {_normalize_quote(citation["quote"]) for citation in citations}
        primary_artifact_ids = list(dict.fromkeys(source_ref.artifact_id for source_ref in primary_source_refs))
        citations.extend(
            _chunk_supporting_citations(
                session=session,
                embedder=embedder,
                decision=primary_decision,
                query=rewritten,
                existing_quotes=existing_quotes,
                artifact_ids=primary_artifact_ids,
                limit=2 - len(citations),
            )
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

    answer_text = _format_main_answer(primary_decision, supporting_evidence=citations[0]["quote"] if citations else None)

    return _build_answer_payload(
        status=answer_status,
        question=question,
        answer=answer_text,
        context=context,
        citations=citations[:4],
        primary_decision=primary_decision,
        supporting_context=supporting_context,
    )
