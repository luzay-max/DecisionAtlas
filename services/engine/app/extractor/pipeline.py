from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from time import monotonic
from typing import Callable
import re

from app.extractor.parser import ParsedDecision, parse_extraction_response
from app.extractor.prompt_loader import load_prompt
from app.llm.base import (
    DecisionScreeningRequest,
    ExtractionProvider,
    ExtractionRequest,
    ProviderRequestError,
    ProviderTimeoutError,
)
from app.repositories.artifacts import ArtifactRepository
from app.repositories.decisions import DecisionRepository
from app.repositories.source_refs import SourceRefRepository
from app.repositories.workspaces import WorkspaceRepository
from sqlalchemy.orm import Session


SIGNAL_WORDS = (
    "decide",
    "decision",
    "tradeoff",
    "trade-off",
    "chose",
    "because",
    "why",
    "rationale",
    "migration",
    "rollout",
    "deprecat",
    "architecture",
    "cache only",
    "must ",
    "should ",
    "adopt",
    "replace",
)
TITLE_SIGNAL_WORDS = (
    "decision",
    "architecture",
    "migration",
    "rollout",
    "release",
    "deprecation",
    "rfc",
    "adr",
    "proposal",
)
PATH_SIGNAL_WORDS = (
    "decision",
    "architecture",
    "migration",
    "rollout",
    "release",
    "deprecation",
    "rfc",
    "adr",
    "runbook",
    "operat",
    "design",
)
STRONG_DOCUMENT_CATEGORIES = {
    "adr",
    "rfc",
    "architecture",
    "migration",
    "rollout",
    "release",
    "operations",
    "deprecation",
}
GENERIC_TITLE_WORDS = ("readme", "chore", "docs", "typo", "cleanup", "format")
MAX_SCREENING_ARTIFACT_CHARS = 2400
MAX_EXTRACTION_ARTIFACT_CHARS = 5000
MAX_RECOVERY_ARTIFACT_CHARS = 3200
MAX_SHORTLIST_ARTIFACTS = 80
MIN_EXTRACTION_SIGNAL_SCORE = 4
MAX_FULL_EXTRACTION_CONCURRENCY = 3
MAX_RELEVANT_BLOCKS = 6
MAX_RECOVERY_FRAGMENTS = 6
MAX_SPARSE_RECOVERY_ARTIFACTS = 4
MIN_SPARSE_RECOVERY_SIGNAL_SCORE = 4
DOC_SIGNAL_CATEGORY_FAMILIES = {
    "adr": "adr_doc",
    "rfc": "rfc_doc",
    "architecture": "architecture_doc",
    "migration": "migration_doc",
    "rollout": "rollout_doc",
    "release": "release_doc",
    "operations": "operations_doc",
    "deprecation": "deprecation_doc",
}
EXTRACTION_FAMILY_PROMPTS = {
    "rationale_doc": "decision-extraction-rationale-doc",
    "adr_doc": "decision-extraction-rationale-doc",
    "rfc_doc": "decision-extraction-rationale-doc",
    "architecture_doc": "decision-extraction-rationale-doc",
    "migration_doc": "decision-extraction-rationale-doc",
    "rollout_doc": "decision-extraction-rationale-doc",
    "release_doc": "decision-extraction-rationale-doc",
    "operations_doc": "decision-extraction-rationale-doc",
    "deprecation_doc": "decision-extraction-rationale-doc",
    "pull_request": "decision-extraction-pull-request",
    "lightweight_evidence": "decision-extraction-lightweight-evidence",
}
RECOVERABLE_LOSS_REASONS = {
    "null_decision",
    "invalid_json",
    "missing_required_fields",
    "ungrounded_quote",
    "provider_request_failed",
}


@dataclass(slots=True)
class _RankedArtifact:
    score: int
    artifact_id: int
    artifact: object


@dataclass(slots=True)
class _CompletedExtraction:
    artifact: object
    family: str
    raw_response: str | None = None
    timeout: bool = False
    request_400: bool = False
    request_error: bool = False
    latency_ms: int = 0
    recovery: bool = False
    sparse_recovery: bool = False


@dataclass(slots=True)
class _ExtractionEvaluation:
    decision: ParsedDecision | None = None
    grounded_quotes: list[tuple[int, int, str]] = field(default_factory=list)
    loss_reason: str | None = None
    salvaged: bool = False
    recoverable: bool = False


