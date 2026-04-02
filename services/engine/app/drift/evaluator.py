from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from app.drift.semantic_classifier import classify_semantic_drift
from app.drift.semantic_recall import recall_related_decisions
from app.drift.semantic_recall import SemanticCandidate
from app.drift.rule_extractor import extract_rules
from app.drift.rules import find_rule_match
from app.indexing.embedder import Embedder, FakeEmbedder
from app.db.models import Artifact
from app.repositories.artifacts import ArtifactRepository
from app.repositories.decisions import DecisionRepository
from app.repositories.drift_alerts import DriftAlertRepository
from app.repositories.source_refs import SourceRefRepository
from app.repositories.workspaces import WorkspaceRepository

SEMANTIC_ALERT_TYPES = ("possible_supersession", "needs_review")


@dataclass(frozen=True)
class DriftEvaluationResult:
    workspace_slug: str
    evaluated_rules: int
    created_alerts: int


@dataclass
class GroupedFollowupSignal:
    decision_id: int
    decision_title: str
    chosen_option: str
    representative_artifact: Artifact
    representative_score: float
    artifact_count: int = 1
    latest_timestamp: datetime | None = None
    implementation_substitution: bool = False

    @classmethod
    def from_candidate(
        cls,
        artifact: Artifact,
        candidate: SemanticCandidate,
        *,
        implementation_substitution: bool,
    ) -> "GroupedFollowupSignal":
        return cls(
            decision_id=candidate.decision_id,
            decision_title=candidate.title,
            chosen_option=candidate.chosen_option,
            representative_artifact=artifact,
            representative_score=candidate.score,
            artifact_count=1,
            latest_timestamp=artifact.timestamp,
            implementation_substitution=implementation_substitution,
        )

    def absorb(self, artifact: Artifact, candidate: SemanticCandidate, *, implementation_substitution: bool) -> None:
        self.artifact_count += 1
        self.implementation_substitution = self.implementation_substitution or implementation_substitution
        artifact_timestamp = artifact.timestamp
        if _is_better_representative(
            current_artifact=self.representative_artifact,
            current_score=self.representative_score,
            candidate_artifact=artifact,
            candidate_score=candidate.score,
        ):
            self.representative_artifact = artifact
            self.representative_score = candidate.score
        if artifact_timestamp and (self.latest_timestamp is None or artifact_timestamp > self.latest_timestamp):
            self.latest_timestamp = artifact_timestamp


