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


def test_private_repo_pilot_evidence_verifier_accepts_safe_sample() -> None:
    verifier = _load_script("verify_private_repo_pilot_evidence")
    root = Path(__file__).resolve().parents[4]

    bundle = verifier.verify_private_repo_pilot_evidence(
        evidence_json=root / "templates" / "private-repo-pilot-evidence.example.json",
        evidence_markdown=root / "docs" / "project" / "private-repo-pilot-evidence-example.md",
        generated_at="2026-06-10T00:00:00+00:00",
    )
    markdown = verifier.render_markdown(bundle)

    assert bundle["status"] == "operator_guided"
    assert bundle["blockers"] == []
    assert bundle["handoff_summary"]["advisory_only"] is True
    assert "Private Repo Pilot Evidence Verification" in markdown
    assert "operator_guided" in markdown


def test_private_repo_pilot_evidence_verifier_blocks_missing_redaction_statement() -> None:
    verifier = _load_script("verify_private_repo_pilot_evidence")
    root = Path(__file__).resolve().parents[4]
    scratch = _scratch_dir("private-repo-missing-redaction")
    evidence_json = scratch / "evidence.json"
    evidence_markdown = scratch / "evidence.md"

    data = json.loads((root / "templates" / "private-repo-pilot-evidence.example.json").read_text(encoding="utf-8"))
    data["redaction"]["redaction_statement"] = ""
    evidence_json.write_text(json.dumps(data), encoding="utf-8")
    evidence_markdown.write_text("Repository tokens and provider keys remain on the customer-controlled host.", encoding="utf-8")

    bundle = verifier.verify_private_repo_pilot_evidence(
        evidence_json=evidence_json,
        evidence_markdown=evidence_markdown,
        generated_at="2026-06-10T00:00:00+00:00",
    )

    assert bundle["status"] == "blocking"
    assert any(blocker["id"] == "json:redaction_statement" for blocker in bundle["blockers"])
    assert any(str(blocker["id"]).startswith("markdown:phrase:") for blocker in bundle["blockers"])


def test_private_repo_pilot_evidence_verifier_blocks_obvious_token_leakage() -> None:
    verifier = _load_script("verify_private_repo_pilot_evidence")
    root = Path(__file__).resolve().parents[4]
    scratch = _scratch_dir("private-repo-token-leak")
    evidence_json = scratch / "evidence.json"
    evidence_markdown = scratch / "evidence.md"

    data = json.loads((root / "templates" / "private-repo-pilot-evidence.example.json").read_text(encoding="utf-8"))
    data["credential_custody"]["custody_statement"] = "GITHUB_TOKEN=test-placeholder-token"
    evidence_json.write_text(json.dumps(data), encoding="utf-8")
    evidence_markdown.write_text(
        (root / "docs" / "project" / "private-repo-pilot-evidence-example.md").read_text(encoding="utf-8")
        + "\nGITHUB_TOKEN=test-placeholder-token\n",
        encoding="utf-8",
    )

    bundle = verifier.verify_private_repo_pilot_evidence(
        evidence_json=evidence_json,
        evidence_markdown=evidence_markdown,
        generated_at="2026-06-10T00:00:00+00:00",
    )

    assert bundle["status"] == "blocking"
    assert any(blocker["id"] == "json:forbidden_material" for blocker in bundle["blockers"])
    assert any(blocker["id"] == "markdown:forbidden_material" for blocker in bundle["blockers"])
