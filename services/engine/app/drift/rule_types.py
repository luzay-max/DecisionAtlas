from __future__ import annotations

from dataclasses import dataclass


REDIS_PERSISTENCE_PATTERNS: tuple[str, ...] = (
    r"redis.{0,40}(primary database|system of record|source of truth|persistent store|durable store|session state)",
    r"(primary database|system of record|source of truth|persistent store|durable store|session state).{0,40}redis",
    r"(persist|durable|canonical|permanent).{0,24}(in|to).{0,10}redis",
    r"redis.{0,24}(persist|durable|canonical|permanent)",
)


@dataclass(frozen=True)
class DriftRule:
    rule_type: str
    workspace_id: int
    decision_id: int
    decision_title: str
    summary: str
    required_term: str
    forbidden_patterns: tuple[str, ...]
