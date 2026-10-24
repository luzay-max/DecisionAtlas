"""Offline, self-attested independent decision-evidence review packets.

This module never establishes a person's identity, changes a Decision, or
interprets a review as production acceptance.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime
import hashlib
import json
import re

_REVIEWER = re.compile(r"^[A-Za-z0-9_.-]{2,80}$")
_DECISION_QUALITY = {"real_decision", "not_a_decision", "uncertain"}
_QUOTE_VALIDITY = {"supported", "unsupported", "not_evaluated"}
_ADOPTION = {"adopted", "not_adopted", "unknown"}
_VERDICT = {"accept", "reject", "uncertain"}


def _fingerprint(data: object) -> str:
    """Deterministic, unsigned digest. Never confuse it with authentication."""
    encoded = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _nonblank(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_packet(packet: object) -> dict:
    if not isinstance(packet, dict) or packet.get("schema_version") != 1 or packet.get("review_type") != "independent_source_evidence":
        raise ValueError("invalid Phase-C review packet")
    expected = packet.get("packet_sha256")
    base = {k: v for k, v in packet.items() if k != "packet_sha256"}
    if not isinstance(expected, str) or expected != _fingerprint(base):
        raise ValueError("review packet fingerprint mismatch")
    candidates = packet.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError("review packet candidates missing")
    ids = [c.get("id") if isinstance(c, dict) else None for c in candidates]
    if any(not _nonblank(x) for x in ids) or len(set(ids)) != len(ids):
        raise ValueError("review packet candidate IDs invalid or duplicated")
    return packet


def prepare_review_packet(snapshot: dict, verification: dict) -> dict:
    """Join local Phase-A data with Phase-B checks, fail closed on mismatches."""
    if not isinstance(snapshot, dict) or not isinstance(verification, dict):
        raise ValueError("Phase-A export and Phase-B report objects required")
    if snapshot.get("schema_version") != 1 or snapshot.get("scope") != "operator_approved_local_public_sqlite_snapshot":
        raise ValueError("invalid Phase-A public snapshot")
    if (verification.get("schema_version") != 1
            or verification.get("basis") != "operator_supplied_public_capture_not_live_verification"
            or verification.get("human_review") != "not_run"
            or verification.get("source_authenticity") != "capture_not_independently_attested"
            or verification.get("model_accuracy") != "not_evaluated"):
        raise ValueError("invalid Phase-B offline verification report")
    workspace = snapshot.get("workspace")
    rows, findings = snapshot.get("rows"), verification.get("results")
    if (not isinstance(workspace, dict) or not _nonblank(workspace.get("repo_url"))
            or not _nonblank(workspace.get("slug"))
            or not isinstance(rows, list) or not isinstance(findings, list)
            or snapshot.get("candidate_count") != len(rows)
            or verification.get("candidate_count") != len(findings)
            or len(rows) != len(findings)):
        raise ValueError("Phase-A / Phase-B candidate count or workspace mismatch")

    candidates = []
    seen = set()
    for source, result in zip(rows, findings):
        if not isinstance(source, dict) or not isinstance(result, dict) or not isinstance(source.get("candidate"), dict):
            raise ValueError("malformed candidate or evidence result")
        candidate = source["candidate"]
        identity = candidate.get("id")
        if not _nonblank(identity) or identity in seen or result.get("id") != identity:
            raise ValueError("candidate identity mismatch or duplicate")
        seen.add(identity)
        if (result.get("automatic_acceptance") is not False
                or result.get("review_required") is not True):
            raise ValueError("verified source cannot automatically accept decisions")
        cites, checks = candidate.get("citations"), result.get("checks")
        if not isinstance(cites, list) or not isinstance(checks, list) or len(cites) != len(checks):
            raise ValueError("candidate citation count differs from verification checks")
        evidence = []
        for i, (citation, check) in enumerate(zip(cites, checks)):
            if (not isinstance(citation, dict) or not isinstance(check, dict)
                    or not _nonblank(citation.get("url")) or check.get("citation_index") != i
                    or check.get("url") != citation["url"]
                    or check.get("status") not in {"pass", "fail", "not_evaluated"}
                    or not _nonblank(check.get("reason"))):
                raise ValueError("source citation does not match recorded verification check")
            evidence.append({
                "url": citation["url"],
                "quote": citation.get("quote"),
                "start": citation.get("start"),
                "end": citation.get("end"),
                "capture_check_status": check["status"],
                "capture_check_reason": check["reason"],
            })
        candidates.append({
            "id": identity,
            "title": candidate.get("title"),
            "problem": candidate.get("problem"),
            "chosen_option": candidate.get("chosen_option"),
            "tradeoffs": candidate.get("tradeoffs"),
            "provider_kind": candidate.get("provider_kind", "unknown"),
            "stored_review_state": source.get("stored_review_state"),
            "evidence": evidence,
        })
    packet = {
        "schema_version": 1,
        "review_type": "independent_source_evidence",
        "workspace": {"slug": workspace["slug"], "repo_url": workspace["repo_url"]},
        "source_digests": {
            "phase_a_sha256": _fingerprint(snapshot),
            "phase_b_sha256": _fingerprint(verification),
        },
        "human_review": "not_run",
        "reviewer_identity_verification": "not_provided",
        "model_accuracy": "not_evaluated",
        "candidate_count": len(candidates),
        "candidates": candidates,
    }
    packet["packet_sha256"] = _fingerprint(packet)
    return packet


def blank_reviewer_template(packet: dict) -> dict:
    packet = _valid_packet(packet)
    return {
        "schema_version": 1,
        "packet_sha256": packet["packet_sha256"],
        "reviewer_id": "",
        "reviewed_at": None,
        "independent_of_candidate_author_attested": False,
        "original_sources_checked_attested": False,
        "assessments": [
            {
                "candidate_id": row["id"],
                "decision_quality": None,
                "quote_validity": None,
                "adoption_evidence": None,
                "verdict": None,
                "rationale": "",
                "source_urls": [],
            }
            for row in packet["candidates"]
        ],
    }


def _validate_submission(packet: dict, submission: object) -> tuple[str, dict[str, dict]]:
    if not isinstance(submission, dict) or submission.get("schema_version") != 1:
        raise ValueError("invalid reviewer submission")
    if submission.get("packet_sha256") != packet["packet_sha256"]:
        raise ValueError("reviewer submission is for a different packet")
    reviewer = submission.get("reviewer_id")
    if not isinstance(reviewer, str) or not _REVIEWER.fullmatch(reviewer):
        raise ValueError("reviewer_id must be a nonempty pseudonymous identifier")
    timestamp = submission.get("reviewed_at")
    if not isinstance(timestamp, str):
        raise ValueError("reviewed_at must be an ISO-8601 timestamp with timezone")
    try:
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("reviewed_at timestamp is invalid") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("reviewed_at must include a timezone")
    if (submission.get("independent_of_candidate_author_attested") is not True
            or submission.get("original_sources_checked_attested") is not True):
        raise ValueError("independence and original-source review must be self-attested")
    source_rows = {row["id"]: row for row in packet["candidates"]}
    assessments = submission.get("assessments")
    if not isinstance(assessments, list) or not assessments:
        raise ValueError("submission must include at least one completed assessment")
    result = {}
    for item in assessments:
        if not isinstance(item, dict):
            raise ValueError("review assessment must be an object")
        candidate_id = item.get("candidate_id")
        if candidate_id not in source_rows or candidate_id in result:
            raise ValueError("unknown or duplicate candidate assessment")
        if (item.get("decision_quality") not in _DECISION_QUALITY
                or item.get("quote_validity") not in _QUOTE_VALIDITY
                or item.get("adoption_evidence") not in _ADOPTION
                or item.get("verdict") not in _VERDICT
                or not _nonblank(item.get("rationale"))):
            raise ValueError("incomplete or invalid human assessment")
        urls = item.get("source_urls")
        if not isinstance(urls, list) or any(not _nonblank(u) for u in urls) or len(set(urls)) != len(urls):
            raise ValueError("review source URLs must be distinct nonempty links")
        evidence = {e["url"]: e for e in source_rows[candidate_id]["evidence"]}
        if any(u not in evidence for u in urls):
            raise ValueError("review source URL was not part of the candidate packet")
        if item["verdict"] == "accept":
            if (item["decision_quality"] != "real_decision"
                    or item["quote_validity"] != "supported"
                    or item["adoption_evidence"] != "adopted"
                    or not urls or any(evidence[u]["capture_check_status"] == "fail" for u in urls)):
                raise ValueError("accept requires positive judgments and nonfailed cited evidence")
        result[candidate_id] = item
    return reviewer, result


def summarize_review_submissions(packet: dict, submissions: list[dict]) -> dict:
    """Aggregate untrusted self-attestations without verifying real identities."""
    packet = _valid_packet(packet)
    if not isinstance(submissions, list):
        raise ValueError("review submissions must be a list")
    by_candidate: dict[str, list[tuple[str, dict]]] = {row["id"]: [] for row in packet["candidates"]}
    reviewer_ids = set()
    for submission in submissions:
        reviewer, assessments = _validate_submission(packet, submission)
        key = reviewer.casefold()
        if key in reviewer_ids:
            raise ValueError("duplicate reviewer identity in submissions")
        reviewer_ids.add(key)
        for candidate_id, assessment in assessments.items():
            by_candidate[candidate_id].append((reviewer, assessment))
    statuses = Counter()
    results = []
    for row in packet["candidates"]:
        assessments = by_candidate[row["id"]]
        verdicts = [item["verdict"] for _, item in assessments]
        if not verdicts:
            state = "not_run"
        elif len(verdicts) == 1:
            state = "single_review"
        elif len(set(verdicts)) != 1:
            state = "disputed"
        else:
            state = "agreed"
        statuses[state] += 1
        results.append({
            "candidate_id": row["id"],
            "review_state": state,
            "reviewer_count": len(verdicts),
            "verdicts": {reviewer: item["verdict"] for reviewer, item in assessments},
            "self_attested_consensus_verdict": verdicts[0] if state == "agreed" else None,
        })
    dual = statuses["agreed"] + statuses["disputed"]
    return {
        "schema_version": 1,
        "packet_sha256": packet["packet_sha256"],
        "human_review": "not_run" if not submissions else "self_attested_not_identity_verified",
        "identity_verified": False,
        "independent_human_signoff": "not_verified",
        "automatic_acceptance": False,
        "database_review_state_modified": False,
        "model_accuracy": "not_evaluated",
        "candidate_count": len(results),
        "distinct_self_attested_reviewers": len(reviewer_ids),
        "review_state_counts": {s: statuses[s] for s in ("not_run", "single_review", "agreed", "disputed")},
        "verdict_agreement": {"numerator": statuses["agreed"], "denominator": dual, "rate": statuses["agreed"] / dual if dual else None},
        "results": results,
    }
