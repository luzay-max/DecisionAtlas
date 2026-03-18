from __future__ import annotations

from app.extractor.parser import parse_extraction_response
from app.extractor.prompt_loader import load_prompt
from app.llm.base import ExtractionProvider, ExtractionRequest
from app.repositories.artifacts import ArtifactRepository
from app.repositories.decisions import DecisionRepository
from app.repositories.source_refs import SourceRefRepository
from app.repositories.workspaces import WorkspaceRepository
from sqlalchemy.orm import Session


SIGNAL_WORDS = ("decide", "decision", "tradeoff", "chose", "because", "why")


def _has_decision_signal(content: str) -> bool:
    lowered = content.lower()
    return any(token in lowered for token in SIGNAL_WORDS)


def _find_span(content: str, quote: str) -> tuple[int | None, int | None]:
    if not quote:
        return None, None
    start = content.find(quote)
    if start == -1:
        return None, None
    return start, start + len(quote)


class CandidateExtractionPipeline:
    def __init__(self, session: Session, provider: ExtractionProvider) -> None:
        self.session = session
        self.provider = provider
        self.workspaces = WorkspaceRepository(session)
        self.artifacts = ArtifactRepository(session)
        self.decisions = DecisionRepository(session)
        self.source_refs = SourceRefRepository(session)

    def run(self, *, workspace_slug: str) -> int:
        workspace = self.workspaces.get_by_slug(workspace_slug)
        if workspace is None:
            raise ValueError(f"Workspace not found: {workspace_slug}")

        prompt = load_prompt("decision-extraction")
        created = 0
        for artifact in self.artifacts.list_by_workspace(workspace.id):
            if not _has_decision_signal(artifact.content):
                continue
            if self.source_refs.exists_for_artifact(artifact.id):
                continue

            raw_response = self.provider.extract_candidate(
                ExtractionRequest(
                    artifact_id=artifact.id,
                    artifact_title=artifact.title,
                    artifact_content=artifact.content,
                    prompt=prompt,
                )
            )
            parsed = parse_extraction_response(raw_response)
            if parsed is None:
                continue

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
            created += 1

        self.session.commit()
        return created
