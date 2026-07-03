from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[4]
    module_path = root / "scripts" / "ci" / "collect_full_chain_random_repo_release_rehearsal.py"
    spec = importlib.util.spec_from_file_location("collect_full_chain_random_repo_release_rehearsal", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_json(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_full_chain_bundle_preserves_random_repo_and_warning_lanes(tmp_path: Path) -> None:
    collector = _load_module()
    multi_repo = _write_json(
        tmp_path / "multi-repo.json",
        {
            "status": "warning",
            "selected_repo_ids": ["httpx", "fastapi"],
            "summary": {"selected_repositories": 2, "pass": 1, "warning": 1, "blocking": 0},
            "recommended_follow_up": ["inspect warning repo"],
        },
    )
    release = _write_json(
        tmp_path / "release.json",
        {"status": "warning", "summary": {"pass": 2, "warning": 5, "blocking": 0}},
    )
    customer_host = _write_json(
        tmp_path / "customer-host.json",
        {
            "status": "warning",
            "host_proof_level": "customer_controlled_with_browser_smoke",
            "summary": {"pass": 3, "warning": 4, "blocking": 0},
        },
    )
    history = _write_json(tmp_path / "index.json", {"entries": [{"entry_id": "latest", "status": "warning"}]})
    args = collector.parse_args(
        [
            "--multi-repo-diagnosis-json",
            str(multi_repo),
            "--release-rehearsal-json",
            str(release),
            "--customer-host-v2-json",
            str(customer_host),
            "--readiness-history-json",
            str(history),
            "--browser-status",
            "passed",
            "--browser-summary",
            "team flow passed",
        ]
    )

    report = collector.build_report(args, tmp_path)
    markdown = collector.render_markdown(report)

    assert report["status"] == "warning"
    assert report["selected_repo_ids"] == ["httpx", "fastapi"]
    assert report["summary"]["selected_repositories"] == 2
    assert {lane["id"]: lane["status"] for lane in report["lanes"]}["browser_rehearsal"] == "pass"
    assert {lane["id"]: lane["status"] for lane in report["lanes"]}["customer_host_v2"] == "warning"
    assert "httpx, fastapi" in markdown


def test_full_chain_bundle_keeps_missing_sources_visible(tmp_path: Path) -> None:
    collector = _load_module()
    args = collector.parse_args(
        [
            "--multi-repo-diagnosis-json",
            "",
            "--release-rehearsal-json",
            "",
            "--customer-host-v2-json",
            "",
            "--readiness-history-json",
            "",
        ]
    )

    report = collector.build_report(args, tmp_path)

    assert report["status"] == "warning"
    assert report["selected_repo_ids"] == []
    assert all(lane["status"] in {"not_provided", "operator_guided"} for lane in report["lanes"])
    assert "Run random real GitHub repository diagnosis" in report["recommended_next_actions"][0]


def test_full_chain_bundle_archives_to_readiness_history(tmp_path: Path) -> None:
    collector = _load_module()
    multi_repo = _write_json(
        tmp_path / "multi-repo.json",
        {"status": "pass", "selected_repo_ids": ["httpx"], "summary": {"selected_repositories": 1}},
    )
    args = collector.parse_args(
        [
            "--multi-repo-diagnosis-json",
            str(multi_repo),
            "--release-rehearsal-json",
            "",
            "--customer-host-v2-json",
            "",
            "--readiness-history-json",
            "",
            "--generated-at",
            "2026-07-03T00:00:00+00:00",
            "--output-json",
            str(tmp_path / "full-chain.json"),
            "--output-markdown",
            str(tmp_path / "full-chain.md"),
            "--archive-history",
            "--history-root",
            str(tmp_path / "history"),
        ]
    )
    report = collector.build_report(args, tmp_path)
    json_path, markdown_path = collector.write_report(tmp_path, report, args.output_json, args.output_markdown)

    archive = collector.archive_report(tmp_path, report, json_path, markdown_path, args)

    assert archive["entry_id"] == "2026-07-03-full-chain-random-repo-release-rehearsal"
    assert (
        tmp_path
        / "history"
        / "2026-07-03-full-chain-random-repo-release-rehearsal"
        / "full_chain_random_repo_release_rehearsal.json"
    ).exists()
    assert (tmp_path / "history" / "index.json").exists()
    assert (tmp_path / "history" / "trend.md").exists()
