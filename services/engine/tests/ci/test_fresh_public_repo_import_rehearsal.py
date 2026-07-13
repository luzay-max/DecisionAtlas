from __future__ import annotations

from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.ci import collect_fresh_public_repo_import_rehearsal as rehearsal


CANDIDATES = rehearsal.normalize_candidates(
    ["pallets/itsdangerous", "pytest-dev/pluggy", "python-trio/sniffio"]
)


def test_seeded_candidate_order_is_deterministic() -> None:
    first = [row["repo"] for row in rehearsal.seeded_candidate_order(CANDIDATES, "fixed-seed")]
    second = [row["repo"] for row in rehearsal.seeded_candidate_order(CANDIDATES, "fixed-seed")]

    assert first == second
    assert sorted(first) == sorted(row["repo"] for row in CANDIDATES)
    assert rehearsal.candidate_pool_digest(CANDIDATES) == rehearsal.candidate_pool_digest(list(reversed(CANDIDATES)))


def test_select_fresh_candidate_skips_reused_repository(monkeypatch) -> None:
    ordered = [CANDIDATES[0], CANDIDATES[1]]
    monkeypatch.setattr(rehearsal, "seeded_candidate_order", lambda candidates, seed: ordered)

    def fake_request(**kwargs):
        if "itsdangerous" in kwargs["path"]:
            return {"workspace_exists": True, "workspace_slug": "github-pallets-itsdangerous"}, None
        return {"workspace_exists": False, "workspace_slug": None}, None

    monkeypatch.setattr(rehearsal.public_import, "_json_request", fake_request)

    selected, considered = rehearsal.select_fresh_candidate(
        candidates=ordered,
        seed="seed",
        base_url="http://127.0.0.1:3001",
        session_token=None,
    )

    assert selected["repo"] == "pytest-dev/pluggy"
    assert [row["outcome"] for row in considered] == ["reused_not_eligible", "selected_fresh"]


