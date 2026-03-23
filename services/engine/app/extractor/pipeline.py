from __future__ import annotations

from dataclasses import asdict, dataclass
from time import monotonic
from typing import Callable

from app.extractor.parser import parse_extraction_response
from app.extractor.prompt_loader import load_prompt
from app.llm.base import ExtractionProvider, ExtractionRequest, ProviderRequestError, ProviderTimeoutError
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
)
TITLE_SIGNAL_WORDS = ("decision", "architecture", "migration", "rollout", "release", "deprecation", "rfc", "adr")
PATH_SIGNAL_WORDS = ("decision", "architecture", "migration", "rollout", "release", "deprecation", "rfc", "adr", "runbook", "operat")
MAX_EXTRACTION_ARTIFACT_CHARS = 12000


@dataclass(slots=True)
class _RankedArtifact:
    score: int
    artifact_id: int
    artifact: object


@dataclass(slots=True)
class ExtractionRunStats:
    total_artifacts: int = 0
    processed_artifacts: int = 0
    created_candidates: int = 0
    skipped_provider_400: int = 0
    skipped_provider_timeout: int = 0
    skipped_invalid_json: int = 0
    elapsed_seconds: int | None = None
    estimated_remaining_seconds: int | None = None
    current_artifact_title: str | None = None

    def to_summary(self) -> dict[str, int | str | None]:
        return asdict(self)


def _has_decision_signal(content: str) -> bool:
    lowered = content.lower()
    return any(token in lowered for token in SIGNAL_WORDS)


def _artifact_signal_score(artifact) -> int:
    score = 0
    lowered_content = artifact.content.lower()
    lowered_title = (artifact.title or "").lower()
    path = str((artifact.metadata_json or {}).get("path", "")).lower()

    if _has_decision_signal(artifact.content):
        score += 2
    if artifact.type in {"doc", "pr"}:
        score += 1
    if any(token in lowered_title for token in TITLE_SIGNAL_WORDS):
        score += 1
    if any(token in path for token in PATH_SIGNAL_WORDS):
        score += 1

    return score


def _find_span(content: str, quote: str) -> tuple[int | None, int | None]:
    if not quote:
        return None, None
    start = content.find(quote)
    if start == -1:
        return None, None
    return start, start + len(quote)


def _prepare_extraction_content(artifact) -> str:
    content = artifact.content.strip()
    if len(content) <= MAX_EXTRACTION_ARTIFACT_CHARS:
        return content

    head_budget = int(MAX_EXTRACTION_ARTIFACT_CHARS * 0.75)
    tail_budget = MAX_EXTRACTION_ARTIFACT_CHARS - head_budget
    path = (artifact.metadata_json or {}).get("path")
    header_parts = [f"Artifact title: {artifact.title or 'Untitled'}"]
    if isinstance(path, str) and path:
        header_parts.append(f"Artifact path: {path}")
    header = "\n".join(header_parts)
    truncated = (
        f"{header}\n\n"
        f"{content[:head_budget]}\n\n"
        "[... content truncated to stay within extraction limits ...]\n\n"
        f"{content[-tail_budget:]}"
    )
    return truncated


class CandidateExtractionPipeline:
    def __init__(self, session: Session, provider: ExtractionProvider) -> None:
        self.session = session
        self.provider = provider
        self.workspaces = WorkspaceRepository(session)
        self.artifacts = ArtifactRepository(session)
        self.decisions = DecisionRepository(session)
        self.source_refs = SourceRefRepository(session)
        self.last_run_stats = ExtractionRunStats()

    def run(
        self,
        *,
        workspace_slug: str,
        progress_callback: Callable[[ExtractionRunStats], None] | None = None,
    ) -> int:
        workspace = self.workspaces.get_by_slug(workspace_slug)
        if workspace is None:
            raise ValueError(f"Workspace not found: {workspace_slug}")

        prompt = load_prompt("decision-extraction")
        ranked_artifacts = sorted(
            (
                _RankedArtifact(score=_artifact_signal_score(artifact), artifact_id=artifact.id, artifact=artifact)
                for artifact in self.artifacts.list_by_workspace(workspace.id)
            ),
            key=lambda item: (-item.score, item.artifact_id),
        )
        eligible_artifacts = [
            ranked.artifact
            for ranked in ranked_artifacts
            if ranked.score > 0 and not self.source_refs.exists_for_artifact(ranked.artifact.id)
        ]
        stats = ExtractionRunStats(total_artifacts=len(eligible_artifacts))
        started_at = monotonic()
        _update_progress(stats, started_at)
        if progress_callback is not None:
            progress_callback(stats)

        for artifact in eligible_artifacts:
            stats.current_artifact_title = artifact.title

            try:
                raw_response = self.provider.extract_candidate(
                    ExtractionRequest(
                        artifact_id=artifact.id,
                        artifact_title=artifact.title,
                        artifact_content=_prepare_extraction_content(artifact),
                        prompt=prompt,
                    )
                )
            except ProviderTimeoutError:
                stats.skipped_provider_timeout += 1
            except ProviderRequestError as error:
                if "status 400" in str(error):
                    stats.skipped_provider_400 += 1
                else:
                    raise
            else:
                try:
                    parsed = parse_extraction_response(raw_response)
                except ValueError:
                    stats.skipped_invalid_json += 1
                else:
                    if parsed is not None:
                        decision = self.decisions.create_candidate(
                            workspace_id=workspace.id,
                            title=parsed.title,
                            problem=parsed.problem,
                            context=parsed.context,
                            constraints=parsed.constraints,
                            chosen_option=parsed.chosen_option,
                            tradeoffs=parsed.tradeoffs,
                            confidence=parsed.confidence,
                        )
                        span_start, span_end = _find_span(artifact.content, parsed.source_quote)
                        self.source_refs.create(
                            decision_id=decision.id,
                            artifact_id=artifact.id,
                            span_start=span_start,
                            span_end=span_end,
                            quote=parsed.source_quote,
                            url=artifact.url,
                            relevance_score=parsed.confidence,
                        )
                        stats.created_candidates += 1
            stats.processed_artifacts += 1
            _update_progress(stats, started_at)
            if progress_callback is not None:
                progress_callback(stats)

        stats.current_artifact_title = None
        _update_progress(stats, started_at)
        if progress_callback is not None:
            progress_callback(stats)

        self.session.commit()
        self.last_run_stats = stats
        return stats.created_candidates


def _update_progress(stats: ExtractionRunStats, started_at: float) -> None:
    elapsed_seconds = max(0, int(monotonic() - started_at))
    stats.elapsed_seconds = elapsed_seconds
    if stats.total_artifacts <= 0 or stats.processed_artifacts <= 0:
        stats.estimated_remaining_seconds = None
        return
    remaining = max(stats.total_artifacts - stats.processed_artifacts, 0)
    average_seconds_per_artifact = elapsed_seconds / max(stats.processed_artifacts, 1)
    stats.estimated_remaining_seconds = int(round(average_seconds_per_artifact * remaining))
