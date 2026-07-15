from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_release_evidence_module():
    root = Path(__file__).resolve().parents[4]
    module_path = root / "scripts" / "ci" / "collect_release_evidence.py"
    spec = importlib.util.spec_from_file_location("collect_release_evidence", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_release_evidence_normalizes_status_and_separates_advisory() -> None:
    evidence = _load_release_evidence_module()

    assert evidence.normalize_status("pass") == "passed"
    assert evidence.normalize_status("caution") == "caution"
    assert evidence.normalize_status("not provided") == "not_provided"
    assert evidence.calculate_overall_status(
        [{"status": "passed"}, {"status": "passed"}, {"status": "passed"}],
        [{"status": "caution"}],
    ) == "warning"
    assert evidence.calculate_overall_status(
        [{"status": "failed"}, {"status": "passed"}],
        [{"status": "passed"}],
    ) == "failed"


def test_release_evidence_records_missing_optional_input_without_clean_success(tmp_path: Path) -> None:
    evidence = _load_release_evidence_module()
    bundle = evidence.build_bundle(
        [
            evidence.SourceInput("canonical_pre_release", "Canonical", "required_gate", True, status="passed"),
            evidence.SourceInput("openspec_strict_validation", "OpenSpec", "required_gate", True, status="passed"),
            evidence.SourceInput("offline_benchmark_validation", "Benchmark", "required_gate", True, status="passed"),
            evidence.SourceInput("real_repo_benchmark_comparison", "Real repo comparison", "advisory_signal", False),
        ],
        root=tmp_path,
        generated_at="2026-05-08T00:00:00+00:00",
    )

    assert bundle["overall_status"] == "warning"
    assert bundle["missing_inputs"] == [
        {
            "id": "real_repo_benchmark_comparison",
            "label": "Real repo comparison",
            "required": False,
            "status": "not_provided",
        }
    ]


def test_release_evidence_handles_invalid_provided_path_as_warning(tmp_path: Path) -> None:
    evidence = _load_release_evidence_module()
    bundle = evidence.build_bundle(
        [
            evidence.SourceInput("canonical_pre_release", "Canonical", "required_gate", True, status="passed"),
            evidence.SourceInput("openspec_strict_validation", "OpenSpec", "required_gate", True, status="passed"),
            evidence.SourceInput("offline_benchmark_validation", "Benchmark", "required_gate", True, status="passed"),
            evidence.SourceInput(
                "real_repo_benchmark_comparison",
                "Real repo comparison",
                "advisory_signal",
                False,
                path=Path("missing.json"),
            ),
        ],
        root=tmp_path,
        generated_at="2026-05-08T00:00:00+00:00",
    )

    item = next(item for item in bundle["advisory_signals"] if item["id"] == "real_repo_benchmark_comparison")
    assert bundle["overall_status"] == "warning"
    assert item["status"] == "warning"
    assert "source path does not exist" in bundle["warnings"][0]


def test_release_evidence_markdown_discloses_guardrail_and_benchmark_warnings(tmp_path: Path) -> None:
    evidence = _load_release_evidence_module()
    guardrail_path = tmp_path / "guardrail.json"
    comparison_path = tmp_path / "comparison.json"
    guardrail_path.write_text(
        json.dumps(
            {
                "agent_status": "caution",
                "summary": "Governance guardrail found advisory concerns.",
                "context": {"diff_status": "pass", "drift_status": "drift_detected", "advisory_only": True},
            }
        ),
        encoding="utf-8",
    )
    comparison_path.write_text(
        json.dumps(
            {
                "comparison_type": "real-repo-benchmark-regression",
                "summary": {
                    "repositories": 2,
                    "regressed": 1,
                    "operationally_blocked": 1,
                    "improved": 0,
                    "sparse_movements": {
                        "improved": 0,
                        "regressed": 1,
                        "operationally_blocked": 1,
                        "not_provided": 0,
                    },
                    "release_evidence_ready": True,
                },
            }
        ),
        encoding="utf-8",
    )

    bundle = evidence.build_bundle(
        [
            evidence.SourceInput("canonical_pre_release", "Canonical", "required_gate", True, status="passed"),
            evidence.SourceInput("openspec_strict_validation", "OpenSpec", "required_gate", True, status="passed"),
            evidence.SourceInput("offline_benchmark_validation", "Benchmark", "required_gate", True, status="passed"),
            evidence.SourceInput("governance_guardrail", "Governance guardrail", "advisory_signal", False, path=guardrail_path),
            evidence.SourceInput(
                "real_repo_benchmark_comparison",
                "Real repo comparison",
                "advisory_signal",
                False,
                path=comparison_path,
            ),
        ],
        root=tmp_path,
        generated_at="2026-05-08T00:00:00+00:00",
    )
    markdown = evidence.render_markdown(bundle)

    assert bundle["overall_status"] == "warning"
    assert "caution" in markdown
    assert "operationally_blocked" in markdown
    assert "regressed" in markdown
    assert "Governance guardrail found advisory concerns." in markdown
    assert bundle["source_paths"]["governance_guardrail"] == "guardrail.json"
    assert bundle["source_paths"]["real_repo_benchmark_comparison"] == "comparison.json"
    benchmark = next(item for item in bundle["advisory_signals"] if item["id"] == "real_repo_benchmark_comparison")
    assert benchmark["details"]["sparse_regressed"] == 1
    assert benchmark["details"]["sparse_operationally_blocked"] == 1