@dataclass(slots=True)
class ExtractionRunStats:
    shortlisted_artifacts: int = 0
    screened_artifacts: int = 0
    screened_in_artifacts: int = 0
    screened_out_artifacts: int = 0
    full_extraction_requests: int = 0
    completed_full_extractions: int = 0
    recovery_extraction_attempts: int = 0
    total_artifacts: int = 0
    processed_artifacts: int = 0
    created_candidates: int = 0
    salvaged_candidates: int = 0
    recovered_candidates: int = 0
    thin_source_ref_decisions: int = 0
    skipped_provider_400: int = 0
    skipped_provider_timeout: int = 0
    skipped_invalid_json: int = 0
    selected_extraction_families: dict[str, int] = field(default_factory=dict)
    conversion_loss_reasons: dict[str, int] = field(default_factory=dict)
    sparse_recovery_status: str = "not_evaluated"
    sparse_recovery_skip_reason: str | None = None
    sparse_recovery_eligible_artifacts: int = 0
    sparse_recovery_attempted_artifacts: int = 0
    sparse_recovery_model_attempts: int = 0
    sparse_recovery_recovered_candidates: int = 0
    sparse_recovery_evidence_families: dict[str, int] = field(default_factory=dict)
    sparse_recovery_rejection_reasons: dict[str, int] = field(default_factory=dict)
    elapsed_seconds: int | None = None
    estimated_remaining_seconds: int | None = None
    average_full_extraction_latency_ms: int | None = None
    current_artifact_title: str | None = None
    current_phase: str | None = None
    current_extraction_family: str | None = None

    def to_summary(self) -> dict[str, int | str | None]:
        return asdict(self)


def _count_signal_hits(content: str) -> int:
    lowered = content.lower()
    return sum(1 for token in SIGNAL_WORDS if token in lowered)


def _artifact_signal_score(artifact) -> int:
    score = 0
    content = artifact.content or ""
    lowered_title = (artifact.title or "").lower()
    metadata = artifact.metadata_json or {}
    path = str(metadata.get("path", "")).lower()
    signal_category = str(metadata.get("signal_category", "")).lower()
    signal_hits = _count_signal_hits(content)

    score += min(signal_hits, 3)
    if artifact.type == "doc":
        score += 3
    elif artifact.type == "pr":
        score += 2
    elif artifact.type == "issue":
        score += 1

    if signal_category in STRONG_DOCUMENT_CATEGORIES:
        score += 3
    if any(token in lowered_title for token in TITLE_SIGNAL_WORDS):
        score += 3
    if any(token in path for token in PATH_SIGNAL_WORDS):
        score += 2
    if "we decided" in content.lower() or "decision:" in content.lower():
        score += 2

    if artifact.type == "commit" and len(content.strip()) < 280:
        score -= 3
    if artifact.type == "issue" and len(content.strip()) < 220:
        score -= 1
    if path.endswith("readme.md") and score < 7:
        score -= 3
    if any(token == lowered_title.strip() or lowered_title.startswith(f"{token}:") for token in GENERIC_TITLE_WORDS):
        score -= 2

    return score


def _find_span(content: str, quote: str) -> tuple[int | None, int | None]:
    if not quote:
        return None, None
    start = content.find(quote)
    if start == -1:
        return None, None
    return start, start + len(quote)


def _tokenize_signal_terms(*parts: str | None) -> list[str]:
    tokens: list[str] = []
    for part in parts:
        if not part:
            continue
        for token in re.findall(r"[a-z0-9_]{4,}", part.lower()):
            if token not in tokens:
                tokens.append(token)
    return tokens


