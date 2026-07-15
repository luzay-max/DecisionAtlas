from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[4]
    module_path = root / "scripts" / "ci" / "collect_random_repo_warning_lane_reduction.py"
    spec = importlib.util.spec_from_file_location("collect_random_repo_warning_lane_reduction", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_json(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_warning_lane_reducer_classifies_product_and_operator_lanes(tmp_path: Path) -> None:
    collector = _load_module()
    multi_repo = _write_json(
        tmp_path / "multi-repo.json",
        {
            "status": "warning",
            "selected_repo_ids": ["n8n", "rich"],
            "summary": {"selected_repositories": 2, "warning": 2, "blocking": 0},
            "repositories": [
                {
                    "id": "n8n",
                    "status": "warning",
                    "summary": {"recommended_follow_up": ["review_candidates_or_ask_why", "evaluate_or_monitor_drift"]},
                }
            ],
        },
    )
    release = _write_json(
        tmp_path / "release.json",
        {
            "status": "warning",
            "summary": {"operator_guided_lanes": 1, "warning": 1},
            "lanes": [{"id": "hosted_readiness", "status": "operator_guided", "summary": {"manual": True}}],
        },
    )
    args = collector.parse_args(
        [
            "--multi-repo-diagnosis-json",
            str(multi_repo),
            "--release-rehearsal-json",
            str(release),
            "--generated-at",
            "2026-07-04T00:00:00+00:00",
        ]
    )

    report = collector.build_report(args, tmp_path)
    categories = {lane["id"]: lane["category"] for lane in report["classified_lanes"]}

    assert report["status"] == "warning"
    assert report["selected_repo_ids"] == ["n8n", "rich"]
    assert categories["multi_repo_diagnosis:n8n"] == "product_controlled"
    assert categories["release_rehearsal:hosted_readiness"] == "operator_guided"
    assert report["summary"]["product_controlled"] >= 1
    assert report["summary"]["operator_guided"] >= 1
    assert report["reduction_actions"][0]["priority"] == "P0"


def test_warning_lane_reducer_marks_missing_sources_not_provided(tmp_path: Path) -> None:
    collector = _load_module()
    args = collector.parse_args(["--generated-at", "2026-07-04T00:00:00+00:00"])

    report = collector.build_report(args, tmp_path)

    assert report["status"] == "warning"
    assert report["summary"]["not_provided"] == 4
    assert all(source["status"] == "not_provided" for source in report["sources"])
    assert any(action["category"] == "not_provided" for action in report["reduction_actions"])


def test_warning_lane_reducer_propagates_blocking_lanes(tmp_path: Path) -> None:
    collector = _load_module()
    full_chain = _write_json(
        tmp_path / "full-chain.json",
        {
            "status": "blocking",
            "selected_repo_ids": ["pallets/flask"],
            "lanes": [{"id": "provider", "status": "provider_failure", "summary": {"message": "GitHub timeout"}}],
        },
    )
    args = collector.parse_args(["--full-chain-json", str(full_chain)])

    report = collector.build_report(args, tmp_path)

    assert report["status"] == "blocking"
    assert report["summary"]["blocking"] >= 1
    assert any(lane["category"] == "blocking" for lane in report["classified_lanes"])
    assert report["reduction_actions"][0]["category"] == "blocking"


def test_warning_lane_reducer_writes_json_and_markdown(tmp_path: Path) -> None:
    collector = _load_module()
    multi_repo = _write_json(
        tmp_path / "multi-repo.json",
        {
            "status": "warning",
            "selected_repo_ids": ["Textualize/rich"],
            "repositories": [{"id": "rich", "status": "warning", "summary": {"why": "missing support evidence"}}],
        },
    )
    output_json = tmp_path / "out.json"
    output_markdown = tmp_path / "out.md"
    args = collector.parse_args(
        [
            "--multi-repo-diagnosis-json",
            str(multi_repo),
            "--output-json",
            str(output_json),
            "--output-markdown",
            str(output_markdown),
        ]
    )
    report = collector.build_report(args, tmp_path)

    json_path, markdown_path = collector.write_report(tmp_path, report, args.output_json, args.output_markdown)

    assert json_path == output_json
    assert markdown_path == output_markdown
    assert json.loads(output_json.read_text(encoding="utf-8"))["evidence_type"] == "random-repo-warning-lane-reduction"
    markdown = output_markdown.read_text(encoding="utf-8")
    assert "Random Repo Warning Lane Reduction" in markdown
    assert "Textualize/rich" in markdown


def test_warning_lane_reducer_surfaces_product_controlled_grounding_details(tmp_path: Path) -> None:
    collector = _load_module()
    multi_repo = _write_json(
        tmp_path / "multi-repo.json",
        {
            "status": "warning",
            "selected_repo_ids": ["rich"],
            "repositories": [
                {
                    "id": "rich",
                    "repo": "Textualize/rich",
                    "status": "warning",
                    "action_categories": {
                        "product_controlled": 2,
                        "operator_setup": 0,
                        "external_dependency": 0,
                        "not_provided": 0,
                        "blocking": 0,
                    },
                    "accepted_baseline": {
                        "status": "empty",
                        "strength": "none",
                        "candidate_count": 1,
                        "accepted_count": 0,
                    },
                    "grounding_summary": {
                        "warning_lanes_with_grounding": 2,
                        "reason_codes": ["missing_accepted_decision_evidence", "unknown_grounding_gap"],
                    },
                    "lane_reasons": {
                        "why_search": [{"code": "missing_accepted_decision_evidence"}],
                        "drift": [{"code": "unknown_grounding_gap"}],
                    },
                }
            ],
        },
    )
    output_markdown = tmp_path / "out.md"
    args = collector.parse_args(
        [
            "--multi-repo-diagnosis-json",
            str(multi_repo),
            "--output-markdown",
            str(output_markdown),
        ]
    )

    report = collector.build_report(args, tmp_path)
    lane = next(item for item in report["classified_lanes"] if item["id"] == "multi_repo_diagnosis:rich")

    assert lane["category"] == "product_controlled"
    assert lane["grounding"]["reason_codes"] == ["missing_accepted_decision_evidence", "unknown_grounding_gap"]
    assert lane["accepted_baseline"]["status"] == "empty"
    assert lane["accepted_baseline"]["accepted_count"] == 0

    collector.write_report(tmp_path, report, None, str(output_markdown))
    markdown = output_markdown.read_text(encoding="utf-8")

    assert "missing_accepted_decision_evidence" in markdown
    assert "unknown_grounding_gap" in markdown
    assert "accepted_baseline" in markdown


def test_warning_lane_reducer_uses_action_categories_for_aggregate_lanes(tmp_path: Path) -> None:
    collector = _load_module()
    multi_repo = _write_json(
        tmp_path / "multi-repo.json",
        {
            "status": "warning",
            "selected_repo_ids": ["n8n", "rich"],
            "summary": {
                "selected_repositories": 2,
                "warning": 2,
                "blocking": 0,
                "action_categories": {
                    "product_controlled": 0,
                    "operator_setup": 8,
                    "external_dependency": 0,
                    "not_provided": 2,
                    "blocking": 0,
                },
            },
        },
    )
    args = collector.parse_args(["--multi-repo-diagnosis-json", str(multi_repo)])

    report = collector.build_report(args, tmp_path)
    lane = next(item for item in report["classified_lanes"] if item["id"] == "multi_repo_diagnosis:source")

    assert lane["category"] == "operator_guided"
    assert report["summary"]["product_controlled"] == 0
    assert report["summary"]["operator_guided"] >= 1


def test_warning_lane_reducer_deduplicates_release_aggregate_multi_repo_lanes(tmp_path: Path) -> None:
    collector = _load_module()
    release = _write_json(
        tmp_path / "release.json",
        {
            "status": "warning",
            "lanes": [
                {
                    "id": "multi_repo_diagnosis",
                    "status": "warning",
                    "summary": {
                        "action_categories": {
                            "product_controlled": 2,
                            "operator_setup": 0,
                            "external_dependency": 0,
                            "not_provided": 0,
                            "blocking": 0,
                        }
                    },
                }
            ],
        },
    )
    args = collector.parse_args(["--release-rehearsal-json", str(release)])

    report = collector.build_report(args, tmp_path)
    lane = next(item for item in report["classified_lanes"] if item["id"] == "release_rehearsal:multi_repo_diagnosis")

    assert lane["category"] == "operator_guided"
    assert report["summary"]["product_controlled"] == 0
