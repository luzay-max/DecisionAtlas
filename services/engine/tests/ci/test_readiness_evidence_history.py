from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_history_module():
    root = Path(__file__).resolve().parents[4]
    module_path = root / "scripts" / "ci" / "collect_readiness_evidence_history.py"
    spec = importlib.util.spec_from_file_location("collect_readiness_evidence_history", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_json(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_readiness_history_extracts_release_hosted_and_benchmark_summaries(tmp_path: Path) -> None:
    history = _load_history_module()
    release_path = _write_json(
        tmp_path / "release.json",
        {
            "generated_at": "2026-05-09T00:00:00+00:00",
            "overall_status": "warning",
            "required_gates": [{"id": "pre_release", "status": "passed"}],
            "advisory_signals": [{"id": "guardrail", "status": "caution"}],
            "warnings": ["guardrail caution"],
            "missing_inputs": [{"id": "targeted_tests", "status": "not_provided"}],
        },
    )
    hosted_path = _write_json(
        tmp_path / "hosted.json",
        {
            "generated_at": "2026-05-09T00:00:00+00:00",
            "overall_status": "operator_guided",
            "public_walkthrough_status": "operator_guided",
            "public_walkthrough_decision": "operator_review_required",
            "lanes": [
                {"id": "web", "status": "operator_guided"},
                {"id": "release_evidence", "status": "not_provided"},
            ],
            "blockers": [],
            "warnings": [],
        },
    )
    benchmark_path = _write_json(
        tmp_path / "benchmark.json",
        {
            "generated_at": "2026-05-09T00:00:00+00:00",
            "comparison_type": "real-repo-benchmark-regression",
            "summary": {
                "repositories": 3,
                "improved": 1,
                "regressed": 1,
                "operationally_blocked": 1,
                "movements": {"improved": 1, "regressed": 1, "operationally-blocked": 1},
            },
        },
    )

    entry = history.build_entry(
        sources=[
            history.EvidenceSource(history.FAMILY_RELEASE, release_path, None),
            history.EvidenceSource(history.FAMILY_HOSTED, hosted_path, None),
            history.EvidenceSource(history.FAMILY_BENCHMARK, benchmark_path, None),
        ],
        root=tmp_path,
        history_root=tmp_path / "history",
        label="Release RC 1",
        created_at="2026-05-09T12:00:00+00:00",
        commit="abc123",
        version_label="v0.3.0-rc.1",
    )

    assert entry["entry_id"] == "2026-05-09-release-rc-1"
    assert entry["status"] == "warning"
    assert entry["families"]["release_evidence"]["status"] == "warning"
    assert entry["families"]["hosted_readiness"]["public_walkthrough_status"] == "operator_guided"
    assert entry["families"]["benchmark_comparison"]["regressed"] == 1
    assert entry["families"]["release_evidence"]["source_path"] == "release.json"
    assert entry["artifacts"]["release_evidence"]["source_json_path"] == "release.json"
    assert entry["counts"]["benchmark_operational_blockers"] == 1
    assert (tmp_path / "history" / "2026-05-09-release-rc-1" / "entry.json").exists()


def test_readiness_history_records_omitted_and_invalid_sources_without_tmp_scanning(tmp_path: Path) -> None:
    history = _load_history_module()
    entry = history.build_entry(
        sources=[
            history.EvidenceSource(history.FAMILY_RELEASE, None, None),
            history.EvidenceSource(history.FAMILY_HOSTED, Path(".tmp/does-not-exist.json"), None),
            history.EvidenceSource(history.FAMILY_BENCHMARK, None, None),
        ],
        root=tmp_path,
        history_root=tmp_path / "history",
        label="missing inputs",
        created_at="2026-05-09T12:00:00+00:00",
    )

    assert entry["families"]["release_evidence"]["status"] == "not_provided"
    assert entry["families"]["benchmark_comparison"]["status"] == "not_provided"
    assert entry["families"]["hosted_readiness"]["status"] == "not_provided"
    assert "does not exist" in entry["warnings"][0]
    assert entry["counts"]["not_provided"] >= 3


def test_readiness_history_copies_explicit_artifacts_and_generates_index_markdown(tmp_path: Path) -> None:
    history = _load_history_module()
    release_path = _write_json(
        tmp_path / "release.json",
        {
            "overall_status": "passed",
            "required_gates": [{"id": "pre_release", "status": "passed"}],
            "advisory_signals": [],
            "warnings": [],
            "missing_inputs": [],
        },
    )
    release_md = tmp_path / "release.md"
    release_md.write_text("# Release Evidence\n", encoding="utf-8")
    history_root = tmp_path / "history"

    history.build_entry(
        sources=[
            history.EvidenceSource(history.FAMILY_RELEASE, release_path, release_md),
            history.EvidenceSource(history.FAMILY_HOSTED, None, None),
            history.EvidenceSource(history.FAMILY_BENCHMARK, None, None),
        ],
        root=tmp_path,
        history_root=history_root,
        label="first",
        created_at="2026-05-09T10:00:00+00:00",
    )
    history.build_entry(
        sources=[
            history.EvidenceSource(history.FAMILY_RELEASE, release_path, release_md),
            history.EvidenceSource(history.FAMILY_HOSTED, None, None),
            history.EvidenceSource(history.FAMILY_BENCHMARK, None, None),
        ],
        root=tmp_path,
        history_root=history_root,
        label="second",
        created_at="2026-05-10T10:00:00+00:00",
    )
    index = history.build_index(history_root)
    markdown = history.render_index_markdown(index)

    assert [entry["entry_id"] for entry in index["entries"]] == ["2026-05-09-first", "2026-05-10-second"]
    assert (history_root / "2026-05-09-first" / "release_evidence.json").exists()
    assert (history_root / "2026-05-09-first" / "release_evidence.md").exists()
    assert "Readiness Evidence History" in markdown
    assert "not_provided" in markdown


def test_readiness_history_trend_preserves_non_clean_states(tmp_path: Path) -> None:
    history = _load_history_module()
    clean_entry = {
        "entry_id": "2026-05-08-clean",
        "status": "passed",
        "families": {
            "release_evidence": {"status": "passed"},
            "hosted_readiness": {"status": "pass", "public_walkthrough_status": "pass"},
            "benchmark_comparison": {"status": "passed"},
        },
        "counts": {},
    }
    warning_entry = {
        "entry_id": "2026-05-09-warning",
        "status": "warning",
        "families": {
            "release_evidence": {"status": "warning"},
            "hosted_readiness": {"status": "operator_guided", "public_walkthrough_status": "operator_guided"},
            "benchmark_comparison": {"status": "warning"},
        },
        "counts": {
            "benchmark_regressions": 1,
            "benchmark_operational_blockers": 1,
            "warnings": 2,
            "operator_guided": 1,
            "not_provided": 1,
        },
    }

    markdown = history.render_trend_markdown([clean_entry, warning_entry], limit=5)

    assert "operator_guided" in markdown
    assert "benchmark regressions" in markdown.lower()
    assert "Attach missing optional evidence" in markdown