def _candidate_support_quotes(content: str, parsed_decision) -> list[str]:
    candidates = list(parsed_decision.source_quotes)
    if len(candidates) >= 2:
        return candidates

    signal_terms = _tokenize_signal_terms(
        parsed_decision.problem,
        parsed_decision.chosen_option,
        parsed_decision.tradeoffs,
        parsed_decision.context,
        parsed_decision.constraints,
    )
    if not signal_terms:
        return candidates

    blocks = [block.strip() for block in re.split(r"\n\s*\n", content) if block.strip()]
    snippets: list[tuple[int, str]] = []
    existing = {quote.casefold() for quote in candidates}
    for block in blocks:
        fragments = [fragment.strip() for fragment in re.split(r"(?<=[.!?])\s+", block) if fragment.strip()]
        for fragment in fragments or [block]:
            lowered = fragment.lower()
            if len(fragment) < 30 or len(fragment) > 280:
                continue
            if lowered.casefold() in existing:
                continue
            overlap = sum(1 for token in signal_terms if token in lowered)
            if overlap < 2:
                continue
            snippets.append((overlap, fragment))

    for _, snippet in sorted(snippets, key=lambda item: (-item[0], len(item[1])))[:3]:
        key = snippet.casefold()
        if key in existing:
            continue
        existing.add(key)
        candidates.append(snippet)
        if len(candidates) >= 3:
            break

    return candidates


def _ground_quotes(content: str, quotes: list[str]) -> list[tuple[int, int, str]]:
    grounded: list[tuple[int, int, str]] = []
    seen_spans: set[tuple[int, int]] = set()
    for quote in quotes:
        span_start, span_end = _find_span(content, quote)
        if span_start is None or span_end is None:
            continue
        span = (span_start, span_end)
        if span in seen_spans:
            continue
        seen_spans.add(span)
        grounded.append((span_start, span_end, quote))
    return grounded


def _prepare_screening_content(artifact) -> str:
    return _prepare_relevant_content(artifact, max_chars=MAX_SCREENING_ARTIFACT_CHARS, include_signal_only=False)


def _prepare_extraction_content(artifact) -> str:
    return _prepare_relevant_content(artifact, max_chars=MAX_EXTRACTION_ARTIFACT_CHARS, include_signal_only=True)


def _prepare_recovery_content(artifact) -> str:
    return _prepare_relevant_content(
        artifact,
        max_chars=MAX_RECOVERY_ARTIFACT_CHARS,
        include_signal_only=True,
        prefer_quote_fragments=True,
    )


def _classify_extraction_family(artifact) -> str:
    metadata = artifact.metadata_json or {}
    path = str(metadata.get("path", "")).lower()
    lowered_title = (artifact.title or "").lower()

    if artifact.type == "doc":
        signal_category = str(metadata.get("signal_category", "")).lower()
        if signal_category in DOC_SIGNAL_CATEGORY_FAMILIES:
            return DOC_SIGNAL_CATEGORY_FAMILIES[signal_category]
        if "adr" in lowered_title or "/adr" in path or path.startswith("adr/"):
            return "adr_doc"
        if "rfc" in lowered_title or "/rfc" in path or path.startswith("rfc/"):
            return "rfc_doc"
        if "architecture" in lowered_title or "architecture" in path:
            return "architecture_doc"
        if "migration" in lowered_title or "migration" in path:
            return "migration_doc"
        if "rollout" in lowered_title or "rollout" in path:
            return "rollout_doc"
        if "release" in lowered_title or "release" in path or "changelog" in lowered_title or "changelog" in path:
            return "release_doc"
        if "operation" in lowered_title or "runbook" in path or "operat" in path:
            return "operations_doc"
        if "deprecat" in lowered_title or "deprecat" in path:
            return "deprecation_doc"
        return "rationale_doc"
    if artifact.type == "pr":
        return "pull_request"
    return "lightweight_evidence"


def _is_sparse_recovery_eligible(ranked: _RankedArtifact) -> bool:
    artifact = ranked.artifact
    if ranked.score < MIN_SPARSE_RECOVERY_SIGNAL_SCORE:
        return False
    content = artifact.content or ""
    metadata = artifact.metadata_json or {}
    signal_category = str(metadata.get("signal_category", "")).lower()
    explicit_signal = _count_signal_hits(content) >= 2
    strong_document = artifact.type == "doc" and signal_category in STRONG_DOCUMENT_CATEGORIES
    titled_signal = any(token in (artifact.title or "").lower() for token in TITLE_SIGNAL_WORDS)
    return explicit_signal or strong_document or titled_signal


