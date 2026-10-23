"""Deterministic evidence diagnostics; never grant a human review state.

These checks validate supplied snapshots only. They do not fetch URLs or prove
that a quote semantically supports a decision, even when every check passes.
"""
from __future__ import annotations

import hashlib
import re
from typing import Any
from urllib.parse import urlsplit

PLACEHOLDERS = {
    "recovered from artifact content",
    "use the option described in the artifact",
    "tradeoffs are implied by the artifact",
    "tbd", "todo", "unknown", "n/a",
}


def evaluate_evidence(candidate: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, str]] = []

    def add(field: str, status: str, reason: str) -> None:
        checks.append({"field": field, "status": status, "reason": reason})

    for field in ("title", "problem", "chosen_option", "tradeoffs"):
        value = candidate.get(field)
        if not isinstance(value, str) or not value.strip():
            add(field, "fail", "missing_or_invalid_field")
        elif " ".join(value.casefold().split()).rstrip(".!。") in PLACEHOLDERS:
            add(field, "fail", "placeholder_field")
        else:
            add(field, "pass", "nonempty_nonplaceholder_only")

    citations = candidate.get("citations")
    if not isinstance(citations, list) or not citations:
        add("citations", "not_evaluated", "missing_citations")
        citations = []
    seen: set[tuple[str, str]] = set()
    for index, citation in enumerate(citations):
        prefix = f"citations[{index}]"
        if not isinstance(citation, dict):
            add(prefix, "fail", "invalid_citation")
            continue
        url = citation.get("url")
        quote = citation.get("quote")
        text = citation.get("snapshot_text")
        try:
            parsed = urlsplit(url if isinstance(url, str) else "")
            valid_url = parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username and not parsed.password
        except ValueError:
            valid_url = False
        add(prefix + ".url", "pass" if valid_url else "fail", "url_syntax_only" if valid_url else "invalid_source_url")
        key = (str(url), str(quote))
        add(prefix + ".unique", "fail" if key in seen else "pass", "duplicate_citation" if key in seen else "unique_citation")
        seen.add(key)

        # A branch URL is mutable. PR numbers identify discussions, not an
        # immutable body; a supplied snapshot hash is checked separately below.
        sha = citation.get("revision")
        pinned = valid_url and isinstance(sha, str) and re.fullmatch(r"[0-9a-f]{40}", sha) and f"/blob/{sha}/" in parsed.path
        add(prefix + ".revision", "pass" if pinned else "not_evaluated", "pinned_blob_url" if pinned else "immutable_revision_unverified")
        if not isinstance(quote, str) or not quote.strip() or not isinstance(text, str):
            add(prefix + ".quote", "not_evaluated", "missing_quote_or_snapshot")
        else:
            start, end = citation.get("start"), citation.get("end")
            if start is None and end is None:
                matches = quote in text
            else:
                matches = type(start) is int and type(end) is int and 0 <= start < end <= len(text) and text[start:end] == quote
            add(prefix + ".quote", "pass" if matches else "fail", "exact_quote_match" if matches else "quote_or_span_mismatch")
        digest = citation.get("snapshot_sha256")
        if isinstance(text, str) and isinstance(digest, str):
            matches = hashlib.sha256(text.encode("utf-8")).hexdigest() == digest
            add(prefix + ".snapshot", "pass" if matches else "fail", "snapshot_integrity_only" if matches else "snapshot_hash_mismatch")
        else:
            add(prefix + ".snapshot", "not_evaluated", "snapshot_integrity_unverified")
        if citation.get("kind") == "pull_request":
            merged = citation.get("merged")
            if merged is False:
                add(prefix + ".adoption", "fail", "unmerged_proposal_not_adoption")
            elif merged is True:
                add(prefix + ".adoption", "pass", "merged_does_not_prove_decision_adoption")
            else:
                add(prefix + ".adoption", "not_evaluated", "pr_merge_state_unknown")

    add("semantic_support", "not_evaluated", "human_review_required")
    return {
        "id": candidate.get("id"),
        "provider_kind": candidate.get("provider_kind", "unknown"),
        "diagnostic_status": "fail" if any(c["status"] == "fail" for c in checks) else "review_required",
        "review_required": True,
        "automatic_acceptance": False,
        "checks": checks,
    }
