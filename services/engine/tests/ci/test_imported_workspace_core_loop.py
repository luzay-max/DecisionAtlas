from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.ci import collect_imported_workspace_core_loop as core_loop


def _write_json(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_core_loop_collects_clean_imported_workspace(monkeypatch, tmp_path: Path) -> None:
    import_report = _write_json(
        tmp_path / "public-import.json",
        {
            "repository": {"repo": "fastapi/fastapi", "workspace_slug": "github-fastapi-fastapi"},
            "setup": {"outcome": "reused"},
        },
    )
    guardrail_report = _write_json(
        tmp_path / "guardrail.json",
        {"guardrail": {"agent_status": "continue", "diff_status": "clean", "drift_status": "clean"}},
    )

    def fake_json_request(**kwargs):
        path = kwargs["path"]
        if path.startswith("/dashboard/summary?"):
            return (
                {
                    "workspace_slug": "github-fastapi-fastapi",
                    "github_repo": "fastapi/fastapi",
                    "workspace_mode": "imported",
                    "import_status": "succeeded",
                    "decision_counts": {"candidate": 2, "accepted": 1},
                    "drift_status": {"state": "clean"},
                    "workspace_readiness": {"state": "review_ready"},
                },
                None,
            )
        if path.startswith("/decisions?"):
            return ([{"title": "Use Pydantic models"}, {"title": "Keep async endpoints"}], None)
        if path == "/query/why":
            return (
                {
                    "status": "ok",
                    "question": kwargs["body"]["question"],
                    "answer_context": {"workspace_mode": "imported"},
                    "citations": [{"quote": "Use Pydantic models", "url": "https://github.com/fastapi/fastapi/pull/1"}],
                    "primary_decision": {"decision_id": 1, "title": "Use Pydantic models"},
                },
                None,
            )
        if path.startswith("/drift?"):
            return ({"workspace_mode": "imported", "evaluation": {"state": "clean"}, "alerts": []}, None)
        raise AssertionError(f"unexpected path {path}")

    monkeypatch.setattr(core_loop, "_json_request", fake_json_request)

    report = core_loop.build_report(
        root=ROOT,
        base_url="http://127.0.0.1:3001",
        repo=None,
        workspace_slug=None,
        import_rehearsal_json=import_report,
        guardrail_json=guardrail_report,
        run_guardrail=False,
        session_token=None,
        why_question="why use pydantic",
        evaluate_drift=False,
        generated_at="2026-07-03T00:00:00+00:00",
    )

    assert report["status"] == "pass"
    assert report["repository"]["repo"] == "fastapi/fastapi"
    assert report["lanes"]["dashboard"]["details"]["workspace_mode"] == "imported"
    assert report["lanes"]["review"]["details"]["candidate_count"] == 2
    assert report["lanes"]["why_search"]["details"]["citation_count"] == 1
    assert report["lanes"]["drift"]["details"]["drift_state"] == "clean"
    assert report["lanes"]["guardrail"]["status"] == "pass"


def test_core_loop_preserves_missing_workspace_as_warning(tmp_path: Path) -> None:
    report = core_loop.build_report(
        root=ROOT,
        base_url="http://127.0.0.1:3001",
        repo="fastapi/fastapi",
        workspace_slug=None,
        import_rehearsal_json=None,
        guardrail_json=None,
        run_guardrail=False,
        session_token=None,
        why_question="why",
        evaluate_drift=False,
        generated_at="2026-07-03T00:00:00+00:00",
    )

    assert report["status"] == "warning"
    assert report["lanes"]["setup"]["status"] == "warning"
    assert report["lanes"]["dashboard"]["status"] == "not_provided"
    assert "run_public_import_rehearsal" in report["recommended_next_actions"]


def test_core_loop_classifies_partial_lanes(monkeypatch, tmp_path: Path) -> None:
    guardrail_report = _write_json(tmp_path / "guardrail.json", {"guardrail": {"agent_status": "caution"}})

    def fake_json_request(**kwargs):
        path = kwargs["path"]
        if path.startswith("/dashboard/summary?"):
            return (
                {
                    "workspace_slug": "github-example-repo",
                    "github_repo": "example/repo",
                    "workspace_mode": "imported",
                    "import_status": "succeeded",
                    "decision_counts": {"candidate": 0, "accepted": 0},
                },
                None,
            )
        if path.startswith("/decisions?"):
            return ([], None)
        if path == "/query/why":
            return ({"status": "evidence_limited", "citations": [], "answer_context": {"workspace_mode": "imported"}}, None)
        if path.startswith("/drift?"):
            return (None, {"type": "url_error", "detail": "connection refused"})
        raise AssertionError(f"unexpected path {path}")

    monkeypatch.setattr(core_loop, "_json_request", fake_json_request)

    report = core_loop.build_report(
        root=ROOT,
        base_url="http://127.0.0.1:3001",
        repo="example/repo",
        workspace_slug="github-example-repo",
        import_rehearsal_json=None,
        guardrail_json=guardrail_report,
        run_guardrail=False,
        session_token=None,
        why_question="why",
        evaluate_drift=False,
        generated_at="2026-07-03T00:00:00+00:00",
    )

    assert report["status"] == "blocking"
    assert report["lanes"]["review"]["status"] == "warning"
    assert report["lanes"]["why_search"]["status"] == "warning"
    assert report["lanes"]["drift"]["status"] == "local_stack_failure"
    assert report["lanes"]["guardrail"]["status"] == "warning"


def test_core_loop_markdown_is_compact() -> None:
    report = {
        "generated_at": "now",
        "status": "warning",
        "base_url": "http://127.0.0.1:3001",
        "repository": {"repo": "fastapi/fastapi", "workspace_slug": "github-fastapi-fastapi"},
        "lanes": {"setup": {"status": "pass", "summary": "ready", "next_action": "probe_core_loop"}},
        "recommended_next_actions": ["probe_core_loop"],
        "sensitive_material_note": "no secrets",
    }

    markdown = core_loop.render_markdown(report)

    assert "fastapi/fastapi" in markdown
    assert "| setup | pass | ready | probe_core_loop |" in markdown
    assert "no secrets" in markdown
