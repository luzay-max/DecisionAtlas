from __future__ import annotations

from dataclasses import dataclass
import re

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
STOP_WORDS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "use",
    "using",
    "with",
    "keep",
    "keeping",
    "current",
    "new",
}
GENERIC_REPLACEMENT_TERMS = {"change", "changes", "part", "parts", "thing", "things", "work", "works"}
IMPLEMENTATION_MARKERS = (
    "adapter",
    "browser control",
    "cdp",
    "client",
    "cookie",
    "cookies",
    "dependency",
    "driver",
    "framework",
    "library",
    "mcp",
    "playwright",
    "primitive",
    "primitives",
    "protocol",
    "runtime",
    "sdk",
    "server",
    "test",
    "tests",
    "transport",
    "websocket",
)
MAINTENANCE_MARKERS = (
    "bug",
    "bugs",
    "bugfix",
    "bugfixes",
    "cleanup",
    "fix",
    "fixes",
    "fixed",
    "keep_alive",
    "keep-alive",
    "lifecycle",
    "maintain",
    "maintenance",
    "preserve",
    "preserves",
    "preserving",
    "regression",
    "repair",
    "repairs",
    "shutdown",
    "stability",
)


@dataclass(frozen=True)
class SemanticClassification:
    alert_type: str
    confidence_label: str
    decision_id: int
    summary: str
    is_implementation_substitution: bool = False


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
    decision_layer_supersession = _is_decision_layer_supersession(candidate, content)
    unusually_explicit_for_broad_doc = _has_unusually_explicit_supersession_signal(content)
    review_signal = any(marker in content for marker in REVIEW_MARKERS)
    overlap_signal = candidate.score >= 1.75 and (
        review_signal
        or explicit_supersession
        or broad_artifact
    )

    if (
        candidate.score >= 2.5
        and explicit_supersession
        and decision_layer_supersession
        and (not broad_artifact or unusually_explicit_for_broad_doc)
    ):
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
        if explicit_supersession and not decision_layer_supersession:
            return SemanticClassification(
                alert_type="needs_review",
                confidence_label="low",
                decision_id=candidate.decision_id,
                summary=(
                    f"Artifact '{artifact_title}' appears related to accepted decision '{candidate.title}', "
                    "but the change currently looks closer to an implementation-level substitution than a replacement of the prior choice. "
                    f"Closest prior choice: {candidate.chosen_option}"
                ),
                is_implementation_substitution=True,
            )
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
    if _extract_replacement_targets(content):
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


def _is_decision_layer_supersession(candidate: SemanticCandidate, content: str) -> bool:
    maintenance_biased = _has_maintenance_bias(content)
    replacement_targets = _extract_replacement_targets(content)
    candidate_tokens = _meaningful_tokens(" ".join((candidate.title, candidate.problem, candidate.chosen_option)))
    replacement_tokens = set().union(*(_meaningful_tokens(target) for target in replacement_targets)) if replacement_targets else set()

    if maintenance_biased and not replacement_tokens and "replaced by" not in content and "migrate away from" not in content:
        return False

    if any(marker in content for marker in ("deprecate", "retire", "sunset", "replaced by")):
        return True
    if "migrate away from" in content:
        return True

    if replacement_tokens and replacement_tokens.intersection(candidate_tokens):
        if maintenance_biased and not _has_unusually_explicit_supersession_signal(content):
            return False
        return True
    if replacement_tokens and not replacement_tokens.intersection(candidate_tokens):
        return False

    if maintenance_biased:
        return False

    return not any(marker in content for marker in IMPLEMENTATION_MARKERS)


def _extract_replacement_targets(content: str) -> list[str]:
    patterns = (
        r"replace\s+(?P<old>[^.,;\n]{1,80}?)\s+with\s+(?P<new>[^.,;\n]{1,80})",
        r"switch\s+from\s+(?P<old>[^.,;\n]{1,80}?)\s+to\s+(?P<new>[^.,;\n]{1,80})",
        r"migrate\s+from\s+(?P<old>[^.,;\n]{1,80}?)\s+to\s+(?P<new>[^.,;\n]{1,80})",
        r"(?P<new>[a-z0-9_+-]{2,40})\s+replace\s+(?P<old>[a-z0-9_+-]{2,40})",
    )
    results: list[str] = []
    for pattern in patterns:
        for match in re.finditer(pattern, content):
            old = match.groupdict().get("old")
            new = match.groupdict().get("new")
            if pattern == patterns[-1] and not _is_meaningful_shorthand_replacement(old, new):
                continue
            if old:
                results.append(old.strip())
            if new:
                results.append(new.strip())
    return results


def _meaningful_tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9_+-]+", text.lower())
        if len(token) >= 3 and token not in STOP_WORDS
    }


def _is_meaningful_shorthand_replacement(old: str | None, new: str | None) -> bool:
    operands = [operand for operand in (old, new) if operand]
    if len(operands) != 2:
        return False
    tokens = [operand.strip().lower() for operand in operands]
    return all(token not in STOP_WORDS and token not in GENERIC_REPLACEMENT_TERMS for token in tokens)


def _has_maintenance_bias(content: str) -> bool:
    return any(marker in content for marker in MAINTENANCE_MARKERS)