def _select_sparse_recovery_artifacts(
    ranked_artifacts: list[_RankedArtifact],
    *,
    excluded_artifact_ids: set[int],
    max_artifacts: int,
) -> list[object]:
    if max_artifacts <= 0:
        return []
    eligible = [
        ranked
        for ranked in ranked_artifacts
        if ranked.artifact_id not in excluded_artifact_ids and _is_sparse_recovery_eligible(ranked)
    ]
    selected: list[_RankedArtifact] = []
    selected_ids: set[int] = set()
    seen_families: set[str] = set()
    for ranked in eligible:
        family = _classify_extraction_family(ranked.artifact)
        if family in seen_families:
            continue
        selected.append(ranked)
        selected_ids.add(ranked.artifact_id)
        seen_families.add(family)
        if len(selected) >= max_artifacts:
            break
    if len(selected) < max_artifacts:
        for ranked in eligible:
            if ranked.artifact_id in selected_ids:
                continue
            selected.append(ranked)
            selected_ids.add(ranked.artifact_id)
            if len(selected) >= max_artifacts:
                break
    return [ranked.artifact for ranked in selected]

def _prepare_relevant_content(
    artifact,
    *,
    max_chars: int,
    include_signal_only: bool,
    prefer_quote_fragments: bool = False,
) -> str:
    content = (artifact.content or "").strip()
    path = str((artifact.metadata_json or {}).get("path", "")).strip()
    header_parts = [
        f"Artifact title: {artifact.title or 'Untitled'}",
        f"Artifact type: {artifact.type}",
    ]
    if path:
        header_parts.append(f"Artifact path: {path}")
    header = "\n".join(header_parts)
    if not content:
        return header

    blocks = [block.strip() for block in re.split(r"\n\s*\n", content) if block.strip()]
    if not blocks:
        return f"{header}\n\n{content[:max_chars]}"

    scored_blocks: list[tuple[int, int]] = []
    for index, block in enumerate(blocks):
        block_score = _section_signal_score(block)
        if block_score > 0 or not include_signal_only:
            scored_blocks.append((block_score, index))

    if not scored_blocks:
        selected_indices = list(range(min(3, len(blocks))))
    else:
        top_blocks = sorted(scored_blocks, key=lambda item: (-item[0], item[1]))[:MAX_RELEVANT_BLOCKS]
        selected: set[int] = set()
        for _, index in top_blocks:
            selected.add(index)
            if index + 1 < len(blocks) and len(blocks[index]) < 500:
                selected.add(index + 1)
        selected_indices = sorted(selected)

    remaining = max_chars - len(header) - 2
    selected_blocks = [blocks[index] for index in selected_indices]
    sections: list[str] = []
    if prefer_quote_fragments:
        fragment_header = "Potential decision evidence:"
        remaining -= len(fragment_header) + 2
        fragments = _select_recovery_fragments(selected_blocks)
        if fragments:
            sections.append(fragment_header)
            for fragment in fragments:
                candidate = f"- {fragment}"
                if len(candidate) > remaining:
                    candidate = candidate[:remaining].rstrip()
                if not candidate:
                    continue
                sections.append(candidate)
                remaining -= len(candidate) + 1
                if remaining <= 0:
                    break

    if not sections:
        remaining = max_chars - len(header) - 2
        for block in selected_blocks:
            candidate = block if len(block) <= remaining else block[:remaining].rstrip()
            if not candidate:
                continue
            sections.append(candidate)
            remaining -= len(candidate) + 2
            if remaining <= 0:
                break

    if not sections:
        sections = [content[: max(remaining, 0) or max_chars].rstrip()]

    payload = f"{header}\n\n" + "\n\n".join(sections)
    if len(payload) <= max_chars:
        return payload
    return payload[:max_chars].rstrip()


def _section_signal_score(block: str) -> int:
    lowered = block.lower()
    score = min(_count_signal_hits(block), 4)
    if block.lstrip().startswith("#"):
        score += 1
    if any(token in lowered for token in TITLE_SIGNAL_WORDS):
        score += 1
    if "we decided" in lowered or "because" in lowered:
        score += 1
    return score


def _fragment_signal_score(fragment: str) -> int:
    lowered = fragment.lower()
    score = min(_count_signal_hits(fragment), 4)
    if "we decided" in lowered or "decision:" in lowered:
        score += 2
    if "because" in lowered:
        score += 2
    if "tradeoff" in lowered or "trade-off" in lowered:
        score += 1
    if "must " in lowered or "should " in lowered:
        score += 1
    return score


