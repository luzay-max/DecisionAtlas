from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[4]
    module_path = root / "scripts" / "ci" / "collect_external_self_hosted_install_evidence.py"
    spec = importlib.util.spec_from_file_location("collect_external_self_hosted_install_evidence", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_json(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _valid_payload() -> dict:
    return {
        "evidence_label": "external-test",
        "external_host": {
            "host_class": "clean-vm",
            "os": "Ubuntu 24.04",
            "runtime": "Docker Engine",
            "is_customer_controlled": True,
            "operator": "customer-operator",
        },
        "package_identity": {
            "package_label": "decisionatlas-self-hosted",
            "version_label": "test-version",
            "commit": "abc123",
            "package_manifest_sha256": "sha256-placeholder",
        },
        "lanes": {
            "package_identity": {"status": "passed", "evidence": "manifest recorded"},
            "startup": {"status": "passed", "evidence": "stack started"},
            "health": {"status": "warning", "evidence": "engine health was rerun once"},
            "browser_smoke": {"status": "operator_guided", "evidence": "operator will rerun before handoff"},
            "repository_import": {"status": "not_provided", "evidence": "repo import deferred"},
            "readiness_evidence": {"status": "passed", "evidence": "release evidence attached"},
            "redaction_review": {"status": "passed", "evidence": "reviewed"},
        },
        "source_evidence_paths": [".tmp/release-evidence.md"],
        "limitations": ["public repo import deferred"],
        "redaction_acknowledgement": {"acknowledged": True, "reviewer": "customer-operator"},
    }


def test_external_evidence_generates_json_and_markdown_with_non_pass_states(tmp_path: Path) -> None:
    collector = _load_module()
    input_json = _write_json(tmp_path / "external.json", _valid_payload())
    args = collector.parse_args(
        [
            "--input-json",
            str(input_json),
            "--generated-at",
            "2026-07-02T00:00:00+00:00",
        ]
    )

    bundle = collector.build_evidence(args, tmp_path)
    markdown = collector.render_markdown(bundle)

    assert bundle["status"] == "warning"
    assert bundle["external_host"]["is_customer_controlled"] is True
    assert {lane["id"]: lane["status"] for lane in bundle["lanes"]}["startup"] == "passed"
    assert {lane["id"]: lane["status"] for lane in bundle["lanes"]}["repository_import"] == "not_provided"
    assert "External Self-Hosted Install Evidence" in markdown
    assert "operator_guided" in markdown


def test_external_evidence_blocks_missing_input(tmp_path: Path) -> None:
    collector = _load_module()
    args = collector.parse_args(["--input-json", str(tmp_path / "missing.json")])

    bundle = collector.build_evidence(args, tmp_path)

    assert bundle["status"] == "blocked"
    assert any(lane["id"] == "package_identity" and lane["status"] == "blocked" for lane in bundle["lanes"])


def test_external_evidence_blocks_missing_required_lanes(tmp_path: Path) -> None:
    collector = _load_module()
    payload = _valid_payload()
    del payload["lanes"]["package_identity"]
    input_json = _write_json(tmp_path / "external.json", payload)
    args = collector.parse_args(["--input-json", str(input_json)])

    bundle = collector.build_evidence(args, tmp_path)

    assert bundle["status"] == "blocked"
    assert {lane["id"]: lane["status"] for lane in bundle["lanes"]}["package_identity"] == "blocked"


def test_external_evidence_blocks_secret_like_material(tmp_path: Path) -> None:
    collector = _load_module()
    payload = _valid_payload()
    payload["lanes"]["startup"]["evidence"] = "LLM_API_KEY=sk-test-secret-password"
    input_json = _write_json(tmp_path / "external.json", payload)
    args = collector.parse_args(["--input-json", str(input_json)])

    bundle = collector.build_evidence(args, tmp_path)
    markdown = collector.render_markdown(bundle)

    assert bundle["status"] == "blocked"
    assert any(finding["id"] == "token_like_value" for finding in bundle["redaction_findings"])
    assert {lane["id"]: lane["status"] for lane in bundle["lanes"]}["redaction_review"] == "blocked"
    assert "sk-test-secret-password" not in markdown


def test_external_evidence_normalizes_legacy_status_aliases(tmp_path: Path) -> None:
    collector = _load_module()
    payload = _valid_payload()
    payload["lanes"]["startup"]["status"] = "pass"
    payload["lanes"]["health"]["status"] = "blocking"
    input_json = _write_json(tmp_path / "external.json", payload)
    args = collector.parse_args(["--input-json", str(input_json)])

    bundle = collector.build_evidence(args, tmp_path)
    statuses = {lane["id"]: lane["status"] for lane in bundle["lanes"]}

    assert statuses["startup"] == "passed"
    assert statuses["health"] == "blocked"
    assert bundle["status"] == "blocked"
