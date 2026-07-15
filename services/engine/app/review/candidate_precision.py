from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
import re
from typing import Iterable


_STOPWORDS = {
    "about",
    "after",
    "because",
    "between",
    "from",
    "have",
    "into",
    "more",
    "that",
    "the",
    "their",
    "then",
    "this",
    "through",
    "using",
    "with",
}
_HIGH_SIGNAL_FAMILIES = {"architecture", "migration", "rollout", "release", "operations", "pull_request"}
_TIER_ORDER = {"weak": 0, "partial": 1, "strong": 2}


@dataclass(frozen=True, slots=True)
class CandidatePrecisionProfile:
    decision_id: int
    score: int
    tier: str
    reasons: tuple[str, ...]
    artifact_family: str
    parser_salvaged: bool | None
    recovery: bool
    sparse_recovery: bool
    cluster_id: str | None = None
    cluster_size: int = 1
    duplicate_of: int | None = None

    @property
    def is_representative(self) -> bool:
        return self.duplicate_of is None


def _tokens(*values: str | None) -> set[str]:
    result: set[str] = set()
    for value in values:
        for token in re.findall(r"[a-z0-9]+", (value or "").casefold()):
            if len(token) > 2 and token not in _STOPWORDS:
                result.add(token)
    return result


def _jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def _metadata(decision) -> dict:
    value = getattr(decision, "candidate_metadata_json", None)
    return value if isinstance(value, dict) else {}


def _specificity(decision) -> int:
    fields = _tokens(decision.title, decision.problem, decision.chosen_option, decision.tradeoffs)
    if len(fields) >= 24:
        return 10
    if len(fields) >= 14:
        return 7
    if len(fields) >= 7:
        return 4
    return 0


def build_profile(decision, source_refs: list, primary_artifact) -> CandidatePrecisionProfile:
    metadata = _metadata(decision)
    family = str(metadata.get("artifact_family") or "unknown")
    parser_salvaged = metadata.get("parser_salvaged") if "parser_salvaged" in metadata else None
    recovery = bool(metadata.get("recovery", False))
    sparse_recovery = bool(metadata.get("sparse_recovery", False))
    source_ref_count = len(source_refs)
    previewable_count = sum(1 for source_ref in source_refs if str(getattr(source_ref, "quote", "") or "").strip())
    has_primary = primary_artifact is not None
    has_url = any(getattr(source_ref, "url", None) for source_ref in source_refs) or bool(
        getattr(primary_artifact, "url", None)
    )
    score = 0
    reasons: list[str] = []
    if source_ref_count >= 2:
        score += 30
        reasons.append("multiple_source_refs")
    elif source_ref_count == 1:
        score += 16
        reasons.append("single_source_ref")
    else:
        reasons.append("missing_source_refs")
    if previewable_count:
        score += 10
        reasons.append("previewable_quote")
    else:
        reasons.append("missing_previewable_quote")
    if has_primary:
        score += 10
        reasons.append("artifact_provenance")
    else:
        reasons.append("missing_artifact_provenance")
    if has_url:
        score += 8
        reasons.append("source_url_available")
    else:
        reasons.append("missing_source_url")
    confidence = max(0.0, min(1.0, float(getattr(decision, "confidence", 0.0) or 0.0)))
    score += round(confidence * 22)
    reasons.append("high_confidence" if confidence >= 0.8 else "medium_confidence" if confidence >= 0.6 else "low_confidence")
    specificity = _specificity(decision)
    if specificity:
        score += specificity
        reasons.append("decision_specificity")
    else:
        reasons.append("low_decision_specificity")
    if family in _HIGH_SIGNAL_FAMILIES:
        score += 6
        reasons.append("high_signal_artifact_family")
    elif family == "unknown":
        reasons.append("unknown_extraction_origin")
    else:
        reasons.append("known_extraction_origin")
    if parser_salvaged is True:
        score -= 7
        reasons.append("parser_salvaged")
    if recovery:
        score -= 2
        reasons.append("recovery_extraction")
    if sparse_recovery:
        score -= 2
        reasons.append("sparse_recovery")
    score = max(0, min(100, score))
    if source_ref_count >= 2 and previewable_count >= 1 and has_primary and score >= 70:
        tier = "strong"
    elif score >= 45 and (source_ref_count > 0 or has_primary or has_url):
        tier = "partial"
    else:
        tier = "weak"
    return CandidatePrecisionProfile(
        decision_id=int(decision.id),
        score=score,
        tier=tier,
        reasons=tuple(reasons),
        artifact_family=family,
        parser_salvaged=parser_salvaged if isinstance(parser_salvaged, bool) else None,
        recovery=recovery,
        sparse_recovery=sparse_recovery,
    )


def _clusterable(decision) -> tuple[set[str], set[str]]:
    bearing = _tokens(decision.title, decision.chosen_option)
    all_tokens = bearing | _tokens(decision.problem, decision.tradeoffs)
    return bearing, all_tokens


def rank_profiles(decisions: list, evidence: dict[int, tuple[list, object]]) -> dict[int, CandidatePrecisionProfile]:
    profiles = {
        int(decision.id): build_profile(decision, *evidence.get(int(decision.id), ([], None))) for decision in decisions
    }
    signatures = {int(decision.id): _clusterable(decision) for decision in decisions}
    parent = {int(decision.id): int(decision.id) for decision in decisions}

    def find(value: int) -> int:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(left: int, right: int) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[max(left_root, right_root)] = min(left_root, right_root)

    ordered_ids = sorted(signatures)
    for index, left_id in enumerate(ordered_ids):
        left_bearing, left_all = signatures[left_id]
        if not left_bearing:
            continue
        for right_id in ordered_ids[index + 1 :]:
            right_bearing, right_all = signatures[right_id]
            bearing_overlap = _jaccard(left_bearing, right_bearing)
            all_overlap = _jaccard(left_all, right_all)
            if bearing_overlap >= 0.45 and all_overlap >= 0.55:
                union(left_id, right_id)

    groups: dict[int, list[int]] = {}
    for decision_id in ordered_ids:
        groups.setdefault(find(decision_id), []).append(decision_id)
    for group in groups.values():
        if len(group) < 2:
            continue
        representative = min(
            group,
            key=lambda decision_id: (-profiles[decision_id].score, -_TIER_ORDER[profiles[decision_id].tier], decision_id),
        )
        cluster_id = f"candidate-{min(group)}"
        for decision_id in group:
            profiles[decision_id] = replace(
                profiles[decision_id],
                cluster_id=cluster_id,
                cluster_size=len(group),
                duplicate_of=None if decision_id == representative else representative,
                reasons=profiles[decision_id].reasons
                + (("cluster_representative",) if decision_id == representative else ("near_duplicate",)),
            )
    return profiles


def profile_sort_key(decision, profile: CandidatePrecisionProfile) -> tuple:
    created_at = getattr(decision, "created_at", None)
    timestamp = created_at.timestamp() if isinstance(created_at, datetime) else 0.0
    return (
        -_TIER_ORDER[profile.tier],
        0 if profile.is_representative else 1,
        -profile.score,
        -timestamp,
        -int(decision.id),
    )