def _select_recovery_fragments(blocks: list[str]) -> list[str]:
    ranked: list[tuple[int, str]] = []
    seen: set[str] = set()
    for block in blocks:
        fragments = [fragment.strip() for fragment in re.split(r"(?<=[.!?])\s+", block) if fragment.strip()]
        for fragment in fragments or [block]:
            if len(fragment) < 30 or len(fragment) > 280:
                continue
            score = _fragment_signal_score(fragment)
            if score <= 0:
                continue
            key = fragment.casefold()
            if key in seen:
                continue
            seen.add(key)
            ranked.append((score, fragment))

    return [fragment for _, fragment in sorted(ranked, key=lambda item: (-item[0], len(item[1])))[:MAX_RECOVERY_FRAGMENTS]]


class CandidateExtractionPipeline:
    def __init__(
        self,
        session: Session,
        provider: ExtractionProvider,
        *,
        sparse_recovery_max_artifacts: int = MAX_SPARSE_RECOVERY_ARTIFACTS,
    ) -> None:
        self.session = session
        self.provider = provider
        self.sparse_recovery_max_artifacts = max(0, sparse_recovery_max_artifacts)
        self.workspaces = WorkspaceRepository(session)
        self.artifacts = ArtifactRepository(session)
        self.decisions = DecisionRepository(session)
        self.source_refs = SourceRefRepository(session)
        self.last_run_stats = ExtractionRunStats()

    def _persist_candidate(
        self,
        *,
        workspace_id: int,
        completed: _CompletedExtraction,
        evaluation: _ExtractionEvaluation,
        stats: ExtractionRunStats,
    ) -> None:
        if evaluation.decision is None:
            raise ValueError("Cannot persist an extraction without a decision")
        decision = self.decisions.create_candidate(
            workspace_id=workspace_id,
            title=evaluation.decision.title,
            problem=evaluation.decision.problem,
            context=evaluation.decision.context,
            constraints=evaluation.decision.constraints,
            chosen_option=evaluation.decision.chosen_option,
            tradeoffs=evaluation.decision.tradeoffs,
            confidence=evaluation.decision.confidence,
        )
        for span_start, span_end, quote in evaluation.grounded_quotes:
            self.source_refs.create(
                decision_id=decision.id,
                artifact_id=completed.artifact.id,
                span_start=span_start,
                span_end=span_end,
                quote=quote,
                url=completed.artifact.url,
                relevance_score=evaluation.decision.confidence,
            )
        stats.created_candidates += 1
        if evaluation.salvaged:
            stats.salvaged_candidates += 1
        if completed.recovery:
            stats.recovered_candidates += 1
        if completed.sparse_recovery:
            stats.sparse_recovery_recovered_candidates += 1
        if len(evaluation.grounded_quotes) == 1:
            stats.thin_source_ref_decisions += 1
            _record_conversion_loss(stats, "thin_source_ref_coverage")

    def run(
        self,
        *,
        workspace_slug: str,
        progress_callback: Callable[[ExtractionRunStats], None] | None = None,
    ) -> int:
        workspace = self.workspaces.get_by_slug(workspace_slug)
        if workspace is None:
            raise ValueError(f"Workspace not found: {workspace_slug}")

        screening_prompt = load_prompt("decision-screening")
        extraction_prompts = {
            family: load_prompt(prompt_name)
            for family, prompt_name in EXTRACTION_FAMILY_PROMPTS.items()
        }
        ranked_artifacts = sorted(
            (
                _RankedArtifact(score=_artifact_signal_score(artifact), artifact_id=artifact.id, artifact=artifact)
                for artifact in self.artifacts.list_by_workspace(workspace.id)
            ),
            key=lambda item: (-item.score, item.artifact_id),
        )
        shortlisted_artifacts = [
            ranked.artifact
            for ranked in ranked_artifacts
            if ranked.score >= MIN_EXTRACTION_SIGNAL_SCORE and not self.source_refs.exists_for_artifact(ranked.artifact.id)
        ][:MAX_SHORTLIST_ARTIFACTS]
        stats = ExtractionRunStats(
            shortlisted_artifacts=len(shortlisted_artifacts),
            total_artifacts=len(shortlisted_artifacts),
            current_phase="screening",
        )
        started_at = monotonic()
        latency_total_ms = 0
        _update_progress(stats, started_at)
        if progress_callback is not None:
            progress_callback(stats)

        screened_positive: list[tuple[object, str, str, str]] = []
        for artifact in shortlisted_artifacts:
            stats.current_artifact_title = artifact.title
            stats.current_extraction_family = None
            try:
                decision_like = self.provider.screen_decision_likeness(
                    DecisionScreeningRequest(
                        artifact_id=artifact.id,
                        artifact_title=artifact.title,
                        artifact_content=_prepare_screening_content(artifact),
                        prompt=screening_prompt,
                    )
                )
            except ProviderTimeoutError:
                stats.skipped_provider_timeout += 1
                stats.screened_out_artifacts += 1
            except ProviderRequestError as error:
                if "status 400" in str(error):
                    stats.skipped_provider_400 += 1
                    stats.screened_out_artifacts += 1
                else:
                    raise
            else:
                if decision_like:
                    family = _classify_extraction_family(artifact)
                    stats.selected_extraction_families[family] = stats.selected_extraction_families.get(family, 0) + 1
                    screened_positive.append(
                        (
                            artifact,
                            _prepare_extraction_content(artifact),
                            family,
                            extraction_prompts[family],
                        )
                    )
                    stats.screened_in_artifacts += 1
                else:
                    stats.screened_out_artifacts += 1
            finally:
                stats.screened_artifacts += 1
                _refresh_work_totals(stats)
                _update_progress(stats, started_at)
                if progress_callback is not None:
                    progress_callback(stats)

        stats.current_phase = "extracting"
        _refresh_work_totals(stats)
        _update_progress(stats, started_at)
        if progress_callback is not None:
            progress_callback(stats)

        full_extraction_artifact_ids: set[int] = set()
        futures: dict[object, object] = {}
        with ThreadPoolExecutor(max_workers=MAX_FULL_EXTRACTION_CONCURRENCY) as executor:
            for artifact, payload, family, prompt in screened_positive:
                full_extraction_artifact_ids.add(artifact.id)
                stats.full_extraction_requests += 1
                stats.current_artifact_title = artifact.title
                stats.current_extraction_family = family
                futures[
                    executor.submit(
                        _run_full_extraction,
                        artifact,
                        family,
                        self.provider,
                        ExtractionRequest(
                            artifact_id=artifact.id,
                            artifact_title=artifact.title,
                            artifact_content=payload,
                            prompt=prompt,
                            artifact_family=family,
                        ),
                    )
                ] = artifact
                _refresh_work_totals(stats)

            for future in as_completed(futures):
                completed = future.result()
                latency_total_ms = _accumulate_completed_attempt(stats, latency_total_ms, completed)
                evaluation = _evaluate_extraction_attempt(completed)

                if _should_retry_conversion(completed, evaluation):
                    stats.recovery_extraction_attempts += 1
                    stats.full_extraction_requests += 1
                    stats.current_artifact_title = completed.artifact.title
                    recovery = _run_recovery_extraction(
                        completed.artifact,
                        completed.family,
                        self.provider,
                        extraction_prompts,
                    )
                    latency_total_ms = _accumulate_completed_attempt(stats, latency_total_ms, recovery)
                    evaluation = _evaluate_extraction_attempt(recovery)
                    completed = recovery

                if evaluation.decision is None:
                    _record_attempt_failure_counters(stats, completed, evaluation)
                    _record_conversion_loss(stats, evaluation.loss_reason or "null_decision")
                else:
                    self._persist_candidate(
                        workspace_id=workspace.id,
                        completed=completed,
                        evaluation=evaluation,
                        stats=stats,
                    )
                _refresh_work_totals(stats)
                _update_progress(stats, started_at)
                if progress_callback is not None:
                    progress_callback(stats)

        if stats.created_candidates > 0:
            stats.sparse_recovery_status = "skipped"
            stats.sparse_recovery_skip_reason = "candidate_present"
        elif self.sparse_recovery_max_artifacts <= 0:
            stats.sparse_recovery_status = "skipped"
            stats.sparse_recovery_skip_reason = "disabled_budget"
        else:
            excluded_artifact_ids = set(full_extraction_artifact_ids)
            excluded_artifact_ids.update(
                ranked.artifact_id
                for ranked in ranked_artifacts
                if self.source_refs.exists_for_artifact(ranked.artifact_id)
            )
            sparse_artifacts = _select_sparse_recovery_artifacts(
                ranked_artifacts,
                excluded_artifact_ids=excluded_artifact_ids,
                max_artifacts=self.sparse_recovery_max_artifacts,
            )
            stats.sparse_recovery_eligible_artifacts = len(sparse_artifacts)
            if not sparse_artifacts:
                stats.sparse_recovery_status = "skipped"
                stats.sparse_recovery_skip_reason = "no_eligible_evidence"
            else:
                stats.sparse_recovery_status = "attempted"
                stats.current_phase = "sparse_recovery"
                for artifact in sparse_artifacts:
                    family = _classify_extraction_family(artifact)
                    stats.sparse_recovery_attempted_artifacts += 1
                    stats.sparse_recovery_model_attempts += 1
                    stats.recovery_extraction_attempts += 1
                    stats.full_extraction_requests += 1
                    stats.sparse_recovery_evidence_families[family] = (
                        stats.sparse_recovery_evidence_families.get(family, 0) + 1
                    )
                    stats.current_artifact_title = artifact.title
                    stats.current_extraction_family = family
                    completed = _run_recovery_extraction(
                        artifact,
                        family,
                        self.provider,
                        extraction_prompts,
                    )
                    completed.sparse_recovery = True
                    latency_total_ms = _accumulate_completed_attempt(stats, latency_total_ms, completed)
                    evaluation = _evaluate_extraction_attempt(completed)
                    if evaluation.decision is None:
                        reason = evaluation.loss_reason or "null_decision"
                        _record_attempt_failure_counters(stats, completed, evaluation)
                        _record_conversion_loss(stats, reason)
                        stats.sparse_recovery_rejection_reasons[reason] = (
                            stats.sparse_recovery_rejection_reasons.get(reason, 0) + 1
                        )
                    else:
                        self._persist_candidate(
                            workspace_id=workspace.id,
                            completed=completed,
                            evaluation=evaluation,
                            stats=stats,
                        )
                        stats.sparse_recovery_status = "recovered"
                        stats.sparse_recovery_skip_reason = None
                        _refresh_work_totals(stats)
                        _update_progress(stats, started_at)
                        if progress_callback is not None:
                            progress_callback(stats)
                        break
                    _refresh_work_totals(stats)
                    _update_progress(stats, started_at)
                    if progress_callback is not None:
                        progress_callback(stats)
                if stats.sparse_recovery_recovered_candidates == 0:
                    stats.sparse_recovery_status = "exhausted"
                    stats.sparse_recovery_skip_reason = "all_attempts_rejected"
        stats.current_artifact_title = None
        stats.current_phase = "completed"
        stats.current_extraction_family = None
        _refresh_work_totals(stats)
        _update_progress(stats, started_at)
        if progress_callback is not None:
            progress_callback(stats)

        self.session.commit()
        self.last_run_stats = stats
        return stats.created_candidates


