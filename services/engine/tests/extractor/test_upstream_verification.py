"""Offline tests for pinned public Git blob and captured PR status comparisons."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from app.extractor.upstream_verification import evaluate_public_capture

ROOT = Path(__file__).resolve().parents[4]
FIXTURE = ROOT / "services/engine/tests/fixtures/upstream_evidence/pallets-click-public-captures.json"
CLI = ROOT / "scripts/eval/verify_public_evidence.py"
CAPTURE = json.loads(FIXTURE.read_text(encoding="utf-8"))
DOC = CAPTURE["sources"][0]
UNMERGED = CAPTURE["sources"][1]
MERGED = CAPTURE["sources"][2]


def snapshot(*citations):
    return {
        "schema_version": 1,
        "scope": "operator_approved_local_public_sqlite_snapshot",
        "workspace": {"slug": "click-public", "repo_url": "https://github.com/pallets/click"},
        "rows": [{
            "candidate": {
                "id": "candidate-1", "provider_kind": "unknown",
                "citations": [dict(item) for item in citations],
            },
            "stored_review_state": "candidate",
        }],
    }


def doc_ref():
    content = DOC["content"]
    quote = "Do not add unnecessary dependencies."
    start = content.index(quote)
    return {
        "url": DOC["url"], "kind": "doc", "quote": quote,
        "start": start, "end": start + len(quote), "snapshot_text": content,
        "snapshot_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
    }


def pr_ref(entry):
    return {"url": entry["url"], "kind": "pull_request", "merged": None}


def checked(*citations):
    return evaluate_public_capture(snapshot(*citations), CAPTURE)


def test_real_public_blob_matches_pinned_git_object_and_exact_quote():
    report = checked(doc_ref())
    row = report["results"][0]
    assert row["checks"][0]["status"] == "pass"
    assert row["checks"][0]["reason"] == "span_in_recorded_git_blob"
    assert row["diagnostic_status"] == "review_required"
    assert row["automatic_acceptance"] is False
    assert row["review_required"] is True
    assert report["source_authenticity"] == "capture_not_independently_attested"
    assert report["human_review"] == "not_run"


def test_real_2559_was_closed_unmerged_not_automatically_adopted():
    assert UNMERGED["number"] == 2559
    assert UNMERGED["state"] == "closed"
    assert UNMERGED["merged"] is False
    # The GitHub API can report a merge_commit_sha even on an unmerged PR.
    assert UNMERGED["merge_commit_sha"]
    row = checked(pr_ref(UNMERGED))["results"][0]
    assert row["diagnostic_status"] == "fail"
    assert row["checks"][0]["reason"] == "unmerged_proposal_not_adoption"


def test_real_2562_merged_does_not_mean_human_decision_acceptance():
    assert MERGED["number"] == 2562
    assert MERGED["state"] == "closed"
    assert MERGED["merged"] is True
    row = checked(pr_ref(MERGED))["results"][0]
    assert row["checks"][0]["status"] == "not_evaluated"
    assert row["checks"][0]["reason"] == "merged_still_requires_human_review"
    assert row["automatic_acceptance"] is False


def test_stored_snapshot_differs_from_recorded_fixed_blob():
    ref = doc_ref()
    ref["snapshot_text"] = ref["snapshot_text"] + " modified"
    row = checked(ref)["results"][0]
    assert row["checks"][0]["reason"] == "stored_artifact_differs_from_capture"
    assert row["diagnostic_status"] == "fail"



def test_recorded_content_hash_conflicts_with_phase_a_hash():
    ref = doc_ref()
    ref["snapshot_sha256"] = "0" * 64
    row = checked(ref)["results"][0]
    assert row["checks"][0]["reason"] == "stored_snapshot_hash_mismatch"
    assert row["diagnostic_status"] == "fail"


def test_stored_merge_claim_must_agree_with_captured_state():
    ref = pr_ref(UNMERGED)
    ref["merged"] = True
    row = checked(ref)["results"][0]
    assert row["checks"][0]["reason"] == "stored_merge_state_conflicts_with_capture"
    assert row["diagnostic_status"] == "fail"


def test_wrong_quote_span_fails_even_if_text_matches():
    ref = doc_ref()
    ref["start"] += 1
    row = checked(ref)["results"][0]
    assert row["checks"][0]["reason"] == "quote_or_span_mismatch"
    assert row["diagnostic_status"] == "fail"


def test_missing_capture_remains_not_evaluated():
    ref = doc_ref()
    ref["url"] = "https://github.com/pallets/click/blob/" + "b" * 40 + "/docs/another.md"
    row = checked(ref)["results"][0]
    assert row["checks"][0]["reason"] == "upstream_capture_missing"
    assert row["checks"][0]["status"] == "not_evaluated"


def test_wrong_source_type_fails():
    ref = pr_ref(MERGED)
    ref["kind"] = "doc"
    row = checked(ref)["results"][0]
    assert row["checks"][0]["reason"] == "source_kind_mismatch"


def test_git_blob_sha_must_match_recorded_original_bytes():
    manifest = copy.deepcopy(CAPTURE)
    manifest["sources"][0]["content"] += "tampered"
    with pytest.raises(ValueError, match="Git blob content differs"):
        evaluate_public_capture(snapshot(doc_ref()), manifest)


@pytest.mark.parametrize("mutator", [
    lambda m: m["sources"][1].update(merged=True, state="open"),
    lambda m: m["sources"][1].update(number=2562),
    lambda m: m["sources"][0].update(commit_sha="b" * 40),
    lambda m: m["sources"].append(copy.deepcopy(m["sources"][0])),
    lambda m: m.update(repository="other/private"),
])
def test_invalid_or_conflicting_capture_fails_closed(mutator):
    manifest = copy.deepcopy(CAPTURE)
    mutator(manifest)
    with pytest.raises(ValueError):
        evaluate_public_capture(snapshot(doc_ref()), manifest)


def test_snapshot_must_be_public_and_same_workspace():
    exported = snapshot(doc_ref())
    exported["workspace"]["repo_url"] = "https://github.com/private/repo"
    with pytest.raises(ValueError, match="mismatched"):
        evaluate_public_capture(exported, CAPTURE)
    exported["workspace"]["repo_url"] = "https://github.com/pallets/click"
    exported["scope"] = "unknown"
    with pytest.raises(ValueError, match="reviewed public"):
        evaluate_public_capture(exported, CAPTURE)


def test_report_does_not_mutate_input_or_upgrade_reviews():
    exported = snapshot(doc_ref(), pr_ref(UNMERGED), pr_ref(MERGED))
    before = copy.deepcopy(exported)
    report = evaluate_public_capture(exported, CAPTURE)
    assert exported == before
    assert report["citation_status_counts"] == {"pass": 1, "fail": 1, "not_evaluated": 1}
    assert all(row["automatic_acceptance"] is False for row in report["results"])
    assert report["model_accuracy"] == "not_evaluated"


def test_cli_exit_codes_and_exclusive_output(tmp_path):
    phase_a = tmp_path / "source.json"
    phase_a.write_text(json.dumps(snapshot(doc_ref(), pr_ref(MERGED))), encoding="utf-8")
    output = tmp_path / "verified.json"
    cmd = [
        sys.executable, str(CLI), "--snapshot", str(phase_a),
        "--manifest", str(FIXTURE), "--output", str(output),
    ]
    assert subprocess.run(cmd, capture_output=True).returncode != 0
    assert not output.exists()
    assert subprocess.run(cmd + ["--approve-public-data"], capture_output=True).returncode == 0
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["citation_status_counts"] == {"pass": 1, "not_evaluated": 1}
    original = output.read_bytes()
    assert subprocess.run(cmd + ["--approve-public-data"], capture_output=True).returncode != 0
    assert output.read_bytes() == original

    bad_data = tmp_path / "bad_source.json"
    bad_data.write_text(json.dumps(snapshot(pr_ref(UNMERGED))), encoding="utf-8")
    bad_output = tmp_path / "bad_report.json"
    bad_cmd = [
        sys.executable, str(CLI), "--snapshot", str(bad_data),
        "--manifest", str(FIXTURE), "--output", str(bad_output), "--approve-public-data",
    ]
    assert subprocess.run(bad_cmd, capture_output=True).returncode == 1
    assert json.loads(bad_output.read_text(encoding="utf-8"))["citation_status_counts"]["fail"] == 1

    checkout_output = ROOT / "artifacts" / "never-public-evidence-report.json"
    assert subprocess.run(
        cmd[:cmd.index("--output") + 1] + [str(checkout_output), "--approve-public-data"],
        capture_output=True,
    ).returncode != 0
    assert not checkout_output.exists()


def test_cli_rejects_invalid_capture_before_output(tmp_path):
    input_file = tmp_path / "input.json"
    input_file.write_text(json.dumps(snapshot(doc_ref())), encoding="utf-8")
    bad_manifest = tmp_path / "bad.json"
    bad_manifest.write_text('{"schema_version":1,"sources":[]}', encoding="utf-8")
    output = tmp_path / "output.json"
    cmd = [
        sys.executable, str(CLI), "--snapshot", str(input_file), "--manifest", str(bad_manifest),
        "--output", str(output), "--approve-public-data",
    ]
    assert subprocess.run(cmd, capture_output=True).returncode == 2
    assert not output.exists()
