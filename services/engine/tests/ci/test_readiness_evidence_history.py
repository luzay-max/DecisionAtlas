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


def test_readiness_history_archives_full_delivery_evidence_families(tmp_path: Path) -> None:
    history = _load_history_module()
    release_path = _write_json(tmp_path / "release.json", {"overall_status": "passed", "required_gates": [], "advisory_signals": []})
    hosted_path = _write_json(tmp_path / "hosted.json", {"overall_status": "pass", "public_walkthrough_status": "pass", "lanes": []})
    benchmark_path = _write_json(tmp_path / "benchmark.json", {"summary": {"repositories": 1, "improved": 1, "regressed": 0, "operationally_blocked": 0}})
    external_path = _write_json(
        tmp_path / "external.json",
        {
            "status": "warning",
            "external_host": {"host_class": "clean-vm", "is_customer_controlled": True},
            "lanes": [{"id": "browser_smoke", "status": "operator_guided"}],
            "redaction_findings": [],
        },
    )
    continuity_path = _write_json(
        tmp_path / "continuity.json",
        {
            "status": "pass",
            "integrity": {"restore_matches_source": True, "source_record_count": 2, "restored_record_count": 2},
            "continuity_lanes": [{"id": "restore_validation", "status": "pass"}],
            "blockers": [],
            "redaction_findings": [],
        },
    )
    handoff_path = _write_json(
        tmp_path / "handoff.json",
        {"overall_status": "warning", "sections": {"external_install_evidence": {"status": "warning"}}},
    )
    audit_path = _write_json(
        tmp_path / "audit.json",
        {"overall_status": "warning", "recommended_tier": "Team Self-hosted", "sections": {"team_handoff": {"status": "warning"}}},
    )
    customer_host_path = _write_json(
        tmp_path / "customer-host.json",
        {
            "status": "warning",
            "host_proof_level": "customer_controlled_with_browser_smoke",
            "summary": {"pass": 3, "warning": 2, "blocking": 0, "operator_guided": 1, "not_provided": 1},
            "lanes": [{"id": "release_rehearsal", "status": "warning"}],
        },
    )
    full_chain_path = _write_json(
        tmp_path / "full-chain.json",
        {
            "status": "warning",
            "selected_repo_ids": ["httpx", "fastapi"],
            "summary": {"pass": 2, "warning": 3, "blocking": 0, "operator_guided": 1, "not_provided": 0},
            "lanes": [{"id": "multi_repo_diagnosis", "status": "warning"}],
        },
    )
    external_md = tmp_path / "external.md"
    external_md.write_text("# External\n", encoding="utf-8")
    continuity_md = tmp_path / "continuity.md"
    continuity_md.write_text("# Continuity\n", encoding="utf-8")

    entry = history.build_entry(
        sources=[
            history.EvidenceSource(history.FAMILY_RELEASE, release_path, None),
            history.EvidenceSource(history.FAMILY_HOSTED, hosted_path, None),
            history.EvidenceSource(history.FAMILY_BENCHMARK, benchmark_path, None),
            history.EvidenceSource(history.FAMILY_EXTERNAL_INSTALL, external_path, external_md),
            history.EvidenceSource(history.FAMILY_EXTERNAL_CUSTOMER_HOST_V2, customer_host_path, None),
            history.EvidenceSource(history.FAMILY_FULL_CHAIN_RANDOM_REPO_RELEASE, full_chain_path, None),
            history.EvidenceSource(history.FAMILY_REAL_CONTINUITY, continuity_path, continuity_md),
            history.EvidenceSource(history.FAMILY_TEAM_HANDOFF, handoff_path, None),
            history.EvidenceSource(history.FAMILY_CODE_DECISION_AUDIT, audit_path, None),
        ],
        root=tmp_path,
        history_root=tmp_path / "history",
        label="full delivery",
        created_at="2026-07-02T12:00:00+00:00",
    )
    index = history.build_index(tmp_path / "history")
    index_markdown = history.render_index_markdown(index)
    trend_markdown = history.render_trend_markdown([entry], limit=5)

    assert entry["families"]["external_install_evidence"]["status"] == "warning"
    assert entry["families"]["external_install_evidence"]["operator_guided_count"] == 1
    assert entry["families"]["external_customer_host_rehearsal_v2"]["host_proof_level"] == "customer_controlled_with_browser_smoke"
    assert entry["families"]["external_customer_host_rehearsal_v2"]["operator_guided_count"] == 1
    assert entry["families"]["full_chain_random_repo_release_rehearsal"]["selected_repo_ids"] == ["httpx", "fastapi"]
    assert entry["families"]["full_chain_random_repo_release_rehearsal"]["operator_guided_count"] == 1
    assert entry["families"]["real_continuity_rehearsal"]["restore_matches_source"] is True
    assert entry["families"]["team_handoff"]["section_statuses"]["external_install_evidence"] == "warning"
    assert entry["families"]["code_decision_audit"]["recommended_tier"] == "Team Self-hosted"
    assert (tmp_path / "history" / "2026-07-02-full-delivery" / "external_install_evidence.json").exists()
    assert (tmp_path / "history" / "2026-07-02-full-delivery" / "external_customer_host_rehearsal_v2.json").exists()
    assert (tmp_path / "history" / "2026-07-02-full-delivery" / "full_chain_random_repo_release_rehearsal.json").exists()
    assert (tmp_path / "history" / "2026-07-02-full-delivery" / "real_continuity_rehearsal.md").exists()
    assert "External install" in index_markdown
    assert "Customer host v2" in index_markdown
    assert "Full chain" in index_markdown
    assert "Real continuity" in index_markdown
    assert "Team Self-hosted" not in index_markdown
    assert "warning" in trend_markdown