def test_select_fresh_candidate_preserves_exhausted_pool_reasons(monkeypatch) -> None:
    ordered = [CANDIDATES[0], CANDIDATES[1]]
    monkeypatch.setattr(rehearsal, "seeded_candidate_order", lambda candidates, seed: ordered)
    calls = 0

    def fake_request(**kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            return {"workspace_exists": True, "workspace_slug": "github-pallets-itsdangerous"}, None
        return None, {"type": "url_error", "detail": "connection refused"}

    monkeypatch.setattr(rehearsal.public_import, "_json_request", fake_request)

    selected, considered = rehearsal.select_fresh_candidate(
        candidates=ordered,
        seed="seed",
        base_url="http://127.0.0.1:3001",
        session_token=None,
    )

    assert selected is None
    assert considered[0]["outcome"] == "reused_not_eligible"
    assert considered[1]["outcome"] == "lookup_failed"
    assert considered[1]["classification"] == "local_stack_failure"


def test_collect_rehearsal_composes_successful_fresh_import(monkeypatch, tmp_path) -> None:
    selected = CANDIDATES[1]
    monkeypatch.setattr(
        rehearsal,
        "select_fresh_candidate",
        lambda **kwargs: (selected, [{"repo": selected["repo"], "outcome": "selected_fresh", "lookup": {"workspace_exists": False}}]),
    )
    monkeypatch.setattr(
        rehearsal.public_import,
        "rehearse_public_import",
        lambda **kwargs: {
            "setup": {"outcome": "created", "next_action": "run_benchmark"},
            "repository": {"repo": selected["repo"], "workspace_slug": "github-pytest-dev-pluggy"},
            "import_job": {"job_id": "job-fresh", "status": "succeeded", "imported_count": 17},
        },
    )
    captured = {}

    def fake_core_loop(**kwargs):
        captured.update(kwargs)
        return {
            "status": "warning",
            "accepted_baseline": {"accepted_count": 0, "candidate_count": 2},
            "recommended_next_actions": ["review_candidates"],
        }

    monkeypatch.setattr(rehearsal.core_loop, "build_report", fake_core_loop)

    report = rehearsal.collect_rehearsal(
        root=tmp_path,
        candidates=CANDIDATES,
        seed="seed",
        base_url="http://127.0.0.1:3001",
        session_token=None,
        timeout_seconds=30,
        poll_seconds=0,
        why_question="why",
        evaluate_drift=True,
        run_guardrail=True,
        browser_status="pass",
        browser_summary="Browser verified the same workspace.",
        generated_at="2026-07-10T00:00:00+00:00",
    )

    assert report["fresh_import"]["outcome"] == "fresh_import"
    assert report["summary"]["workspace_slug"] == "github-pytest-dev-pluggy"
    assert report["summary"]["imported_count"] == 17
    assert report["status"] == "warning"
    assert "review_candidates_before_accepted_baseline_claim" in report["recommended_next_actions"]
    assert captured["workspace_slug"] == "github-pytest-dev-pluggy"
    assert captured["import_rehearsal_json"] is None


def test_collect_rehearsal_rejects_lookup_race(monkeypatch, tmp_path) -> None:
    selected = CANDIDATES[0]
    monkeypatch.setattr(rehearsal, "select_fresh_candidate", lambda **kwargs: (selected, []))
    monkeypatch.setattr(
        rehearsal.public_import,
        "rehearse_public_import",
        lambda **kwargs: {
            "setup": {"outcome": "reused", "next_action": "run_benchmark"},
            "repository": {"repo": selected["repo"], "workspace_slug": "github-pallets-itsdangerous"},
            "import_job": None,
        },
    )
    monkeypatch.setattr(rehearsal.core_loop, "build_report", lambda **kwargs: pytest.fail("core loop must not run"))

    report = rehearsal.collect_rehearsal(
        root=tmp_path,
        candidates=CANDIDATES,
        seed="seed",
        base_url="http://127.0.0.1:3001",
        session_token=None,
        timeout_seconds=30,
        poll_seconds=0,
        why_question="why",
        evaluate_drift=False,
        run_guardrail=False,
        browser_status="not_provided",
        browser_summary=None,
    )

    assert report["fresh_import"]["outcome"] == "reuse_race"
    assert report["summary"]["fresh_import"] is False
    assert report["core_loop"] is None
    assert report["status"] == "warning"


@pytest.mark.parametrize("outcome", ["provider_failure", "local_stack_failure"])
def test_collect_rehearsal_preserves_failed_or_timed_out_import(monkeypatch, tmp_path, outcome) -> None:
    selected = CANDIDATES[2]
    monkeypatch.setattr(rehearsal, "select_fresh_candidate", lambda **kwargs: (selected, []))
    monkeypatch.setattr(
        rehearsal.public_import,
        "rehearse_public_import",
        lambda **kwargs: {
            "setup": {"outcome": outcome, "next_action": "inspect_import_failure"},
            "repository": {"repo": selected["repo"], "workspace_slug": "github-python-trio-sniffio"},
            "import_job": {"job_id": "job-failed", "status": "failed" if outcome == "provider_failure" else "running"},
            "error": {"type": "import_failed" if outcome == "provider_failure" else "timeout"},
        },
    )
    monkeypatch.setattr(rehearsal.core_loop, "build_report", lambda **kwargs: pytest.fail("core loop must not run"))

    report = rehearsal.collect_rehearsal(
        root=tmp_path,
        candidates=CANDIDATES,
        seed="seed",
        base_url="http://127.0.0.1:3001",
        session_token=None,
        timeout_seconds=30,
        poll_seconds=0,
        why_question="why",
        evaluate_drift=False,
        run_guardrail=False,
        browser_status="not_provided",
        browser_summary=None,
    )

    assert report["fresh_import"]["outcome"] == outcome
    assert report["import_rehearsal"]["import_job"]["job_id"] == "job-failed"
    assert report["status"] == "warning"


def test_attach_browser_evidence_does_not_repeat_import() -> None:
    source = {
        "evidence_type": "fresh-public-repo-import-rehearsal",
        "fresh_import": {"status": "pass", "outcome": "fresh_import"},
        "core_loop": {"status": "pass", "accepted_baseline": {}, "recommended_next_actions": []},
        "selection": {"selected_repository": "pytest-dev/pluggy"},
        "browser": {"status": "not_provided"},
        "summary": {"fresh_import": True},
    }

    updated = rehearsal.attach_browser_evidence(
        source,
        status="pass",
        summary="Chrome verified review and drift.",
        generated_at="2026-07-10T01:00:00+00:00",
    )

    assert updated["status"] == "pass"
    assert updated["browser"]["summary"] == "Chrome verified review and drift."
    assert updated["summary"]["browser_status"] == "pass"
    assert source["browser"]["status"] == "not_provided"
