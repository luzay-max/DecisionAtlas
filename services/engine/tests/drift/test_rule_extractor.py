from __future__ import annotations

from app.db.models import Decision
from app.drift.rule_extractor import extract_rules


def test_extracts_redis_cache_only_rule_from_accepted_decision() -> None:
    decision = Decision(
        id=7,
        workspace_id=1,
        title="Use Redis Cache",
        status="active",
        review_state="accepted",
        problem="Latency is too high",
        context=None,
        constraints="Redis stays cache-only for the MVP.",
        chosen_option="Use Redis as cache only and keep PostgreSQL primary.",
        tradeoffs="Extra infra",
        confidence=0.91,
    )

    rules = extract_rules(decision)

    assert len(rules) == 1
    assert rules[0].rule_type == "redis_cache_only"
    assert rules[0].decision_id == 7
    assert "cache-only" in rules[0].summary.lower()


def test_skips_non_accepted_decisions() -> None:
    decision = Decision(
        id=8,
        workspace_id=1,
        title="Use Redis Cache",
        status="active",
        review_state="candidate",
        problem="Latency is too high",
        context=None,
        constraints=None,
        chosen_option="Use Redis as cache only.",
        tradeoffs="Extra infra",
        confidence=0.7,
    )

    assert extract_rules(decision) == []