def _run_full_extraction(artifact, family: str, provider: ExtractionProvider, request: ExtractionRequest) -> _CompletedExtraction:
    started_at = monotonic()
    try:
        raw_response = provider.extract_candidate(request)
    except ProviderTimeoutError:
        return _CompletedExtraction(
            artifact=artifact,
            family=family,
            timeout=True,
            latency_ms=max(1, round((monotonic() - started_at) * 1000)),
        )
    except ProviderRequestError as error:
        if "status 400" in str(error):
            return _CompletedExtraction(
                artifact=artifact,
                family=family,
                request_400=True,
                latency_ms=max(1, round((monotonic() - started_at) * 1000)),
            )
        return _CompletedExtraction(
            artifact=artifact,
            family=family,
            request_error=True,
            latency_ms=max(1, round((monotonic() - started_at) * 1000)),
        )
    return _CompletedExtraction(
        artifact=artifact,
        family=family,
        raw_response=raw_response,
        latency_ms=max(1, round((monotonic() - started_at) * 1000)),
    )


def _run_recovery_extraction(
    artifact,
    primary_family: str,
    provider: ExtractionProvider,
    extraction_prompts: dict[str, str],
) -> _CompletedExtraction:
    recovery_family = _classify_recovery_family(artifact, primary_family)
    request = ExtractionRequest(
        artifact_id=artifact.id,
        artifact_title=artifact.title,
        artifact_content=_prepare_recovery_content(artifact),
        prompt=extraction_prompts[recovery_family],
        artifact_family=recovery_family,
    )
    completed = _run_full_extraction(artifact, recovery_family, provider, request)
    completed.recovery = True
    return completed


