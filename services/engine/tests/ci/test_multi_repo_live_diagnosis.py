from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.ci import collect_multi_repo_live_diagnosis as diagnosis


def _write_pool(path: Path) -> Path:
    rows = [
        {"id": "httpx", "repo": "encode/httpx", "workspace_slug": "github-encode-httpx", "priority": "core"},
        {"id": "fastapi", "repo": "fastapi/fastapi", "workspace_slug": "github-fastapi-fastapi", "priority": "core"},
        {"id": "rich", "repo": "Textualize/rich", "workspace_slug": "github-textualize-rich", "priority": "secondary"},
    ]
    path.write_text(json.dumps(rows), encoding="utf-8")
    return path


def test_select_repo_ids_random_is_deterministic(tmp_path: Path) -> None:
    pool = json.loads(_write_pool(tmp_path / "pool.json").read_text(encoding="utf-8"))

    first = diagnosis.select_repo_ids(pool, repo_ids=[], random_count=2, random_seed=7)
    second = diagnosis.select_repo_ids(pool, repo_ids=[], random_count=2, random_seed=7)

    assert first == second
    assert len(first) == 2


def test_select_repo_ids_rejects_unknown(tmp_path: Path) -> None:
    pool = json.loads(_write_pool(tmp_path / "pool.json").read_text(encoding="utf-8"))

    try:
        diagnosis.select_repo_ids(pool, repo_ids=["missing"], random_count=None, random_seed=1)
    except ValueError as exc:
        assert "Unknown repository id" in str(exc)
    else:
        raise AssertionError("Expected unknown repository to fail")


def test_multi_repo_diagnosis_preserves_mixed_outcomes(monkeypatch, tmp_path: Path) -> None:
    pool_path = _write_pool(tmp_path / "pool.json")

    def fake_public_import(**kwargs):
        repo = kwargs["repository"]["repo"]
        if repo == "encode/httpx":
            return {
                "repository": {"repo": repo, "workspace_slug": "github-encode-httpx"},
                "setup": {"outcome": "reused", "next_action": "run_benchmark"},
            }
        return {
            "repository": {"repo": repo, "workspace_slug": "github-fastapi-fastapi"},
            "setup": {"outcome": "provider_failure", "next_action": "retry_when_github_or_network_available"},
            "error": {"type": "import_failed"},
        }

    def fake_core_loop(**kwargs):
        workspace_slug = kwargs["workspace_slug"]
        if workspace_slug == "github-encode-httpx":
            return {
                "status": "pass",
                "lanes": {
                    "review": {"status": "pass"},
                    "why_search": {"status": "pass"},
                    "drift": {"status": "pass"},
                    "guardrail": {"status": "pass"},
                },
                "summary": {
                    "pass_lanes": 6,
                    "warning_lanes": 0,
                    "blocking_lanes": 0,
                    "action_categories": {
                        "product_controlled": 0,
                        "operator_setup": 0,
                        "external_dependency": 0,
                        "not_provided": 0,
                        "blocking": 0,
                    },
                },
                "recommended_next_actions": ["probe_core_loop"],
            }
        return {
            "status": "warning",
            "lanes": {
                "review": {"status": "warning"},
                "why_search": {"status": "warning"},
                "drift": {"status": "not_provided"},
                "guardrail": {"status": "not_provided"},
            },
            "summary": {
                "pass_lanes": 1,
                "warning_lanes": 4,
                "blocking_lanes": 0,
                "action_categories": {
                    "product_controlled": 0,
                    "operator_setup": 2,
                    "external_dependency": 0,
                    "not_provided": 2,
                    "blocking": 0,
                },
                "grounding_summary": {
                    "warning_lanes_with_grounding": 2,
                    "reason_codes": ["missing_accepted_decision_evidence", "unknown_grounding_gap"],
                },
            },
            "lane_reasons": {
                "why_search": [{"code": "missing_accepted_decision_evidence", "summary": "Why evidence is weak."}],
                "drift": [{"code": "unknown_grounding_gap", "summary": "Drift was not evaluated cleanly."}],
            },
            "recommended_next_actions": ["retry_when_github_or_network_available"],
        }

    monkeypatch.setattr(diagnosis.public_import, "rehearse_public_import", fake_public_import)
    monkeypatch.setattr(diagnosis.core_loop, "build_report", fake_core_loop)

    report = diagnosis.build_report(
        root=ROOT,
        pool_path=pool_path,
        base_url="http://127.0.0.1:3001",
        repo_ids=["httpx", "fastapi"],
        random_count=None,
        random_seed=1,
    )

    assert report["status"] == "blocking"
    assert report["summary"]["pass"] == 1
    assert report["summary"]["blocking"] == 1
    assert report["summary"]["action_categories"]["blocking"] == 1
    assert report["summary"]["action_categories"]["external_dependency"] == 1
    assert report["summary"]["grounding_reason_codes"] == ["missing_accepted_decision_evidence", "unknown_grounding_gap"]
    assert report["repositories"][0]["repo"] == "encode/httpx"
    assert report["repositories"][1]["setup_outcome"] == "provider_failure"
    assert report["repositories"][1]["lane_reasons"]["why_search"][0]["code"] == "missing_accepted_decision_evidence"


def test_render_markdown_lists_lane_statuses() -> None:
    report = {
        "generated_at": "now",
        "status": "warning",
        "base_url": "http://127.0.0.1:3001",
        "selected_repo_ids": ["httpx"],
        "summary": {"pass": 0, "warning": 1, "blocking": 0},
        "repositories": [
            {
                "repo": "encode/httpx",
                "status": "warning",
                "setup_outcome": "reused",
                "core_loop_status": "warning",
                "lane_statuses": {"review": "warning", "why_search": "warning", "drift": "pass", "guardrail": "not_provided"},
                "grounding_summary": {"warning_lanes_with_grounding": 1, "reason_codes": ["weak_why_support"]},
                "action_categories": {"product_controlled": 2, "operator_setup": 0},
            }
        ],
        "recommended_follow_up": ["review_candidates"],
        "sensitive_material_note": "no secrets",
    }

    markdown = diagnosis.render_markdown(report)

    assert "encode/httpx" in markdown
    assert "| encode/httpx | warning | reused | warning | warning | warning | pass | not_provided | {\"reason_codes\": [\"weak_why_support\"], \"warning_lanes_with_grounding\": 1} | 2 | 0 |" in markdown
    assert "review_candidates" in markdown
