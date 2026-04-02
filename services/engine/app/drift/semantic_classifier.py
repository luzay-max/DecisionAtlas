from __future__ import annotations

from dataclasses import dataclass

from app.db.models import Artifact
from app.drift.semantic_recall import SemanticCandidate


SUPERSESSION_MARKERS = ("replace", "migrate", "switch", "deprecate", "retire", "move away", "sunset")
REVIEW_MARKERS = ("evaluate", "explore", "consider", "proposal", "alternative", "revisit", "rfc")
BROAD_ARTIFACT_MARKERS = (
    "changelog",
    "contributing",
    "roadmap",
    "implementation phase",
    "implementation phases",
    "release notes",
)


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
    broad_artifact = _is_broad_artifact(artifact)
    explicit_supersession = _has_explicit_supersession_signal(content)
    unusually_explicit_for_broad_doc = _has_unusually_explicit_supersession_signal(content)
    review_signal = any(marker in content for marker in REVIEW_MARKERS)
    overlap_signal = candidate.score >= 1.75 and (
        review_signal
        or explicit_supersession
        or broad_artifact
    )

    if candidate.score >= 2.5 and explicit_supersession and (not broad_artifact or unusually_explicit_for_broad_doc):
        return SemanticClassification(
            alert_type="possible_supersession",
            confidence_label="medium",
            decision_id=candidate.decision_id,
            summary=(
                f"Artifact '{artifact_title}' may indicate that accepted decision '{candidate.title}' is being replaced. "
                "Review the newer change before treating the prior choice as superseded. "
                f"Closest prior choice: {candidate.chosen_option}"
            ),
        )

    if overlap_signal:
        return SemanticClassification(
            alert_type="needs_review",
            confidence_label="low",
            decision_id=candidate.decision_id,
            summary=(
                f"Artifact '{artifact_title}' appears related to accepted decision '{candidate.title}'. "
                "Review whether the newer work changes or reinforces the prior choice. "
                f"Closest prior choice: {candidate.chosen_option}"
            ),
        )

    return None


def _is_broad_artifact(artifact: Artifact) -> bool:
    metadata = artifact.metadata_json if isinstance(artifact.metadata_json, dict) else {}
    lowered_parts = [
        (artifact.title or "").lower(),
        (artifact.source_id or "").lower(),
        str(metadata.get("path") or "").lower(),
        str(metadata.get("signal_category") or "").lower(),
    ]
    haystack = " ".join(part for part in lowered_parts if part)
    return any(marker in haystack for marker in BROAD_ARTIFACT_MARKERS)


def _has_explicit_supersession_signal(content: str) -> bool:
    if any(marker in content for marker in ("deprecate", "retire", "move away from", "sunset", "replaced by")):
        return True
    if "switch from" in content:
        return True
    if "migrate away from" in content or "migrate from" in content:
        return True
    if "replace" in content and "with" in content:
        return True
    return False


def _has_unusually_explicit_supersession_signal(content: str) -> bool:
    return any(
        marker in content
        for marker in (
            "replaced by",
            "switch from",
            "migrate away from",
            "deprecate",
            "retire",
            "sunset",
        )
    )
