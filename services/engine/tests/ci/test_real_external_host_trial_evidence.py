from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[4]
    module_path = root / "scripts" / "ci" / "collect_real_external_host_trial_evidence.py"
    spec = importlib.util.spec_from_file_location("collect_real_external_host_trial_evidence", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_json(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _real_host_payload() -> dict:
    return {
        "host_profile": {
            "host_class": "customer-vm",
            "os_family": "Ubuntu Server",
            "os_version": "24.04",
            "deployment_mode": "docker-compose",
            "is_customer_controlled": True,
            "operator": "pilot-admin",
        },
        "package_identity": {
            "package_label": "decisionatlas-self-hosted",
            "version_label": "v0.4.0-pilot.1",
            "commit": "abc123def456",
            "package_manifest_sha256": "7c4f0f46fbb3",
        },
        "trial_lanes": {
            lane_id: {
                "status": "passed",
                "summary": f"{lane_id} completed on the customer-controlled host.",
            }
            for lane_id in (
                "startup",
                "health",
                "admin_login",
                "team_workspace",
                "repository_import",
                "review",
                "why",
                "drift",
                "continuity",
                "browser_smoke",
            )
        },
        "browser_smoke": {
            "status": "passed",
            "operator": "pilot-admin",
            "summary": "Opened home, team, review, evidence, and workspace pages.",
            "pages": ["/", "/team", "/review?workspace=pilot-workspace", "/evidence"],
        },
        "redaction_acknowledgement": {
            "acknowledged": True,
            "reviewer": "pilot-admin",
        },
        "limitations": ["private repository import was validated through redacted status only"],
    }


def test_real_external_host_trial_passes_with_clean_sources(tmp_path: Path) -> None:
    collector = _load_module()
    host_input = _write_json(tmp_path / "host.json", _real_host_payload())
    customer_host = _write_json(
        tmp_path / "customer-host.json",
        {
            "status": "pass",
            "host_proof_level": "customer_controlled_with_browser_smoke",
            "summary": {"pass": 6, "warning": 0, "blocking": 0, "operator_guided": 0, "not_provided": 0},
            "lanes": [],
            "blockers": [],
            "limitations": [],
        },
    )
    full_chain = _write_json(
        tmp_path / "full-chain.json",
        {
            "status": "pass",
            "selected_repo_ids": ["pallets/flask", "Textualize/rich"],
            "summary": {"pass": 5, "warning": 0, "blocking": 0, "operator_guided": 0, "not_provided": 0},
            "lanes": [],
            "blockers": [],
            "limitations": [],
        },
    )
    args = collector.parse_args(
        [
            "--host-input-json",
            str(host_input),
            "--customer-host-v2-json",
            str(customer_host),
            "--full-chain-json",
            str(full_chain),
            "--generated-at",
            "2026-07-03T00:00:00+00:00",
        ]
    )

    report = collector.build_report(args, tmp_path)
    markdown = collector.render_markdown(report)

    assert report["status"] == "pass"
    assert report["host_proof_level"] == "real_external_customer_controlled"
    assert report["selected_repo_ids"] == ["pallets/flask", "Textualize/rich"]
    assert report["summary"]["placeholder_findings"] == 0
    assert "Real External Host Trial Evidence" in markdown


def test_real_external_host_trial_marks_example_template_non_clean(tmp_path: Path) -> None:
    collector = _load_module()
    root = Path(__file__).resolve().parents[4]
    template = root / "templates" / "external-customer-host-rehearsal-v2.example.json"
    args = collector.parse_args(
        [
            "--host-input-json",
            str(template),
            "--generated-at",
            "2026-07-03T00:00:00+00:00",
        ]
    )

    report = collector.build_report(args, root)

    assert report["status"] == "warning"
    assert report["host_proof_level"] == "template_or_placeholder"
    assert report["summary"]["placeholder_findings"] >= 1
    assert "Replace example/template placeholder values" in report["recommended_next_actions"][0]


def test_real_external_host_trial_missing_input_is_operator_guided(tmp_path: Path) -> None:
    collector = _load_module()
    args = collector.parse_args(["--generated-at", "2026-07-03T00:00:00+00:00"])

    report = collector.build_report(args, tmp_path)

    assert report["status"] == "warning"
    assert report["host_proof_level"] == "operator_guided"
    assert {lane["id"]: lane["status"] for lane in report["lanes"]}["host_input"] == "operator_guided"


def test_real_external_host_trial_blocks_secret_like_material(tmp_path: Path) -> None:
    collector = _load_module()
    payload = _real_host_payload()
    payload["commands_run"] = [{"command": "set GITHUB_TOKEN=ghp_secretvalue123"}]
    host_input = _write_json(tmp_path / "host.json", payload)
    args = collector.parse_args(["--host-input-json", str(host_input)])

    report = collector.build_report(args, tmp_path)
    markdown = collector.render_markdown(report)

    assert report["status"] == "blocking"
    assert any(finding["id"] == "token_like_value" for finding in report["redaction_findings"])
    assert "ghp_secretvalue123" not in markdown


def test_real_external_host_trial_archives_to_readiness_history(tmp_path: Path) -> None:
    collector = _load_module()
    host_input = _write_json(tmp_path / "host.json", _real_host_payload())
    args = collector.parse_args(
        [
            "--host-input-json",
            str(host_input),
            "--generated-at",
            "2026-07-03T00:00:00+00:00",
            "--output-json",
            str(tmp_path / "trial.json"),
            "--output-markdown",
            str(tmp_path / "trial.md"),
            "--archive-history",
            "--history-root",
            str(tmp_path / "history"),
        ]
    )
    report = collector.build_report(args, tmp_path)
    json_path, markdown_path = collector.write_report(tmp_path, report, args.output_json, args.output_markdown)

    archive = collector.archive_report(tmp_path, report, json_path, markdown_path, args)

    assert archive["entry_id"] == "2026-07-03-real-external-host-trial-evidence"
    assert (
        tmp_path
        / "history"
        / "2026-07-03-real-external-host-trial-evidence"
        / "real_external_host_trial_evidence.json"
    ).exists()
    assert (tmp_path / "history" / "index.json").exists()
    assert (tmp_path / "history" / "trend.md").exists()


def test_real_external_host_trial_accepts_legacy_lanes_but_keeps_missing_core_work_visible(tmp_path: Path) -> None:
    collector = _load_module()
    payload = _real_host_payload()
    payload.pop("trial_lanes")
    payload["commands_run"] = [{"id": "start_stack", "status": "passed", "summary": "Started."}]
    payload["health_checks"] = [{"id": "api_health", "status": "passed", "summary": "OK."}]
    host_input = _write_json(tmp_path / "legacy.json", payload)
    args = collector.parse_args(["--host-input-json", str(host_input)])

    report = collector.build_report(args, tmp_path)
    lanes = {lane["id"]: lane for lane in report["lanes"]}

    assert report["status"] == "warning"
    assert lanes["startup"]["status"] == "pass"
    assert lanes["health"]["status"] == "pass"
    assert lanes["admin_login"]["status"] == "not_provided"
    assert "admin_login_lane_missing" in {finding["id"] for finding in report["required_host_findings"]}


def test_real_external_host_trial_redacts_external_paths_and_source_secrets(tmp_path: Path) -> None:
    collector = _load_module()
    payload = _real_host_payload()
    payload["trial_lanes"]["health"]["summary"] = r"Validated at C:\customer\decisionatlas\health.log"
    host_input = _write_json(tmp_path / "host.json", payload)
    outside_source = Path("C:/customer/private-release.json")
    args = collector.parse_args(["--host-input-json", str(host_input), "--customer-host-v2-json", str(outside_source)])

    report = collector.build_report(args, tmp_path)
    markdown = collector.render_markdown(report)

    assert "C:\\customer" not in markdown
    assert "<external-path>" in json.dumps(report)
