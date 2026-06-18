from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path


def _load_script(name: str):
    root = Path(__file__).resolve().parents[4]
    module_path = root / "scripts" / "ci" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _scratch_dir(name: str) -> Path:
    root = Path(__file__).resolve().parents[4]
    path = root / ".tmp" / "ci-test-scratch" / name
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path


def _safe_sample() -> dict:
    root = Path(__file__).resolve().parents[4]
    return json.loads((root / "templates" / "backup-restore-upgrade-rehearsal.example.json").read_text(encoding="utf-8"))


def test_backup_restore_upgrade_rehearsal_accepts_safe_sample() -> None:
    rehearsal = _load_script("rehearse_backup_restore_upgrade")
    root = Path(__file__).resolve().parents[4]

    bundle = rehearsal.rehearse_backup_restore_upgrade(
        input_json=root / "templates" / "backup-restore-upgrade-rehearsal.example.json",
        generated_at="2026-06-10T00:00:00+00:00",
    )
    markdown = rehearsal.render_markdown(bundle)

    assert bundle["status"] == "operator_guided"
    assert bundle["blockers"] == []
    assert bundle["continuity_summary"]["lane_status_counts"]["operator_guided"] == 6
    assert bundle["continuity_summary"]["lane_status_counts"]["not_provided"] == 2
    assert "Backup Restore Upgrade Rehearsal" in markdown
    assert "non-destructive" in markdown


def test_backup_restore_upgrade_rehearsal_blocks_missing_required_lane() -> None:
    rehearsal = _load_script("rehearse_backup_restore_upgrade")
    scratch = _scratch_dir("backup-restore-missing-lane")
    input_json = scratch / "rehearsal.json"
    data = _safe_sample()
    data["continuity_lanes"] = [
        lane for lane in data["continuity_lanes"] if lane["id"] != "rollback_plan"
    ]
    input_json.write_text(json.dumps(data), encoding="utf-8")

    bundle = rehearsal.rehearse_backup_restore_upgrade(
        input_json=input_json,
        generated_at="2026-06-10T00:00:00+00:00",
    )

    assert bundle["status"] == "blocking"
    assert any(blocker["id"] == "lane:present:rollback_plan" for blocker in bundle["blockers"])


def test_backup_restore_upgrade_rehearsal_blocks_invalid_status() -> None:
    rehearsal = _load_script("rehearse_backup_restore_upgrade")
    scratch = _scratch_dir("backup-restore-invalid-status")
    input_json = scratch / "rehearsal.json"
    data = _safe_sample()
    data["continuity_lanes"][0]["status"] = "clean"
    input_json.write_text(json.dumps(data), encoding="utf-8")

    bundle = rehearsal.rehearse_backup_restore_upgrade(
        input_json=input_json,
        generated_at="2026-06-10T00:00:00+00:00",
    )

    assert bundle["status"] == "blocking"
    assert any(blocker["id"] == "lane:status:database_backup" for blocker in bundle["blockers"])


def test_backup_restore_upgrade_rehearsal_blocks_obvious_secret_material() -> None:
    rehearsal = _load_script("rehearse_backup_restore_upgrade")
    scratch = _scratch_dir("backup-restore-secret")
    input_json = scratch / "rehearsal.json"
    data = _safe_sample()
    data["custody"]["custody_statement"] = "DATABASE_URL=redacted-placeholder"
    input_json.write_text(json.dumps(data), encoding="utf-8")

    bundle = rehearsal.rehearse_backup_restore_upgrade(
        input_json=input_json,
        generated_at="2026-06-10T00:00:00+00:00",
    )

    assert bundle["status"] == "blocking"
    assert any(blocker["id"] == "input:forbidden_material" for blocker in bundle["blockers"])
