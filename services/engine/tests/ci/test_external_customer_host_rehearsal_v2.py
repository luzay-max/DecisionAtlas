from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[4]
    module_path = root / "scripts" / "ci" / "collect_external_customer_host_rehearsal_v2.py"
    spec = importlib.util.spec_from_file_location("collect_external_customer_host_rehearsal_v2", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_json(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _host_payload() -> dict:
    return {
        "host_profile": {
            "host_class": "customer-vm",
            "os_family": "Windows Server",
            "deployment_mode": "docker-compose",
            "is_customer_controlled": True,
            "operator": "customer-operator",
        },
        "package_identity": {
            "package_label": "decisionatlas-self-hosted",
            "version_label": "v0.customer-test",
            "commit": "abc123",
        },
        "browser_smoke": {
            "status": "passed",
            "summary": "operator opened dashboard, review, evidence",
            "pages": ["/", "/team", "/review?workspace=demo-workspace", "/evidence"],
        },
        "redaction_acknowledgement": {
            "acknowledged": True,
            "reviewer": "customer-operator",
        },
        "limitations": ["public GitHub import rerun separately"],
    }


def test_customer_host_v2_generates_warning_with_non_pass_source_lanes(tmp_path: Path) -> None:
    collector = _load_module()
    host_input = _write_json(tmp_path / "host.json", _host_payload())
    package_json = _write_json(tmp_path / "package.json", {"status": "pass", "package_label": "decisionatlas"})
    release_json = _write_json(
        tmp_path / "release.json",
        {"status": "warning", "summary": {"pass": 2, "warning": 1, "blocking": 0}},
    )
    args = collector.parse_args(
        [
            "--host-input-json",
            str(host_input),
            "--package-verification-json",
            str(package_json),
            "--release-rehearsal-json",
            str(release_json),
            "--generated-at",
            "2026-07-03T00:00:00+00:00",
        ]
    )

    report = collector.build_report(args, tmp_path)
    markdown = collector.render_markdown(report)

    assert report["status"] == "warning"
    assert report["host_proof_level"] == "customer_controlled_with_browser_smoke"
    assert {lane["id"]: lane["status"] for lane in report["lanes"]}["customer_host_template"] == "pass"
    assert {lane["id"]: lane["status"] for lane in report["lanes"]}["browser_smoke"] == "pass"
    assert {lane["id"]: lane["status"] for lane in report["lanes"]}["release_rehearsal"] == "warning"
    assert "External Customer Host Rehearsal v2" in markdown
    assert "customer_controlled_with_browser_smoke" in markdown


def test_customer_host_v2_missing_template_is_operator_guided(tmp_path: Path) -> None:
    collector = _load_module()
    args = collector.parse_args(["--generated-at", "2026-07-03T00:00:00+00:00"])

    report = collector.build_report(args, tmp_path)

    assert report["status"] == "warning"
    assert report["host_proof_level"] == "operator_guided"
    assert {lane["id"]: lane["status"] for lane in report["lanes"]}["customer_host_template"] == "operator_guided"
    assert "Fill the sanitized customer-host v2 template" in report["recommended_next_actions"][0]


def test_customer_host_v2_blocks_secret_like_material(tmp_path: Path) -> None:
    collector = _load_module()
    payload = _host_payload()
    payload["commands_run"] = [{"command": "set LLM_API_KEY=sk-test-secret-password"}]
    host_input = _write_json(tmp_path / "host.json", payload)
    args = collector.parse_args(["--host-input-json", str(host_input)])

    report = collector.build_report(args, tmp_path)
    markdown = collector.render_markdown(report)

    assert report["status"] == "blocking"
    assert any(finding["id"] == "token_like_value" for finding in report["redaction_findings"])
    assert {lane["id"]: lane["status"] for lane in report["lanes"]}["redaction_review"] == "blocking"
    assert "sk-test-secret-password" not in markdown


def test_customer_host_v2_archives_to_readiness_history(tmp_path: Path) -> None:
    collector = _load_module()
    host_input = _write_json(tmp_path / "host.json", _host_payload())
    args = collector.parse_args(
        [
            "--host-input-json",
            str(host_input),
            "--generated-at",
            "2026-07-03T00:00:00+00:00",
            "--output-json",
            str(tmp_path / "customer-host.json"),
            "--output-markdown",
            str(tmp_path / "customer-host.md"),
            "--archive-history",
            "--history-root",
            str(tmp_path / "history"),
        ]
    )
    report = collector.build_report(args, tmp_path)
    json_path, markdown_path = collector.write_report(tmp_path, report, args.output_json, args.output_markdown)

    archive = collector.archive_report(tmp_path, report, json_path, markdown_path, args)

    assert archive["entry_id"] == "2026-07-03-external-customer-host-rehearsal-v2"
    assert (
        tmp_path
        / "history"
        / "2026-07-03-external-customer-host-rehearsal-v2"
        / "external_customer_host_rehearsal_v2.json"
    ).exists()
    assert (tmp_path / "history" / "index.json").exists()
    assert (tmp_path / "history" / "trend.md").exists()
