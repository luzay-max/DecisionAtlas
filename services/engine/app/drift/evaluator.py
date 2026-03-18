from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.drift.semantic_classifier import classify_semantic_drift
from app.drift.semantic_recall import recall_related_decisions
from app.drift.rule_extractor import extract_rules
from app.drift.rules import find_rule_match
from app.indexing.embedder import Embedder, FakeEmbedder
from app.repositories.artifacts import ArtifactRepository
from app.repositories.decisions import DecisionRepository
from app.repositories.drift_alerts import DriftAlertRepository
from app.repositories.source_refs import SourceRefRepository
from app.repositories.workspaces import WorkspaceRepository


@dataclass(frozen=True)
class DriftEvaluationResult:
    workspace_slug: str
    evaluated_rules: int
    created_alerts: int


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

        self.session.commit()
        return DriftEvaluationResult(
            workspace_slug=workspace.slug,
            evaluated_rules=evaluated_rules,
            created_alerts=created_alerts,
        )
