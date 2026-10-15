from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[4]
    module_path = root / "scripts" / "ci" / "collect_pilot_customer_trial_package.py"
    spec = importlib.util.spec_from_file_location("collect_pilot_customer_trial_package", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _scratch_dir(name: str) -> Path:
    root = Path(__file__).resolve().parents[4]
    path = root / ".tmp" / "ci-test-scratch" / name
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path


def test_pilot_customer_trial_package_generates_warning_bundle_for_current_sample_evidence(tmp_path: Path) -> None:
    collector = _load_module()
    root = Path(__file__).resolve().parents[4]
    args = collector.parse_args(
        [
            "--generated-at",
            "2026-07-04T00:00:00+00:00",
            "--pilot-delivery-verification-json",
            ".tmp/pilot-customer-delivery-kit-verification.json",
            "--real-external-host-trial-json",
            ".tmp/real-external-host-trial-evidence.json",
            "--full-chain-json",
            ".tmp/full-chain-random-repo-release-rehearsal.json",
            "--output-json",
            str(tmp_path / "trial-package.json"),
            "--output-markdown",
            str(tmp_path / "trial-package.md"),
            "--bundle-dir",
            str(tmp_path / "bundle"),
            "--clean-bundle",
        ]
    )

    package = collector.build_package(args, root)
    json_path, markdown_path, bundle_dir = collector.write_outputs(root, package, args)

    assert package["status"] == "warning"
    assert package["summary"]["blocking"] == 0
    assert any(lane["id"] == "real_external_host_trial" for lane in package["evidence_lanes"])
    assert json_path.exists()
    assert markdown_path.exists()
    assert (bundle_dir / "README.md").exists()
    assert (bundle_dir / "operator-checklist.md").exists()
    assert (bundle_dir / "evidence-manifest.json").exists()


def test_pilot_customer_trial_package_blocks_missing_required_material(tmp_path: Path) -> None:
    collector = _load_module()
    root = _scratch_dir("pilot-trial-package-missing-material")

    args = collector.parse_args(["--generated-at", "2026-07-04T00:00:00+00:00"])
    package = collector.build_package(args, root)

    assert package["status"] == "blocking"
    assert any(lane["id"] == "material:pilot_delivery_entry" for lane in package["blockers"])


def test_pilot_customer_trial_package_preserves_missing_evidence_as_not_provided() -> None:
    collector = _load_module()
    root = Path(__file__).resolve().parents[4]

    args = collector.parse_args(["--generated-at", "2026-07-04T00:00:00+00:00"])
    package = collector.build_package(args, root)

    assert package["status"] == "warning"
    assert any(lane["id"] == "real_external_host_trial" and lane["status"] == "not_provided" for lane in package["evidence_lanes"])
    assert package["summary"]["not_provided"] >= 1


def test_pilot_customer_trial_package_blocks_sensitive_operator_note() -> None:
    collector = _load_module()
    root = Path(__file__).resolve().parents[4]

    args = collector.parse_args(["--operator-note", "GITHUB_TOKEN=ghp_secretvalue123"])
    package = collector.build_package(args, root)
    markdown = collector.render_markdown(package)

    assert package["status"] == "blocking"
    assert any(finding["id"] == "token_like_value" for finding in package["redaction_findings"])
    assert "ghp_secretvalue123" not in markdown


def test_pilot_customer_trial_package_can_pass_with_clean_evidence(tmp_path: Path) -> None:
    collector = _load_module()
    root = Path(__file__).resolve().parents[4]
    evidence_paths = {}
    for lane_id, _label, attr_name in collector.EVIDENCE_LANES:
        payload = {
            "status": "pass",
            "generated_at": "2026-07-04T00:00:00+00:00",
            "summary": {"pass": 1, "warning": 0, "blocking": 0},
        }
        if lane_id == "real_external_host_trial":
            payload["host_proof_level"] = "real_external_customer_controlled"
        if lane_id == "full_chain_random_repo_release":
            payload["selected_repo_ids"] = ["pallets/flask"]
        evidence_paths[attr_name] = _write_json(tmp_path / f"{lane_id}.json", payload)

    argv = ["--generated-at", "2026-07-04T00:00:00+00:00"]
    for attr_name, path in evidence_paths.items():
        argv.extend([f"--{attr_name.replace('_', '-')}", str(path)])
    args = collector.parse_args(argv)

    package = collector.build_package(args, root)

    assert package["status"] == "pass"
    assert package["blockers"] == []
