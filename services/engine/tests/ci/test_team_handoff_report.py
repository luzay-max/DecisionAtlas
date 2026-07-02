from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_report_module():
    root = Path(__file__).resolve().parents[4]
    module_path = root / "scripts" / "ci" / "collect_team_handoff_report.py"
    spec = importlib.util.spec_from_file_location("collect_team_handoff_report", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_json(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_team_handoff_report_generates_json_and_markdown(tmp_path: Path) -> None:
    report = _load_report_module()
    release = _write_json(
        tmp_path / "release.json",
        {
            "generated_at": "2026-06-08T00:00:00+00:00",
            "overall_status": "passed",
            "required_gates": [{"id": "openspec", "label": "OpenSpec", "status": "passed"}],
            "advisory_signals": [{"id": "guardrail", "label": "Guardrail", "status": "caution"}],
            "warnings": ["guardrail caution"],
            "missing_inputs": [],
        },
    )
    hosted = _write_json(
        tmp_path / "hosted.json",
        {
            "overall_status": "operator_guided",
            "public_walkthrough_status": "operator_guided",
            "lanes": [{"id": "web", "status": "operator_guided"}],
            "blockers": [],
            "warnings": [],
        },
    )
    benchmark = _write_json(
        tmp_path / "benchmark.json",
        {
            "comparison_type": "real-repo-benchmark-regression",
            "summary": {"repositories": 1, "improved": 1, "regressed": 0, "operationally_blocked": 0},
        },
    )
    license_support = _write_json(
        tmp_path / "entitlement.json",
        {
            "schema_version": 1,
            "customer_label": "Example Customer",
            "tier": "Team Self-hosted",
            "deployment_scope": {"environment": "customer-controlled server"},
            "support": {
                "support_start": "2026-06-01",
                "support_end": "2027-06-01",
                "support_channel": "email",
            },
            "upgrade": {"upgrade_channel": "manual self-hosted package update"},
            "runtime_enforcement": {"enabled": False},
        },
    )
    audit = _write_json(
        tmp_path / "audit.json",
        {
            "events": [
                {
                    "actor_username": "local-admin",
                    "actor_role": "admin",
                    "target_type": "decision",
                    "action": "accepted",
                    "previous_state": "pending",
                    "new_state": "accepted",
                    "rationale": "Accepted for handoff.",
                    "timestamp": "2026-06-08T00:00:00+00:00",
                }
            ]
        },
    )
    clean_install = _write_json(
        tmp_path / "clean-install.json",
        {
            "status": "warning",
            "label": "clean-test",
            "package_path": ".tmp/self-hosted-package/decisionatlas-self-hosted",
            "clean_workspace_path": ".tmp/clean-self-hosted-install/clean-test",
            "source_evidence": [
                {"id": "release_evidence", "status": "pass"},
                {"id": "hosted_readiness", "status": "operator_guided"},
            ],
            "blockers": [],
            "recommended_next_actions": ["Review operator-guided lanes."],
        },
    )
    external_install = _write_json(
        tmp_path / "external-install.json",
        {
            "status": "warning",
            "label": "external-install",
            "external_host": {"host_class": "clean-vm", "is_customer_controlled": True},
            "package_identity": {"package_label": "decisionatlas-self-hosted", "version_label": "test-version"},
            "lanes": [
                {"id": "package_identity", "status": "passed"},
                {"id": "repository_import", "status": "operator_guided"},
            ],
            "redaction_findings": [],
            "recommended_next_actions": ["Disclose operator-guided import."],
        },
    )

    args = report.parse_args(
        [
            "--generated-at",
            "2026-06-08T01:00:00+00:00",
            "--commit",
            "abc123",
            "--workspace-slug",
            "demo-workspace",
            "--repository-provider",
            "github",
            "--repository-access-mode",
            "public",
            "--repository",
            "fastapi/fastapi",
            "--repository-authorization-status",
            "authorized",
            "--release-evidence-json",
            str(release),
            "--hosted-readiness-json",
            str(hosted),
            "--benchmark-comparison-json",
            str(benchmark),
            "--benchmark-trend-json",
            str(benchmark),
            "--license-support-json",
            str(license_support),
            "--clean-install-rehearsal-json",
            str(clean_install),
            "--external-install-evidence-json",
            str(external_install),
            "--audit-history-json",
            str(audit),
        ]
    )
    bundle = report.build_report(args, tmp_path)
    markdown = report.render_markdown(bundle)

    assert bundle["overall_status"] == "warning"
    assert bundle["sections"]["release_evidence"]["status"] == "pass"
    assert bundle["sections"]["hosted_readiness"]["public_walkthrough_status"] == "operator_guided"
    assert bundle["sections"]["benchmark_comparison"]["repositories"] == 1
    assert bundle["sections"]["benchmark_trend"]["repositories"] == 1
    assert bundle["sections"]["license_support"]["tier"] == "Team Self-hosted"
    assert bundle["sections"]["clean_install_rehearsal"]["status"] == "warning"
    assert bundle["sections"]["external_install_evidence"]["status"] == "warning"
    assert bundle["sections"]["external_install_evidence"]["lane_statuses"]["repository_import"] == "operator_guided"
    assert bundle["sections"]["clean_install_rehearsal"]["evidence_family_statuses"]["hosted_readiness"] == "operator_guided"
    assert bundle["sections"]["license_support"]["runtime_enforcement_enabled"] is False
    assert bundle["sections"]["review_audit"]["events"][0]["actor"] == "local-admin"
    assert "DecisionAtlas Team Handoff Report" in markdown
    assert "demo-workspace" in markdown
    assert "operator_guided" in markdown


def test_team_handoff_report_preserves_missing_evidence(tmp_path: Path) -> None:
    report = _load_report_module()
    args = report.parse_args(["--generated-at", "2026-06-08T01:00:00+00:00", "--commit", "abc123"])

    bundle = report.build_report(args, tmp_path)

    assert bundle["overall_status"] == "warning"
    assert bundle["sections"]["release_evidence"]["status"] == "not_provided"
    assert bundle["sections"]["benchmark_comparison"]["status"] == "not_provided"
    assert bundle["sections"]["benchmark_trend"]["status"] == "not_provided"
    assert bundle["sections"]["clean_install_rehearsal"]["status"] == "not_provided"
    assert bundle["sections"]["external_install_evidence"]["status"] == "not_provided"
    assert bundle["sections"]["license_support"]["status"] == "not_provided"
    assert bundle["sources"]["release_evidence"]["warnings"] == ["source_not_provided"]


def test_team_handoff_report_redacts_secret_like_material(tmp_path: Path) -> None:
    report = _load_report_module()
    audit = _write_json(
        tmp_path / "audit.json",
        {
            "events": [
                {
                    "actor_username": "reviewer",
                    "actor_role": "reviewer",
                    "target_type": "governance_rule",
                    "action": "accepted",
                    "new_state": "accepted",
                    "rationale": "Token sk-test-secret-password should never be copied.",
                    "credential_ref": "secret-ref",
                    "local_path": r"C:\Users\Max\private-repo",
                }
            ],
            "provider_token": "ghp_secret_token",
            "password": "plain-secret",
        },
    )
    license_support = _write_json(
        tmp_path / "entitlement.json",
        {
            "tier": "Team Self-hosted",
            "support": {"support_contact": "sk-test-secret-password"},
            "deployment_scope": {"local_path": r"C:\Users\Max\customer"},
        },
    )
    args = report.parse_args(
        [
            "--generated-at",
            "2026-06-08T01:00:00+00:00",
            "--commit",
            "abc123",
            "--audit-history-json",
            str(audit),
            "--license-support-json",
            str(license_support),
        ]
    )

    bundle = report.build_report(args, tmp_path)
    text = json.dumps(bundle, sort_keys=True)

    assert "ghp_secret_token" not in text
    assert "plain-secret" not in text
    assert "sk-test-secret-password" not in text
    assert r"C:\Users\Max\private-repo" not in text
    assert r"C:\Users\Max\customer" not in text
    assert "[redacted]" in text


def test_team_handoff_report_summarizes_unsafe_external_evidence_without_copying_secret(tmp_path: Path) -> None:
    report = _load_report_module()
    external_install = _write_json(
        tmp_path / "external-install.json",
        {
            "status": "blocked",
            "external_host": {"host_class": "customer-vm", "operator": "operator"},
            "package_identity": {"package_label": "decisionatlas-self-hosted"},
            "lanes": [{"id": "redaction_review", "status": "blocked", "evidence": "LLM_API_KEY=sk-test-secret-password"}],
            "redaction_findings": [{"id": "token_like_value", "status": "blocked"}],
        },
    )
    args = report.parse_args(["--external-install-evidence-json", str(external_install)])

    bundle = report.build_report(args, tmp_path)
    text = json.dumps(bundle, sort_keys=True)

    assert bundle["overall_status"] == "blocking"
    assert bundle["sections"]["external_install_evidence"]["status"] == "blocking"
    assert bundle["sections"]["external_install_evidence"]["redaction_finding_count"] == 1
    assert "sk-test-secret-password" not in text


def test_package_verifier_tracks_team_handoff_lane(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[4]
    module_path = root / "scripts" / "ci" / "verify_self_hosted_package.py"
    spec = importlib.util.spec_from_file_location("verify_self_hosted_package", module_path)
    assert spec and spec.loader
    verifier = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    lane_ids = {lane["id"] for lane in verifier.OPTIONAL_RUNTIME_LANES}

    assert "team_handoff_report" in lane_ids
    assert "clean_self_hosted_install_rehearsal" in lane_ids
    assert "license_support_boundary" in lane_ids
    assert "external_self_hosted_install_evidence" in lane_ids
