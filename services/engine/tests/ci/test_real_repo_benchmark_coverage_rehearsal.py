from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[4]
    module_path = root / "scripts" / "ci" / "rehearse_real_repo_benchmark_coverage.py"
    spec = importlib.util.spec_from_file_location("rehearse_real_repo_benchmark_coverage", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_json(path: Path, payload: dict | list) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _pool(rows: list[str]) -> list[dict]:
    return [
        {
            "id": repo_id,
            "repo": f"example/{repo_id}",
            "workspace_slug": f"github-example-{repo_id}",
            "release_role": "real repo coverage fixture",
            "benchmark_purpose": "Exercise benchmark coverage rehearsal.",
            "priority": "core",
            "operator_setup_status": "ready",
            "profile": "medium_decision_rich",
            "sparse_expectations": {
                "expects_sparse_recovery": False,
                "allow_zero_candidates": True,
                "expected_statuses": ["skipped", "attempted", "recovered", "exhausted", "not_evaluated"],
            },
        }
        for repo_id in rows
    ]


def _snapshot(repo_ids: list[str], *, generated_at: str = "2026-06-09T00:00:00+00:00") -> dict:
    return {
        "schema_version": 1,
        "generated_at": generated_at,
        "source": "test",
        "summary": {"repositories": len(repo_ids), "passed": len(repo_ids), "failed": 0},
        "repositories": [
            {
                "id": repo_id,
                "repo": f"example/{repo_id}",
                "workspace_slug": f"github-example-{repo_id}",
                "role": "fixture",
                "benchmark_purpose": "Fixture row.",
                "passed": True,
                "value_outcome": "useful_now",
                "bounded_outcome": "why_ready",
                "value_outcome_allowed": True,
                "key_metrics": {
                    "candidate_decision_count": 2,
                    "accepted_decision_count": 1,
                    "strong_candidate_count": 1,
                    "thin_candidate_ratio": 0,
                    "why_case_passed_count": 1,
                    "drift_case_passed_count": 1,
                },
                "limitation_categories": [],
                "follow_up_categories": [],
                "why_summary": {"case_count": 1, "passed_count": 1},
                "drift_summary": {"case_count": 1, "passed_count": 1, "state": "clean"},
                "operational_error_type": None,
            }
            for repo_id in repo_ids
        ],
    }


def test_coverage_rehearsal_generates_full_offline_artifact_chain(tmp_path: Path) -> None:
    rehearsal = _load_module()
    pool_path = _write_json(tmp_path / "pool.json", _pool(["browser-use"]))
    current = _write_json(tmp_path / "current.json", _snapshot(["browser-use"]))
    baseline = _write_json(tmp_path / "baseline.json", _snapshot(["browser-use"]))

    report = rehearsal.build_rehearsal(
        root=tmp_path,
        label="offline rehearsal",
        generated_at="2026-06-09T01:00:00+00:00",
        pool_path=pool_path,
        baseline_snapshot_path=baseline,
        current_report_path=current,
        output_dir=tmp_path / "out",
        output_json=tmp_path / "out" / "rehearsal.json",
        output_markdown=tmp_path / "out" / "rehearsal.md",
    )

    assert report["status"] == "pass"
    assert report["mode"] == "offline"
    assert report["summary"]["covered_repositories"] == 1
    assert report["summary"]["sparse_not_provided"] == 1
    assert (tmp_path / "out" / "rehearsal-current-snapshot.json").exists()
    assert (tmp_path / "out" / "rehearsal-comparison.json").exists()
    assert (tmp_path / "out" / "rehearsal-trend.json").exists()
    assert "rehearsal-current-snapshot" in (tmp_path / "out" / "rehearsal.md").read_text(encoding="utf-8")


def test_coverage_rehearsal_preserves_missing_pool_warning(tmp_path: Path) -> None:
    rehearsal = _load_module()
    pool_path = _write_json(tmp_path / "pool.json", _pool(["browser-use", "fastapi"]))
    current = _write_json(tmp_path / "current.json", _snapshot(["browser-use"]))
    baseline = _write_json(tmp_path / "baseline.json", _snapshot(["browser-use"]))

    report = rehearsal.build_rehearsal(
        root=tmp_path,
        label="missing coverage",
        generated_at="2026-06-09T01:00:00+00:00",
        pool_path=pool_path,
        baseline_snapshot_path=baseline,
        current_report_path=current,
        output_dir=tmp_path / "out",
        output_json=tmp_path / "out" / "rehearsal.json",
        output_markdown=tmp_path / "out" / "rehearsal.md",
    )

    assert report["status"] == "warning"
    assert report["summary"]["missing_repositories"] == 1
    assert "Run or attach benchmark comparison rows" in report["recommended_follow_up"][0]


def test_coverage_rehearsal_random_selection_is_deterministic() -> None:
    rehearsal = _load_module()

    selected_once = rehearsal.select_repo_ids(
        _pool(["httpx", "fastapi", "rich", "n8n", "browser-use"]),
        repo_ids=[],
        random_count=2,
        random_seed=42,
    )
    selected_twice = rehearsal.select_repo_ids(
        _pool(["httpx", "fastapi", "rich", "n8n", "browser-use"]),
        repo_ids=[],
        random_count=2,
        random_seed=42,
    )

    assert selected_once == selected_twice
    assert len(selected_once) == 2


def test_live_coverage_rehearsal_preserves_explicit_selection_and_redacts_paths(
    tmp_path: Path,
    monkeypatch,
) -> None:
    rehearsal = _load_module()
    pool_path = _write_json(tmp_path / "pool.json", _pool(["browser-use", "fastapi"]))
    baseline = _write_json(tmp_path / "baseline.json", _snapshot(["browser-use"]))

    def fake_live_current_report(*, repo_ids: list[str], report_path: Path, **_kwargs):
        assert repo_ids == ["browser-use"]
        _write_json(report_path, _snapshot(repo_ids, generated_at="2026-06-09T00:30:00+00:00"))
        return "pass", []

    monkeypatch.setattr(rehearsal, "_run_live_current_report", fake_live_current_report)
    report = rehearsal.build_rehearsal(
        root=tmp_path,
        label="live rehearsal",
        generated_at="2026-06-09T01:00:00+00:00",
        pool_path=pool_path,
        baseline_snapshot_path=baseline,
        output_dir=tmp_path / "out",
        output_json=tmp_path / "out" / "rehearsal.json",
        output_markdown=tmp_path / "out" / "rehearsal.md",
        live=True,
        base_url="https://operator:secret@example.test:9443/api?token=hidden",
        repo_ids=["browser-use"],
        random_seed=17,
    )

    serialized = (tmp_path / "out" / "rehearsal.json").read_text(encoding="utf-8")
    assert report["selected_repo_ids"] == ["browser-use"]
    assert report["base_url"] == "https://example.test:9443/api"
    assert "operator:secret" not in serialized
    assert "token=hidden" not in serialized
    assert str(tmp_path) not in serialized


def test_coverage_rehearsal_requires_current_report_without_live(tmp_path: Path) -> None:
    rehearsal = _load_module()
    pool_path = _write_json(tmp_path / "pool.json", _pool(["browser-use"]))
    baseline = _write_json(tmp_path / "baseline.json", _snapshot(["browser-use"]))

    try:
        rehearsal.build_rehearsal(
            root=tmp_path,
            label="missing input",
            generated_at="2026-06-09T01:00:00+00:00",
            pool_path=pool_path,
            baseline_snapshot_path=baseline,
            output_dir=tmp_path / "out",
            output_json=tmp_path / "out" / "rehearsal.json",
            output_markdown=tmp_path / "out" / "rehearsal.md",
        )
    except ValueError as exc:
        assert "--current-report-json is required" in str(exc)
    else:
        raise AssertionError("Expected missing current report to raise ValueError")
