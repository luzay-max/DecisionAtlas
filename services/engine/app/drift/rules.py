from __future__ import annotations

import re
from dataclasses import dataclass

from app.db.models import Artifact
from app.drift.rule_types import DriftRule


@dataclass(frozen=True)
class RuleMatch:
    matched_text: str
    excerpt: str


def find_rule_match(rule: DriftRule, artifact: Artifact) -> RuleMatch | None:
    content = artifact.content or ""
    lowered = content.lower()
    if rule.required_term not in lowered:
        return None

    for pattern in rule.forbidden_patterns:
        match = re.search(pattern, content, flags=re.IGNORECASE)
        if match is not None:
            return RuleMatch(
                matched_text=match.group(0),
                excerpt=_excerpt(content, match.start(), match.end()),
            )

    return None


def _excerpt(content: str, start: int, end: int, window: int = 100) -> str:
    excerpt_start = max(0, start - window)
    excerpt_end = min(len(content), end + window)
    excerpt = content[excerpt_start:excerpt_end].strip()
    return excerpt.replace("\n", " ")
