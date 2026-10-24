"""Self-attested review workflow: synthetic offline assertions, no human identities."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from app.extractor.human_evidence_review import (
    blank_reviewer_template, prepare_review_packet, summarize_review_submissions,
)

ROOT = Path(__file__).resolve().parents[4]
CLI = ROOT / "scripts/eval/human_evidence_review.py"
URL = "https://github.com/example/public/blob/" + "a" * 40 + "/README.md"
PR = "https://github.com/example/public/pull/1"


def inputs():
    snapshot = {
        "schema_version": 1, "scope": "operator_approved_local_public_sqlite_snapshot",
        "workspace": {"slug": "only-public", "repo_url": "https://github.com/example/public"},
        "candidate_count": 2,
        "rows": [
            {"stored_review_state": "accepted", "candidate": {
                "id": "decision-a", "provider_kind": "fake", "title": "Use a documented cache",
                "problem": "Repeated reads slow us down", "chosen_option": "Use local cache",
                "tradeoffs": "Invalidation maintenance", "citations": [
                    {"url": URL, "quote": "Local cache chosen.", "start": 0, "end": 19,
                     "snapshot_text": "Local cache chosen.", "snapshot_sha256": hashlib.sha256(b"Local cache chosen.").hexdigest()},
                ],
            }},
            {"stored_review_state": "candidate", "candidate": {
                "id": "decision-b", "provider_kind": "fake", "title": "Rejected proposal",
                "problem": "Need compatibility", "chosen_option": "Proposal from PR",
                "tradeoffs": "Risk of change", "citations": [
                    {"url": PR, "quote": "Propose a new type", "merged": None},
                ],
            }},
        ],
    }
    verified = {
        "schema_version": 1, "basis": "operator_supplied_public_capture_not_live_verification",
        "source_authenticity": "capture_not_independently_attested",
        "human_review": "not_run", "model_accuracy": "not_evaluated",
        "candidate_count": 2,
        "results": [
            {"id": "decision-a", "automatic_acceptance": False, "review_required": True,
             "checks": [{"citation_index": 0, "url": URL, "status": "pass", "reason": "span_in_recorded_git_blob"}]},
            {"id": "decision-b", "automatic_acceptance": False, "review_required": True,
             "checks": [{"citation_index": 0, "url": PR, "status": "fail", "reason": "unmerged_proposal_not_adoption"}]},
        ],
    }
    return snapshot, verified


def packet():
    return prepare_review_packet(*inputs())


def submission(p, reviewer="reviewer-a", candidate="decision-a", verdict="accept"):
    source_url = URL if candidate == "decision-a" else PR
    return {
        "schema_version": 1, "packet_sha256": p["packet_sha256"],
        "reviewer_id": reviewer, "reviewed_at": "2026-10-24T13:00:00Z",
        "independent_of_candidate_author_attested": True,
        "original_sources_checked_attested": True,
        "assessments": [{
            "candidate_id": candidate, "decision_quality": "real_decision",
            "quote_validity": "supported", "adoption_evidence": "adopted",
            "verdict": verdict, "rationale": "Personally read the cited public source.",
            "source_urls": [source_url],
        }],
    }


def test_prepare_is_repeatable_and_does_not_sign_existing_review_state():
    a, b = inputs()
    originals = copy.deepcopy((a, b))
    result = prepare_review_packet(a, b)
    assert result == prepare_review_packet(a, b)
    assert (a, b) == originals
    assert result["candidate_count"] == 2
    assert result["human_review"] == "not_run"
    assert result["reviewer_identity_verification"] == "not_provided"
    assert result["model_accuracy"] == "not_evaluated"
    first = result["candidates"][0]
    assert first["stored_review_state"] == "accepted"
    assert first["evidence"][0]["quote"] == "Local cache chosen."
    assert first["evidence"][0]["capture_check_status"] == "pass"
    assert "snapshot_text" not in first["evidence"]  # Minimize sensitive export.
    assert result["packet_sha256"] == hashlib.sha256(
        json.dumps(
            {k: v for k, v in result.items() if k != "packet_sha256"},
            sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def test_blank_template_is_never_a_completed_review():
    p = packet()
    blank = blank_reviewer_template(p)
    assert blank["packet_sha256"] == p["packet_sha256"]
    assert blank["reviewer_id"] == ""
    assert blank["independent_of_candidate_author_attested"] is False
    assert all(x["verdict"] is None for x in blank["assessments"])
    with pytest.raises(ValueError, match="reviewer_id"):
        summarize_review_submissions(p, [blank])


def test_no_submissions_remain_not_run_without_spurious_accuracy():
    summary = summarize_review_submissions(packet(), [])
    assert summary["human_review"] == "not_run"
    assert summary["identity_verified"] is False
    assert summary["independent_human_signoff"] == "not_verified"
    assert summary["model_accuracy"] == "not_evaluated"
    assert summary["automatic_acceptance"] is False
    assert summary["verdict_agreement"] == {"numerator": 0, "denominator": 0, "rate": None}
    assert summary["review_state_counts"] == {"not_run": 2, "single_review": 0, "agreed": 0, "disputed": 0}


def test_two_self_attested_reviews_agree_but_do_not_verify_identity_or_accept_db():
    p = packet()
    outcome = summarize_review_submissions(p, [submission(p), submission(p, "reviewer-b")])
    assert outcome["human_review"] == "self_attested_not_identity_verified"
    assert outcome["distinct_self_attested_reviewers"] == 2
    assert outcome["identity_verified"] is False
    assert outcome["database_review_state_modified"] is False
    assert outcome["verdict_agreement"] == {"numerator": 1, "denominator": 1, "rate": 1.0}
    assert outcome["review_state_counts"]["agreed"] == 1
    assert outcome["review_state_counts"]["not_run"] == 1
    assert outcome["results"][0]["self_attested_consensus_verdict"] == "accept"


def test_disagreement_is_reported_and_not_silently_accepted():
    p = packet()
    a = submission(p)
    b = submission(p, "reviewer-b", verdict="uncertain")
    report = summarize_review_submissions(p, [a, b])
    assert report["review_state_counts"]["disputed"] == 1
    assert report["verdict_agreement"] == {"numerator": 0, "denominator": 1, "rate": 0}
    assert report["results"][0]["self_attested_consensus_verdict"] is None


def test_single_review_is_not_quorum():
    p = packet()
    report = summarize_review_submissions(p, [submission(p)])
    assert report["review_state_counts"]["single_review"] == 1
    assert report["verdict_agreement"]["rate"] is None


def test_declared_independence_cannot_be_assumed_without_attestations():
    p = packet()
    for key in ("independent_of_candidate_author_attested", "original_sources_checked_attested"):
        entry = submission(p)
        entry[key] = False
        with pytest.raises(ValueError, match="self-attested"):
            summarize_review_submissions(p, [entry])


@pytest.mark.parametrize("timestamp", ["2026-10-24", "not-a-date", None, "2026-10-24T13:00:00"])
def test_review_time_requires_valid_timezone(timestamp):
    p = packet()
    entry = submission(p)
    entry["reviewed_at"] = timestamp
    with pytest.raises(ValueError, match="reviewed_at"):
        summarize_review_submissions(p, [entry])


def test_reviewer_identity_must_be_unique_case_insensitively():
    p = packet()
    with pytest.raises(ValueError, match="duplicate reviewer"):
        summarize_review_submissions(p, [submission(p, "Alice"), submission(p, "alice")])


def test_candidate_id_and_source_urls_are_bound_to_packet():
    p = packet()
    wrong_id = submission(p)
    wrong_id["assessments"][0]["candidate_id"] = "unknown"
    with pytest.raises(ValueError, match="candidate"):
        summarize_review_submissions(p, [wrong_id])
    wrong_source = submission(p)
    wrong_source["assessments"][0]["source_urls"] = ["https://github.com/other/private"]
    with pytest.raises(ValueError, match="not part"):
        summarize_review_submissions(p, [wrong_source])


def test_claimed_acceptance_rejected_for_failed_capture():
    p = packet()
    with pytest.raises(ValueError, match="nonfailed cited evidence"):
        summarize_review_submissions(p, [submission(p, candidate="decision-b")])


@pytest.mark.parametrize("field,new_value", [
    ("decision_quality", "not_a_decision"),
    ("quote_validity", "unsupported"),
    ("adoption_evidence", "unknown"),
    ("source_urls", []),
])
def test_acceptance_requires_explicit_positive_reasoning(field, new_value):
    p = packet()
    entry = submission(p)
    entry["assessments"][0][field] = new_value
    with pytest.raises(ValueError, match="accept requires"):
        summarize_review_submissions(p, [entry])


def test_blank_or_duplicated_assessments_are_invalid():
    p = packet()
    empty = submission(p)
    empty["assessments"] = []
    with pytest.raises(ValueError, match="completed assessment"):
        summarize_review_submissions(p, [empty])
    repeat = submission(p)
    repeat["assessments"].append(copy.deepcopy(repeat["assessments"][0]))
    with pytest.raises(ValueError, match="duplicate"):
        summarize_review_submissions(p, [repeat])


def test_fingerprint_rejects_tampered_packet_and_stale_submission():
    p = packet()
    a = submission(p)
    stale = copy.deepcopy(p)
    stale["candidates"][0]["problem"] = "tampered"
    with pytest.raises(ValueError, match="fingerprint"):
        summarize_review_submissions(stale, [a])
    fresh = prepare_review_packet(*inputs())
    fresh["candidates"][0]["problem"] = "changed"
    fresh["packet_sha256"] = hashlib.sha256(
        json.dumps({k: v for k, v in fresh.items() if k != "packet_sha256"},
                   sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    with pytest.raises(ValueError, match="different packet"):
        summarize_review_submissions(fresh, [a])


def test_prepare_rejects_cross_candidate_citation_and_implicit_acceptance():
    a, b = inputs()
    b["results"][0]["checks"][0]["url"] = PR
    with pytest.raises(ValueError, match="citation"):
        prepare_review_packet(a, b)
    a, b = inputs()
    b["results"][0]["automatic_acceptance"] = True
    with pytest.raises(ValueError, match="automatically"):
        prepare_review_packet(a, b)


def test_prepare_rejects_duplicate_candidate_ids_and_unverified_inputs():
    a, b = inputs()
    a["rows"][1]["candidate"]["id"] = "decision-a"
    b["results"][1]["id"] = "decision-a"
    with pytest.raises(ValueError, match="duplicate"):
        prepare_review_packet(a, b)
    a, b = inputs()
    b["source_authenticity"] = "verified"
    with pytest.raises(ValueError, match="Phase-B"):
        prepare_review_packet(a, b)


def test_cli_prepare_template_and_zero_review_summary(tmp_path):
    source, upstream = inputs()
    source_path = tmp_path / "phase-a.json"
    verify_path = tmp_path / "phase-b.json"
    source_path.write_text(json.dumps(source), encoding="utf-8")
    verify_path.write_text(json.dumps(upstream), encoding="utf-8")

    def run(*args):
        return subprocess.run([sys.executable, str(CLI), *map(str, args)], capture_output=True)

    packet_path = tmp_path / "packet.json"
    prepare = ("prepare", "--snapshot", source_path, "--verification", verify_path, "--output", packet_path)
    assert run(*prepare).returncode != 0
    assert run(*prepare, "--approve-public-data").returncode == 0
    prior = packet_path.read_bytes()
    assert run(*prepare, "--approve-public-data").returncode != 0
    assert packet_path.read_bytes() == prior
    p = json.loads(prior)
    template_path = tmp_path / "blank.json"
    assert run("template", "--packet", packet_path, "--output", template_path, "--approve-public-data").returncode == 0
    assert json.loads(template_path.read_text())["reviewer_id"] == ""
    summary_path = tmp_path / "summary.json"
    assert run("summarize", "--packet", packet_path, "--output", summary_path, "--approve-public-data").returncode == 0
    assert json.loads(summary_path.read_text())["human_review"] == "not_run"

    internal = ROOT / "artifacts" / "must-not-write-review.json"
    assert run("template", "--packet", packet_path, "--output", internal, "--approve-public-data").returncode != 0
    assert not internal.exists()


def test_cli_rejects_blank_submission_and_malformed_input_without_output(tmp_path):
    p = packet()
    packet_path = tmp_path / "packet.json"
    packet_path.write_text(json.dumps(p), encoding="utf-8")
    blank = tmp_path / "blank.json"
    blank.write_text(json.dumps(blank_reviewer_template(p)), encoding="utf-8")
    output = tmp_path / "out.json"
    args = [sys.executable, str(CLI), "summarize", "--packet", str(packet_path),
            "--submission", str(blank), "--output", str(output), "--approve-public-data"]
    assert subprocess.run(args, capture_output=True).returncode == 2
    assert not output.exists()