def _classify_recovery_family(artifact, primary_family: str) -> str:
    if primary_family == "lightweight_evidence":
        content = artifact.content or ""
        if artifact.type in {"issue", "commit"} and len(content) >= 500 and _count_signal_hits(content) >= 4:
            return "rationale_doc"
        return primary_family
    if primary_family == "pull_request":
        return primary_family
    return "lightweight_evidence"


def _accumulate_completed_attempt(stats: ExtractionRunStats, latency_total_ms: int, completed: _CompletedExtraction) -> int:
    stats.completed_full_extractions += 1
    stats.current_artifact_title = completed.artifact.title
    stats.current_extraction_family = completed.family
    latency_total_ms += completed.latency_ms
    stats.average_full_extraction_latency_ms = max(
        1,
        round(latency_total_ms / max(stats.completed_full_extractions, 1)),
    )
    return latency_total_ms


def _evaluate_extraction_attempt(completed: _CompletedExtraction) -> _ExtractionEvaluation:
    if completed.timeout:
        return _ExtractionEvaluation(loss_reason="provider_timeout")
    if completed.request_400:
        return _ExtractionEvaluation(loss_reason="provider_request_failed", recoverable=not completed.recovery)
    if completed.request_error:
        return _ExtractionEvaluation(loss_reason="provider_request_failed")

    parsed = parse_extraction_response(
        completed.raw_response,
        artifact_title=completed.artifact.title,
    )
    if parsed.decision is None:
        loss_reason = parsed.loss_reason or "null_decision"
        return _ExtractionEvaluation(
            loss_reason=loss_reason,
            salvaged=parsed.salvaged,
            recoverable=(loss_reason in RECOVERABLE_LOSS_REASONS and not completed.recovery),
        )

    grounded_quotes = _ground_quotes(
        completed.artifact.content,
        _candidate_support_quotes(completed.artifact.content, parsed.decision),
    )
    if not grounded_quotes:
        return _ExtractionEvaluation(
            loss_reason="ungrounded_quote",
            salvaged=parsed.salvaged,
            recoverable=not completed.recovery,
        )
    return _ExtractionEvaluation(
        decision=parsed.decision,
        grounded_quotes=grounded_quotes,
        salvaged=parsed.salvaged,
    )