class DriftEvaluator:
    def __init__(self, session: Session, *, embedder: Embedder | None = None) -> None:
        self.session = session
        self.embedder = embedder or FakeEmbedder()
        self.artifacts = ArtifactRepository(session)
        self.decisions = DecisionRepository(session)
        self.alerts = DriftAlertRepository(session)
        self.source_refs = SourceRefRepository(session)
        self.workspaces = WorkspaceRepository(session)

    def evaluate_workspace(self, workspace_slug: str) -> DriftEvaluationResult:
        workspace = self.workspaces.get_by_slug(workspace_slug)
        if workspace is None:
            raise ValueError(f"Workspace not found: {workspace_slug}")

        accepted = self.decisions.list_by_review_state(workspace.id, "accepted")
        artifacts = self.artifacts.list_by_workspace(workspace.id)
        evaluated_rules = 0
        created_alerts = 0
        source_artifact_ids: set[int] = set()
        rule_flagged_artifact_ids: set[int] = set()
        grouped_followups: dict[int, GroupedFollowupSignal] = {}

        for decision in accepted:
            rules = extract_rules(decision)
            if not rules:
                source_artifact_ids.update(source_ref.artifact_id for source_ref in self.source_refs.list_by_decision(decision.id))
                continue

            decision_source_artifact_ids = {source_ref.artifact_id for source_ref in self.source_refs.list_by_decision(decision.id)}
            source_artifact_ids.update(decision_source_artifact_ids)
            for rule in rules:
                evaluated_rules += 1
                for artifact in artifacts:
                    if artifact.id in decision_source_artifact_ids:
                        continue
                    if artifact.timestamp and decision.created_at and artifact.timestamp <= decision.created_at:
                        continue

                    match = find_rule_match(rule, artifact)
                    if match is None:
                        continue

                    title = artifact.title or f"Artifact {artifact.id}"
                    summary = (
                        f"{rule.summary} Possible drift in '{title}': {match.excerpt}"
                    )
                    _, created = self.alerts.create_or_update(
                        workspace_id=workspace.id,
                        artifact_id=artifact.id,
                        decision_id=decision.id,
                        alert_type="possible_drift",
                        summary=summary,
                        status="open",
                    )
                    if created:
                        created_alerts += 1
                    rule_flagged_artifact_ids.add(artifact.id)

        self.alerts.delete_by_workspace_and_types(workspace.id, SEMANTIC_ALERT_TYPES)

        for artifact in artifacts:
            if artifact.id in source_artifact_ids or artifact.id in rule_flagged_artifact_ids:
                continue

            candidates = recall_related_decisions(
                session=self.session,
                workspace_slug=workspace.slug,
                artifact=artifact,
                embedder=self.embedder,
            )
            classification = classify_semantic_drift(artifact=artifact, candidates=candidates)
            if classification is None:
                continue

            if classification.alert_type == "needs_review":
                candidate = candidates[0]
                existing = grouped_followups.get(classification.decision_id)
                if existing is None:
                    grouped_followups[classification.decision_id] = GroupedFollowupSignal.from_candidate(
                        artifact,
                        candidate,
                        implementation_substitution=classification.is_implementation_substitution,
                    )
                else:
                    existing.absorb(
                        artifact,
                        candidate,
                        implementation_substitution=classification.is_implementation_substitution,
                    )
                continue

            _, created = self.alerts.create_or_update(
                workspace_id=workspace.id,
                artifact_id=artifact.id,
                decision_id=classification.decision_id,
                alert_type=classification.alert_type,
                summary=classification.summary,
                status="open",
            )
            if created:
                created_alerts += 1

        for signal in grouped_followups.values():
            _, created = self.alerts.create_or_update(
                workspace_id=workspace.id,
                artifact_id=signal.representative_artifact.id,
                decision_id=signal.decision_id,
                alert_type="needs_review",
                summary=_summarize_grouped_followup(signal),
                status="open",
            )
            if created:
                created_alerts += 1

        self.session.commit()
        return DriftEvaluationResult(
            workspace_slug=workspace.slug,
            evaluated_rules=evaluated_rules,
            created_alerts=created_alerts,
        )


def _is_better_representative(
    *,
    current_artifact: Artifact,
    current_score: float,
    candidate_artifact: Artifact,
    candidate_score: float,
) -> bool:
    current_timestamp = current_artifact.timestamp
    candidate_timestamp = candidate_artifact.timestamp
    if candidate_score > current_score:
        return True
    if candidate_score < current_score:
        return False
    if current_timestamp is None:
        return candidate_timestamp is not None
    if candidate_timestamp is None:
        return False
    return candidate_timestamp > current_timestamp


def _summarize_grouped_followup(signal: GroupedFollowupSignal) -> str:
    title = signal.representative_artifact.title or f"Artifact {signal.representative_artifact.id}"
    if signal.artifact_count <= 1:
        if signal.implementation_substitution:
            return (
                f"Artifact '{title}' appears related to accepted decision '{signal.decision_title}', "
                "but the change currently looks closer to an implementation-level substitution than a replacement of the prior choice. "
                f"Closest prior choice: {signal.chosen_option}"
            )
        return (
            f"Artifact '{title}' appears related to accepted decision '{signal.decision_title}'. "
            "Review whether the newer work changes or reinforces the prior choice. "
            f"Closest prior choice: {signal.chosen_option}"
        )

    additional_count = signal.artifact_count - 1
    artifact_word = "artifact" if additional_count == 1 else "artifacts"
    if signal.implementation_substitution:
        return (
            f"Artifact '{title}' and {additional_count} related follow-up {artifact_word} appear connected to accepted decision "
            f"'{signal.decision_title}', but the newer work still looks closer to implementation-level substitution than full decision replacement. "
            f"Closest prior choice: {signal.chosen_option}"
        )
    return (
        f"Artifact '{title}' and {additional_count} related follow-up {artifact_word} appear connected to accepted decision "
        f"'{signal.decision_title}'. Review whether this newer work only continues the prior choice or introduces a real decision change. "
        f"Closest prior choice: {signal.chosen_option}"
    )
