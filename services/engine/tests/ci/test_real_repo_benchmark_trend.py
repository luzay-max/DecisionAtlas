from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_trend_module():
    root = Path(__file__).resolve().parents[4]
    module_path = root / "scripts" / "ci" / "collect_real_repo_benchmark_trend.py"
    spec = importlib.util.spec_from_file_location("collect_real_repo_benchmark_trend", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_handoff_module():
    root = Path(__file__).resolve().parents[4]
    module_path = root / "scripts" / "ci" / "collect_team_handoff_report.py"
    spec = importlib.util.spec_from_file_location("collect_team_handoff_report", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _pool() -> list[dict]:
    return [
        {
            "id": "browser-use",
            "repo": "browser-use/browser-use",
            "workspace_slug": "github-browser-use-browser-use",
            "release_role": "decision-rich regression repository",
            "benchmark_purpose": "Protect known imported why-search and drift examples.",
            "priority": "core",
            "operator_setup_status": "ready",
            "profile": "medium_decision_rich",
            "sparse_expectations": {
                "expects_sparse_recovery": False,
                "allow_zero_candidates": True,
                "expected_statuses": ["skipped", "attempted", "recovered", "exhausted", "not_evaluated"],
            },
        },
        {
            "id": "fastapi",
            "repo": "fastapi/fastapi",
            "workspace_slug": "github-fastapi-fastapi",
            "release_role": "large Python framework",
            "benchmark_purpose": "Track large framework extraction quality.",
            "priority": "core",
            "operator_setup_status": "operator_guided",
            "profile": "docs_heavy",
            "sparse_expectations": {
                "expects_sparse_recovery": True,
                "allow_zero_candidates": True,
                "expected_statuses": ["attempted", "recovered", "exhausted", "not_evaluated"],
            },
        },
    ]


def test_trend_pool_validation_accepts_release_fields() -> None:
    trend = _load_trend_module()

    assert trend.validate_pool(_pool()) == []


def test_trend_evidence_preserves_clean_and_missing_pool_coverage() -> None:
    trend = _load_trend_module()
    comparison = {
        "generated_at": "2026-06-09T00:00:00+00:00",
        "comparison_type": "real-repo-benchmark-regression",
        "repositories": [
            {
                "id": "browser-use",
                "repo": "browser-use/browser-use",
                "workspace_slug": "github-browser-use-browser-use",
                "movement": "unchanged",
                "baseline_value_outcome": "useful_now",
                "current_value_outcome": "useful_now",
                "baseline_bounded_outcome": "why_ready",
                "current_bounded_outcome": "why_ready",
                "reasons": ["value_outcome: useful_now -> useful_now"],
            }
        ],
    }

    report = trend.build_trend(
        pool=_pool(),
        comparison=comparison,
        generated_at="2026-06-09T01:00:00+00:00",
        label="release rehearsal",
    )
    markdown = trend.render_markdown(report)

    assert report["status"] == "warning"
    assert report["summary"]["covered_repositories"] == 1
    assert report["summary"]["missing_repositories"] == 1
    assert report["repositories"][1]["movement"] == "missing-from-pool"
    assert "Run or attach benchmark comparison rows" in markdown


def test_trend_evidence_records_missing_comparison_as_not_provided() -> None:
    trend = _load_trend_module()

    report = trend.build_trend(
        pool=_pool(),
        comparison=None,
        generated_at="2026-06-09T01:00:00+00:00",
        label="release rehearsal",
    )

    assert report["status"] == "warning"
    assert report["summary"]["not_provided_repositories"] == 2
    assert {row["movement"] for row in report["repositories"]} == {"not_provided"}
    assert report["comparison_source"]["provided"] is False


def test_trend_evidence_preserves_regression_and_operational_blocker() -> None:
    trend = _load_trend_module()
    comparison = {
        "repositories": [
            {"id": "browser-use", "repo": "browser-use/browser-use", "movement": "regressed"},
            {"id": "fastapi", "repo": "fastapi/fastapi", "movement": "operationally-blocked"},
        ]
    }

    report = trend.build_trend(
        pool=_pool(),
        comparison=comparison,
        generated_at="2026-06-09T01:00:00+00:00",
        label="release rehearsal",
    )

    assert report["status"] == "warning"
    assert report["summary"]["regressed"] == 1
    assert report["summary"]["operationally_blocked"] == 1
    assert "regressed" in report["summary"]["movements"]
    assert "operationally-blocked" in report["summary"]["movements"]


def test_team_handoff_report_summarizes_benchmark_trend(tmp_path: Path) -> None:
    handoff = _load_handoff_module()
    trend_path = tmp_path / "trend.json"
    trend_path.write_text(
        json.dumps(
            {
                "status": "warning",
                "generated_at": "2026-06-09T01:00:00+00:00",
                "label": "release rehearsal",
                "summary": {
                    "repositories": 2,
                    "covered_repositories": 1,
                    "missing_repositories": 1,
                    "not_provided_repositories": 0,
                    "operator_guided_repositories": 1,
                    "regressed": 1,
                    "improved": 0,
                    "operationally_blocked": 0,
                    "sparse_improved": 0,
                    "sparse_regressed": 1,
                    "sparse_operationally_blocked": 0,
                    "sparse_not_provided": 0,
                    "missing_from_current": 1,
                },
                "recommended_follow_up": ["Investigate regressed repositories."],
            }
        ),
        encoding="utf-8",
    )
    args = handoff.parse_args(
        [
            "--generated-at",
            "2026-06-09T01:00:00+00:00",
            "--commit",
            "abc123",
            "--benchmark-trend-json",
            str(trend_path),
        ]
    )

    report = handoff.build_report(args, tmp_path)

    assert report["overall_status"] == "warning"
    assert report["sections"]["benchmark_trend"]["status"] == "warning"
    assert report["sections"]["benchmark_trend"]["covered_repositories"] == 1
    assert report["sections"]["benchmark_trend"]["operator_guided_repositories"] == 1
    assert report["sections"]["benchmark_trend"]["sparse_regressed"] == 1
