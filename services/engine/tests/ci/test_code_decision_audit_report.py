from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[4]
    module_path = root / "scripts" / "ci" / "collect_code_decision_audit_report.py"
    spec = importlib.util.spec_from_file_location("collect_code_decision_audit_report", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_json(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_audit_report_summarizes_supplied_evidence_and_preserves_warning(tmp_path: Path) -> None:
    audit = _load_module()
    release = _write_json(
        tmp_path / "release.json",
        {"overall_status": "warning", "required_gates": [{"id": "pre_release", "status": "passed"}], "missing_inputs": []},
    )
    trend = _write_json(
        tmp_path / "trend.json",
        {
            "status": "warning",
            "summary": {"repositories": 5, "covered_repositories": 1, "missing_repositories": 4, "regressed": 0, "operationally_blocked": 0},
            "recommended_follow_up": ["Run or attach benchmark comparison rows."],
        },
    )
    handoff = _write_json(
        tmp_path / "handoff.json",
        {
            "overall_status": "warning",
            "workspace": {"slug": "demo-workspace"},
            "repository_scope": {"repository": "browser-use/browser-use"},
            "sections": {"benchmark_trend": {"status": "warning"}},
        },
    )
    external_install = _write_json(
        tmp_path / "external-install.json",
        {
            "status": "warning",
            "external_host": {"host_class": "clean-vm", "is_customer_controlled": True},
            "package_identity": {"package_label": "decisionatlas-self-hosted", "version_label": "test-version"},
            "lanes": [{"id": "browser_smoke", "status": "operator_guided"}],
        },
    )
    real_continuity = _write_json(
        tmp_path / "real-continuity.json",
        {
            "status": "warning",
            "scratch_scope": {"scratch_only": True},
            "integrity": {"restore_matches_source": True, "source_record_count": 2, "restored_record_count": 2},
            "continuity_lanes": [{"id": "post_upgrade_validation", "status": "operator_guided"}],
        },
    )

    args = audit.parse_args(
        [
            "--generated-at",
            "2026-06-09T00:00:00+00:00",
            "--customer",
            "Sample Team",
            "--repository",
            "browser-use/browser-use",
            "--workspace",
            "demo-workspace",
            "--release-evidence-json",
            str(release),
            "--benchmark-trend-json",
            str(trend),
            "--team-handoff-json",
            str(handoff),
            "--external-install-evidence-json",
            str(external_install),
            "--real-continuity-rehearsal-json",
            str(real_continuity),
        ]
    )
    report = audit.build_report(args, tmp_path)
    markdown = audit.render_markdown(report)

    assert report["overall_status"] == "warning"
    assert report["sections"]["benchmark_trend"]["covered_repositories"] == 1
    assert report["sections"]["team_handoff"]["repository_scope"]["repository"] == "browser-use/browser-use"
    assert report["sections"]["external_install_evidence"]["lane_statuses"]["browser_smoke"] == "operator_guided"
    assert report["sections"]["real_continuity_rehearsal"]["restore_matches_source"] is True
    assert "External install evidence" in markdown
    assert "Real continuity evidence" in markdown
    assert "Run or attach benchmark comparison rows." in markdown
    assert "Code Decision Audit Report" in markdown


def test_audit_report_records_omitted_evidence_as_not_provided(tmp_path: Path) -> None:
    audit = _load_module()
    args = audit.parse_args(["--generated-at", "2026-06-09T00:00:00+00:00"])

    report = audit.build_report(args, tmp_path)

    assert report["overall_status"] == "warning"
    assert report["sections"]["release_evidence"]["status"] == "not_provided"
    assert report["sources"]["release_evidence"]["warnings"] == ["source_not_provided"]
    assert report["sections"]["team_handoff"]["status"] == "not_provided"
    assert report["sections"]["external_install_evidence"]["status"] == "not_provided"
    assert report["sections"]["real_continuity_rehearsal"]["status"] == "not_provided"


def test_audit_report_redacts_secret_like_and_local_path_material(tmp_path: Path) -> None:
    audit = _load_module()
    license_support = _write_json(
        tmp_path / "license.json",
        {
            "tier": "Team Self-hosted",
            "customer_label": "Secret Customer",
            "support": {"support_contact": "sk-test-secret-password"},
            "deployment_scope": {"local_path": r"C:\Users\Max\private"},
            "runtime_enforcement": {"enabled": False, "api_key": "ghp_secret_token"},
        },
    )
    args = audit.parse_args(
        [
            "--generated-at",
            "2026-06-09T00:00:00+00:00",
            "--license-support-json",
            str(license_support),
            "--open-commercial-question",
            "Who owns upgrade windows?",
        ]
    )

    report = audit.build_report(args, tmp_path)
    text = json.dumps(report, sort_keys=True)

    assert "sk-test-secret-password" not in text
    assert "ghp_secret_token" not in text
    assert r"C:\Users\Max\private" not in text
    assert "[redacted]" in text
    assert "[local_path_redacted]" in text
    assert report["open_commercial_questions"] == ["Who owns upgrade windows?"]


def test_audit_report_summarizes_blocked_external_evidence_without_secret_copy(tmp_path: Path) -> None:
    audit = _load_module()
    external_install = _write_json(
        tmp_path / "external-install.json",
        {
            "status": "blocked",
            "external_host": {"host_class": "customer-vm"},
            "package_identity": {"package_label": "decisionatlas-self-hosted"},
            "lanes": [{"id": "redaction_review", "status": "blocked", "evidence": "GITHUB_TOKEN=ghp_secret_token"}],
            "redaction_findings": [{"id": "token_like_value", "status": "blocked"}],
        },
    )
    args = audit.parse_args(["--external-install-evidence-json", str(external_install)])

    report = audit.build_report(args, tmp_path)
    text = json.dumps(report, sort_keys=True)

    assert report["overall_status"] == "blocking"
    assert report["sections"]["external_install_evidence"]["status"] == "blocking"
    assert report["sections"]["external_install_evidence"]["redaction_finding_count"] == 1
    assert "ghp_secret_token" not in text


def test_audit_report_summarizes_blocked_real_continuity_without_secret_copy(tmp_path: Path) -> None:
    audit = _load_module()
    real_continuity = _write_json(
        tmp_path / "real-continuity.json",
        {
            "status": "blocking",
            "scratch_scope": {"scratch_only": True},
            "integrity": {"restore_matches_source": False},
            "continuity_lanes": [{"id": "redaction", "status": "blocking", "details": {"secret": "GITHUB_TOKEN=ghp_secret_token"}}],
            "redaction_findings": [{"id": "token_like_value", "status": "blocking"}],
        },
    )
    args = audit.parse_args(["--real-continuity-rehearsal-json", str(real_continuity)])

    report = audit.build_report(args, tmp_path)
    text = json.dumps(report, sort_keys=True)

    assert report["overall_status"] == "blocking"
    assert report["sections"]["real_continuity_rehearsal"]["status"] == "blocking"
    assert report["sections"]["real_continuity_rehearsal"]["redaction_finding_count"] == 1
    assert "ghp_secret_token" not in text
