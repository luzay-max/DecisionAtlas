from __future__ import annotations

from app.db.models import Decision
from app.drift.rule_types import DriftRule, REDIS_PERSISTENCE_PATTERNS


CACHE_ONLY_MARKERS = (
    "cache only",
    "cache-only",
    "only as cache",
    "only as a cache",
)


def extract_rules(decision: Decision) -> list[DriftRule]:
    if decision.review_state != "accepted":
        return []

    decision_text = " ".join(
        part
        for part in [
            decision.title,
            decision.problem,
            decision.context,
            decision.constraints,
            decision.chosen_option,
            decision.tradeoffs,
        ]
        if part
    ).lower()

    if "redis" in decision_text and any(marker in decision_text for marker in CACHE_ONLY_MARKERS):
        return [
            DriftRule(
                rule_type="redis_cache_only",
                workspace_id=decision.workspace_id,
                decision_id=decision.id,
                decision_title=decision.title,
                summary=f"Accepted decision '{decision.title}' keeps Redis cache-only.",
                required_term="redis",
                forbidden_patterns=REDIS_PERSISTENCE_PATTERNS,
            )
        ]

    return []