def test_readiness_history_records_omitted_and_invalid_sources_without_tmp_scanning(tmp_path: Path) -> None:
    history = _load_history_module()
    entry = history.build_entry(
        sources=[
            history.EvidenceSource(history.FAMILY_RELEASE, None, None),
            history.EvidenceSource(history.FAMILY_HOSTED, Path(".tmp/does-not-exist.json"), None),
            history.EvidenceSource(history.FAMILY_BENCHMARK, None, None),
            history.EvidenceSource(history.FAMILY_EXTERNAL_INSTALL, None, None),
            history.EvidenceSource(history.FAMILY_EXTERNAL_CUSTOMER_HOST_V2, None, None),
            history.EvidenceSource(history.FAMILY_FULL_CHAIN_RANDOM_REPO_RELEASE, None, None),
            history.EvidenceSource(history.FAMILY_REAL_CONTINUITY, None, None),
            history.EvidenceSource(history.FAMILY_TEAM_HANDOFF, None, None),
            history.EvidenceSource(history.FAMILY_CODE_DECISION_AUDIT, None, None),
        ],
        root=tmp_path,
        history_root=tmp_path / "history",
        label="missing inputs",
        created_at="2026-05-09T12:00:00+00:00",
    )

    assert entry["families"]["release_evidence"]["status"] == "not_provided"
    assert entry["families"]["benchmark_comparison"]["status"] == "not_provided"
    assert entry["families"]["external_install_evidence"]["status"] == "not_provided"
    assert entry["families"]["external_customer_host_rehearsal_v2"]["status"] == "not_provided"
    assert entry["families"]["full_chain_random_repo_release_rehearsal"]["status"] == "not_provided"
    assert entry["families"]["real_continuity_rehearsal"]["status"] == "not_provided"
    assert entry["families"]["team_handoff"]["status"] == "not_provided"
    assert entry["families"]["code_decision_audit"]["status"] == "not_provided"
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
            "external_install_evidence": {"status": "pass"},
            "external_customer_host_rehearsal_v2": {"status": "pass"},
            "full_chain_random_repo_release_rehearsal": {"status": "pass"},
            "real_continuity_rehearsal": {"status": "pass"},
            "team_handoff": {"status": "pass"},
            "code_decision_audit": {"status": "pass"},
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
            "external_install_evidence": {"status": "warning"},
            "external_customer_host_rehearsal_v2": {"status": "blocking"},
            "full_chain_random_repo_release_rehearsal": {"status": "blocking"},
            "real_continuity_rehearsal": {"status": "blocking"},
            "team_handoff": {"status": "warning"},
            "code_decision_audit": {"status": "warning"},
        },
        "counts": {
            "benchmark_regressions": 1,
            "benchmark_operational_blockers": 1,
            "external_customer_host_v2_blockers": 1,
            "full_chain_random_repo_release_blockers": 1,
            "real_continuity_blockers": 1,
            "warnings": 2,
            "operator_guided": 1,
            "not_provided": 1,
        },
    }

    markdown = history.render_trend_markdown([clean_entry, warning_entry], limit=5)

    assert "operator_guided" in markdown
    assert "benchmark regressions" in markdown.lower()
    assert "Real continuity" in markdown
    assert "Customer host v2" in markdown
    assert "Resolve customer-host v2 blockers" in markdown
    assert "Full chain" in markdown
    assert "Resolve full-chain random repo release rehearsal blockers" in markdown
    assert "Resolve real continuity rehearsal blockers" in markdown
    assert "Attach missing optional evidence" in markdown
