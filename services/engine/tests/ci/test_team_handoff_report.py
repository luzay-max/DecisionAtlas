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
    args = report.parse_args(
        [
            "--generated-at",
            "2026-06-08T01:00:00+00:00",
            "--commit",
            "abc123",
            "--audit-history-json",
            str(audit),
        ]
    )

    bundle = report.build_report(args, tmp_path)
    text = json.dumps(bundle, sort_keys=True)

    assert "ghp_secret_token" not in text
    assert "plain-secret" not in text
    assert "sk-test-secret-password" not in text
    assert r"C:\Users\Max\private-repo" not in text
    assert "[redacted]" in text


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
