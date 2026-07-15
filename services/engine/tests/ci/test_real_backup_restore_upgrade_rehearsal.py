from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_script():
    root = Path(__file__).resolve().parents[4]
    module_path = root / "scripts" / "ci" / "rehearse_real_backup_restore_upgrade.py"
    spec = importlib.util.spec_from_file_location("rehearse_real_backup_restore_upgrade", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_real_rehearsal_generates_scratch_backup_restore_evidence(tmp_path: Path) -> None:
    rehearsal = _load_script()
    args = rehearsal.parse_args(
        [
            "--label",
            "real-test",
            "--scratch-root",
            str(tmp_path / "scratch"),
            "--previous-version",
            "before",
            "--target-version",
            "after",
            "--post-upgrade-status",
            "pass",
            "--rollback-plan-status",
            "pass",
            "--generated-at",
            "2026-07-02T00:00:00+00:00",
        ]
    )

    bundle = rehearsal.build_rehearsal(args, tmp_path)
    markdown = rehearsal.render_markdown(bundle)

    assert bundle["status"] == "pass"
    assert bundle["scratch_scope"]["scratch_only"] is True
    assert bundle["integrity"]["restore_matches_source"] is True
    assert bundle["integrity"]["source_record_count"] == 2
    assert bundle["blockers"] == []
    assert "Real Backup Restore Upgrade Rehearsal" in markdown


def test_real_rehearsal_detects_restore_mismatch(tmp_path: Path) -> None:
    rehearsal = _load_script()
    args = rehearsal.parse_args(
        [
            "--label",
            "mismatch-test",
            "--scratch-root",
            str(tmp_path / "scratch"),
            "--previous-version",
            "before",
            "--target-version",
            "after",
            "--post-upgrade-status",
            "pass",
            "--rollback-plan-status",
            "pass",
            "--inject-restore-mismatch",
        ]
    )

    bundle = rehearsal.build_rehearsal(args, tmp_path)

    assert bundle["status"] == "blocking"
    assert bundle["integrity"]["restore_matches_source"] is False
    assert any(blocker["id"] == "restore_validation" for blocker in bundle["blockers"])


def test_real_rehearsal_rejects_source_path_outside_scratch_root(tmp_path: Path) -> None:
    rehearsal = _load_script()
    outside = tmp_path / "outside.json"
    outside.write_text(json.dumps({"decisions": []}), encoding="utf-8")
    args = rehearsal.parse_args(
        [
            "--label",
            "unsafe-path-test",
            "--scratch-root",
            str(tmp_path / "scratch"),
            "--source-state-json",
            str(outside),
        ]
    )

    bundle = rehearsal.build_rehearsal(args, tmp_path)

    assert bundle["status"] == "blocking"
    assert any(blocker["id"] == "path_safety:source_state" for blocker in bundle["blockers"])


def test_real_rehearsal_blocks_secret_like_source_state(tmp_path: Path) -> None:
    rehearsal = _load_script()
    scratch = tmp_path / "scratch"
    source = scratch / "secret-test" / "source" / "state.json"
    source.parent.mkdir(parents=True)
    source.write_text(json.dumps({"decisions": [{"title": "LLM_API_KEY=sk-test-secret-password"}]}), encoding="utf-8")
    args = rehearsal.parse_args(
        [
            "--label",
            "secret-test",
            "--scratch-root",
            str(scratch),
            "--source-state-json",
            str(source),
        ]
    )

    bundle = rehearsal.build_rehearsal(args, tmp_path)
    markdown = rehearsal.render_markdown(bundle)

    assert bundle["status"] == "blocking"
    assert any(finding["id"] == "token_like_value" for finding in bundle["redaction_findings"])
    assert "sk-test-secret-password" not in markdown
