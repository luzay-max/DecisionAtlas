from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[4]
    module_path = root / "scripts" / "ci" / "review_candidates_into_accepted_baseline.py"
    spec = importlib.util.spec_from_file_location("review_candidates_into_accepted_baseline", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_review_candidates_dry_run_does_not_mutate(monkeypatch) -> None:
    collector = _load_module()
    calls: list[dict] = []

    def fake_json_request(**kwargs):
        calls.append(kwargs)
        path = kwargs["path"]
        if path.endswith("review_state=candidate"):
            return ([{"id": 10, "title": "Candidate A", "review_state": "candidate", "confidence": 0.9}], None)
        if path.endswith("review_state=accepted"):
            return ([], None)
        raise AssertionError(f"unexpected path {path}")

    monkeypatch.setattr(collector, "_json_request", fake_json_request)

    report = collector.build_report(
        base_url="http://127.0.0.1:3001",
        workspace_slug="github-textualize-rich",
        max_accept=1,
        confirm_accept=False,
        review_rationale=None,
        session_token=None,
        generated_at="2026-07-08T00:00:00+00:00",
    )

    assert report["status"] == "pass"
    assert report["mode"] == "dry_run"
    assert report["before"]["candidate_count"] == 1
    assert report["after"]["accepted_count"] == 0
    assert report["selected_candidates"][0]["id"] == 10
    assert all("/review" not in call["path"] for call in calls)


def test_review_candidates_confirm_accepts_bounded_candidates(monkeypatch) -> None:
    collector = _load_module()
    accepted_after_calls = 0

    def fake_json_request(**kwargs):
        nonlocal accepted_after_calls
        path = kwargs["path"]
        if path.endswith("review_state=candidate"):
            return (
                [
                    {"id": 10, "title": "Candidate A", "review_state": "candidate", "confidence": 0.9},
                    {"id": 11, "title": "Candidate B", "review_state": "candidate", "confidence": 0.8},
                ],
                None,
            )
        if path.endswith("review_state=accepted"):
            accepted_after_calls += 1
            return (([] if accepted_after_calls == 1 else [{"id": 10, "title": "Candidate A", "review_state": "accepted"}]), None)
        if path == "/decisions/10/review":
            assert kwargs["method"] == "POST"
            assert kwargs["body"]["review_state"] == "accepted"
            assert kwargs["body"]["review_rationale"] == "Source-backed baseline seed."
            return ({"id": 10, "title": "Candidate A", "review_state": "accepted"}, None)
        raise AssertionError(f"unexpected path {path}")

    monkeypatch.setattr(collector, "_json_request", fake_json_request)

    report = collector.build_report(
        base_url="http://127.0.0.1:3001",
        workspace_slug="github-textualize-rich",
        max_accept=1,
        confirm_accept=True,
        review_rationale="Source-backed baseline seed.",
        session_token=None,
    )

    assert report["status"] == "pass"
    assert report["mode"] == "confirmed_accept"
    assert report["accepted_decisions"][0]["id"] == 10
    assert report["before"]["candidate_count"] == 2
    assert report["after"]["accepted_count"] == 1


def test_review_candidates_requires_rationale_for_confirm() -> None:
    collector = _load_module()

    try:
        collector.build_report(
            base_url="http://127.0.0.1:3001",
            workspace_slug="github-textualize-rich",
            max_accept=1,
            confirm_accept=True,
            review_rationale=None,
            session_token=None,
        )
    except ValueError as exc:
        assert "review-rationale" in str(exc)
    else:
        raise AssertionError("Expected confirm accept without rationale to fail")


def test_review_candidates_reports_api_failure(monkeypatch, tmp_path: Path) -> None:
    collector = _load_module()

    def fake_json_request(**kwargs):
        path = kwargs["path"]
        if path.endswith("review_state=candidate"):
            return ([{"id": 10, "title": "Candidate A", "review_state": "candidate"}], None)
        if path.endswith("review_state=accepted"):
            return ([], None)
        if path == "/decisions/10/review":
            return (None, {"type": "http_error", "status": 403, "detail": "forbidden"})
        raise AssertionError(f"unexpected path {path}")

    monkeypatch.setattr(collector, "_json_request", fake_json_request)

    report = collector.build_report(
        base_url="http://127.0.0.1:3001",
        workspace_slug="github-textualize-rich",
        max_accept=1,
        confirm_accept=True,
        review_rationale="Source-backed baseline seed.",
        session_token=None,
    )
    markdown = collector.render_markdown(report)

    assert report["status"] == "blocking"
    assert report["errors"][0]["status"] == 403
    assert "forbidden" in json.dumps(report["errors"])
    assert "Candidate A" in markdown
