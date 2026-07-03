from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.ci import collect_release_rehearsal_evidence as rehearsal


def _write_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_missing_optional_inputs_are_warning_not_blocking(tmp_path: Path) -> None:
    args = rehearsal.parse_args(
        [
            "--no-default-discovery",
            "--generated-at",
            "2026-07-03T00:00:00+00:00",
        ]
    )

    report = rehearsal.build_report(args, tmp_path)

    assert report["status"] == "warning"
    assert report["summary"]["blocking"] == 0
    assert "release_evidence" in report["missing_lanes"]
    assert report["operator_guided_lanes"] == []


def test_warning_and_blocking_aggregation(tmp_path: Path) -> None:
    release = _write_json(tmp_path / "release.json", {"overall_status": "passed", "required_gates": [], "advisory_signals": []})
    hosted = _write_json(tmp_path / "hosted.json", {"overall_status": "blocking", "lanes": []})
    args = rehearsal.parse_args(
        [
            "--no-default-discovery",
            "--release-evidence-report",
            str(release),
            "--hosted-readiness-report",
            str(hosted),
        ]
    )

    report = rehearsal.build_report(args, tmp_path)

    assert report["status"] == "blocking"
    assert report["summary"]["blocking"] == 1


def test_render_markdown_lists_lanes(tmp_path: Path) -> None:
    report = {
        "label": "smoke",
        "generated_at": "now",
        "status": "warning",
        "summary": {"pass": 1, "warning": 1, "blocking": 0, "missing_lanes": 1},
        "lanes": [
            {"id": "release_evidence", "label": "Release evidence", "status": "pass", "source_path": "release.json", "summary": {"status": "pass"}},
            {"id": "guardrail_summary", "label": "Governance guardrail", "status": "not_provided", "source_path": None, "summary": {}},
        ],
        "missing_lanes": ["guardrail_summary"],
        "operator_guided_lanes": ["hosted_readiness"],
        "recommended_follow_up": ["attach guardrail"],
        "warnings": [],
        "sensitive_material_note": "no secrets",
    }

    markdown = rehearsal.render_markdown(report)

    assert "Release Rehearsal Evidence Bundle" in markdown
    assert "| Release evidence | pass | release.json |" in markdown
    assert "hosted_readiness" in markdown
    assert "attach guardrail" in markdown


def test_live_multi_repo_invocation_is_plumbed(monkeypatch, tmp_path: Path) -> None:
    calls = {}

    def fake_build_report(**kwargs):
        calls.update(kwargs)
        return {
            "status": "warning",
            "summary": {"selected_repositories": 1, "pass": 0, "warning": 1, "blocking": 0},
            "selected_repo_ids": ["httpx"],
            "recommended_follow_up": ["review_candidates"],
        }

    monkeypatch.setattr(rehearsal.multi_repo, "build_report", fake_build_report)
    monkeypatch.setattr(rehearsal.multi_repo, "render_markdown", lambda report: "# multi\n")
    args = rehearsal.parse_args(
        [
            "--no-default-discovery",
            "--run-multi-repo-diagnosis",
            "--repo-id",
            "httpx",
            "--multi-repo-output-json",
            str(tmp_path / "multi.json"),
            "--multi-repo-output-markdown",
            str(tmp_path / "multi.md"),
        ]
    )

    report = rehearsal.build_report(args, tmp_path)

    assert calls["repo_ids"] == ["httpx"]
    assert report["status"] == "warning"
    assert (tmp_path / "multi.json").exists()


def test_archive_bundle_writes_history_entry(tmp_path: Path) -> None:
    report = {
        "generated_at": "2026-07-03T00:00:00+00:00",
        "label": "smoke",
        "status": "warning",
        "summary": {"pass": 0, "warning": 1, "blocking": 0},
        "lanes": [{"id": "release_evidence", "status": "warning"}],
    }
    json_path = _write_json(tmp_path / "bundle.json", report)
    markdown_path = tmp_path / "bundle.md"
    markdown_path.write_text("# bundle\n", encoding="utf-8")

    archive = rehearsal.archive_bundle(tmp_path, report, json_path, markdown_path, "history")

    assert archive["entry_id"] == "2026-07-03-release-rehearsal-one-command"
    assert (tmp_path / "history" / archive["entry_id"] / "release_rehearsal.json").exists()
    assert (tmp_path / "history" / "release-rehearsal-index.json").exists()