def _record_attempt_failure_counters(stats: ExtractionRunStats, completed: _CompletedExtraction, evaluation: _ExtractionEvaluation) -> None:
    if evaluation.decision is not None:
        return
    if completed.timeout:
        stats.skipped_provider_timeout += 1
        return
    if completed.request_400:
        stats.skipped_provider_400 += 1
        return
    if evaluation.loss_reason == "invalid_json":
        stats.skipped_invalid_json += 1


def _should_retry_conversion(completed: _CompletedExtraction, evaluation: _ExtractionEvaluation) -> bool:
    return (
        not completed.recovery
        and evaluation.decision is None
        and evaluation.recoverable
        and evaluation.loss_reason in RECOVERABLE_LOSS_REASONS
    )


def _refresh_work_totals(stats: ExtractionRunStats) -> None:
    stats.total_artifacts = stats.shortlisted_artifacts + stats.screened_in_artifacts + stats.recovery_extraction_attempts
    stats.processed_artifacts = stats.screened_artifacts + stats.completed_full_extractions


def _update_progress(stats: ExtractionRunStats, started_at: float) -> None:
    elapsed_seconds = max(0, int(monotonic() - started_at))
    stats.elapsed_seconds = elapsed_seconds
    if stats.total_artifacts <= 0 or stats.processed_artifacts <= 0:
        stats.estimated_remaining_seconds = None
        return
    remaining = max(stats.total_artifacts - stats.processed_artifacts, 0)
    average_seconds_per_unit = elapsed_seconds / max(stats.processed_artifacts, 1)
    stats.estimated_remaining_seconds = int(round(average_seconds_per_unit * remaining))


def _record_conversion_loss(stats: ExtractionRunStats, reason: str) -> None:
    stats.conversion_loss_reasons[reason] = stats.conversion_loss_reasons.get(reason, 0) + 1
