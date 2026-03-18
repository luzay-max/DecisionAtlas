from __future__ import annotations

from dataclasses import dataclass

from app.db.models import Artifact
from app.drift.semantic_recall import SemanticCandidate


SUPERSESSION_MARKERS = ("replace", "migrate", "switch", "deprecate", "retire", "move away")
REVIEW_MARKERS = ("evaluate", "explore", "consider", "proposal", "alternative", "revisit", "rfc")


@dataclass(frozen=True)
class SemanticClassification:
    alert_type: str
    confidence_label: str
    decision_id: int
    summary: str


def classify_semantic_drift(
    *,
    artifact: Artifact,
    candidates: list[SemanticCandidate],
) -> SemanticClassification | None:
    if not candidates:
        return None

    candidate = candidates[0]
    if artifact.timestamp and candidate.created_at and artifact.timestamp <= candidate.created_at:
        return None

    content = " ".join(filter(None, [artifact.title, artifact.content])).lower()
    artifact_title = artifact.title or f"Artifact {artifact.id}"

    if candidate.score >= 2.0 and any(marker in content for marker in SUPERSESSION_MARKERS):
        return SemanticClassification(
            alert_type="possible_supersession",
            confidence_label="medium",
            decision_id=candidate.decision_id,
            summary=(
                f"Artifact '{artifact_title}' may supersede accepted decision '{candidate.title}'. "
                f"Closest prior choice: {candidate.chosen_option}"
            ),
        )

    if candidate.score >= 1.5 and any(marker in content for marker in REVIEW_MARKERS):
        return SemanticClassification(
            alert_type="needs_review",
            confidence_label="low",
            decision_id=candidate.decision_id,
            summary=(
                f"Artifact '{artifact_title}' overlaps with accepted decision '{candidate.title}' and needs review. "
                f"Closest prior choice: {candidate.chosen_option}"
            ),
        )

    return None
