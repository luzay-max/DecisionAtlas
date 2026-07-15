from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_hosted_readiness_module():
    root = Path(__file__).resolve().parents[4]
    module_path = root / "scripts" / "demo" / "collect_hosted_readiness.py"
    spec = importlib.util.spec_from_file_location("collect_hosted_readiness", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_hosted_readiness_normalizes_status_and_blocks_public_walkthrough() -> None:
    hosted = _load_hosted_readiness_module()

    assert hosted.normalize_status("passed") == "pass"
    assert hosted.normalize_status("blocking") == "blocking"
    assert hosted.normalize_status("known limitation") == "known_limitation"
    assert hosted.normalize_status("operator guided") == "operator_guided"
    assert hosted.calculate_public_walkthrough_status(
        [
            {"required_for_public_walkthrough": True, "status": "pass"},
            {"required_for_public_walkthrough": True, "status": "blocking"},
            {"required_for_public_walkthrough": False, "status": "blocking"},
        ]
    ) == "blocking"


def test_hosted_readiness_missing_hosted_inputs_are_operator_guided(tmp_path: Path) -> None:
    hosted = _load_hosted_readiness_module()
    bundle = hosted.build_bundle(
        [
            hosted.LaneInput("web", "Web", "core", True, default_when_missing="operator_guided"),
            hosted.LaneInput("api", "API", "core", True, default_when_missing="operator_guided"),
            hosted.LaneInput("engine", "Engine", "core", True, default_when_missing="operator_guided"),
        ],
        root=tmp_path,
        generated_at="2026-05-08T00:00:00+00:00",
    )

    assert bundle["public_walkthrough_status"] == "operator_guided"
    assert bundle["public_walkthrough_decision"] == "operator_review_required"
    assert [item["id"] for item in bundle["missing_inputs"]] == ["web", "api", "engine"]


def test_hosted_readiness_invalid_required_report_path_blocks(tmp_path: Path) -> None:
    hosted = _load_hosted_readiness_module()
    bundle = hosted.build_bundle(
        [
            hosted.LaneInput(
                "hosted_health_check",
                "Health",
                "core",
                True,
                path=Path("missing-health.json"),
                command="scripts/demo/health-check.ps1",
                default_when_missing="operator_guided",
            )
        ],
        root=tmp_path,
        generated_at="2026-05-08T00:00:00+00:00",
    )

    assert bundle["public_walkthrough_status"] == "blocking"
    assert bundle["public_walkthrough_decision"] == "do_not_proceed"
    assert bundle["blockers"][0]["id"] == "hosted_health_check"
    assert "source path does not exist" in bundle["warnings"][0]


def test_hosted_readiness_markdown_discloses_scope_and_release_gate(tmp_path: Path) -> None:
    hosted = _load_hosted_readiness_module()
    guardrail_path = tmp_path / "guardrail.json"
    release_path = tmp_path / "release-evidence.json"
    benchmark_path = tmp_path / "benchmark.json"
    guardrail_path.write_text(
        json.dumps({"agent_status": "caution", "summary": "Guardrail caution."}),
        encoding="utf-8",
    )
    release_path.write_text(
        json.dumps({"overall_status": "warning", "missing_inputs": [{"id": "real_repo"}], "warnings": ["optional missing"]}),
        encoding="utf-8",
    )
    benchmark_path.write_text(
        json.dumps({"comparison_type": "real-repo-benchmark-regression", "summary": {"repositories": 1, "regressed": 1, "operationally_blocked": 1}}),
        encoding="utf-8",
    )

    bundle = hosted.build_bundle(
        [
            hosted.LaneInput("web", "Web", "core", True, status="pass"),
            hosted.LaneInput("api", "API", "core", True, status="pass"),
            hosted.LaneInput("engine", "Engine", "core", True, status="pass"),
            hosted.LaneInput("seeded", "Seeded", "public", True, status="pass"),
            hosted.LaneInput("governance_guardrail", "Guardrail", "governance", False, path=guardrail_path),
            hosted.LaneInput("release_evidence", "Release evidence", "release", False, path=release_path),
            hosted.LaneInput("real_repo_evidence", "Real repo", "optional", False, path=benchmark_path),
        ],
        root=tmp_path,
        generated_at="2026-05-08T00:00:00+00:00",
    )
    markdown = hosted.render_markdown(bundle)

    assert bundle["public_walkthrough_status"] == "pass"
    assert "non_blocking" in markdown
    assert "operator-guided evidence" in markdown
    assert "does not replace scripts/ci/pre-release.ps1" in markdown
    assert "scoped to demo-workspace" in markdown
    assert "operationally_blocked" in markdown
    assert bundle["source_paths"]["governance_guardrail"] == "guardrail.json"
    assert bundle["source_paths"]["release_evidence"] == "release-evidence.json"
    assert bundle["source_paths"]["real_repo_evidence"] == "benchmark.json"
