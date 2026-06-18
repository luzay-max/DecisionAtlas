from __future__ import annotations

import importlib.util
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


def _scratch_root(name: str) -> Path:
    root = Path(__file__).resolve().parents[4]
    scratch = root / ".tmp" / "ci-test-scratch" / name
    if scratch.exists():
        shutil.rmtree(scratch)
    scratch.mkdir(parents=True)
    return scratch


def _copy_required_docs(module, scratch: Path) -> None:
    root = Path(__file__).resolve().parents[4]
    for relative in module.REQUIRED_DOCS.values():
        source = root / relative
        target = scratch / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)


def test_pilot_commercial_proposal_kit_verifier_passes_current_docs() -> None:
    verifier = _load_script("verify_pilot_commercial_proposal_kit")
    root = Path(__file__).resolve().parents[4]

    bundle = verifier.verify_proposal_kit(root, generated_at="2026-06-18T00:00:00+00:00")
    markdown = verifier.render_markdown(bundle)

    assert bundle["status"] == "pass"
    assert bundle["blockers"] == []
    assert "Pilot Commercial Proposal Kit Verification" in markdown
    assert "filled_customer_quote" in {lane["id"] for lane in bundle["optional_customer_lanes"]}


def test_pilot_commercial_proposal_kit_verifier_blocks_missing_required_reference() -> None:
    verifier = _load_script("verify_pilot_commercial_proposal_kit")
    scratch = _scratch_root("proposal-kit-missing-reference")
    _copy_required_docs(verifier, scratch)
    quote_path = scratch / "docs" / "project" / "pilot-paid-quote-template.md"
    quote_path.write_text(
        quote_path.read_text(encoding="utf-8").replace("runtime license enforcement", "runtime boundary"),
        encoding="utf-8",
    )

    bundle = verifier.verify_proposal_kit(scratch, generated_at="2026-06-18T00:00:00+00:00")

    assert bundle["status"] == "blocking"
    assert any(
        blocker["id"] == "reference:docs/project/pilot-paid-quote-template.md:runtime license enforcement"
        for blocker in bundle["blockers"]
    )


def test_pilot_commercial_proposal_kit_verifier_blocks_customer_private_material() -> None:
    verifier = _load_script("verify_pilot_commercial_proposal_kit")
    scratch = _scratch_root("proposal-kit-private-material")
    _copy_required_docs(verifier, scratch)
    quote_path = scratch / "docs" / "project" / "pilot-paid-quote-template.md"
    quote_path.write_text(
        quote_path.read_text(encoding="utf-8") + "\ncustomer legal name: Example Corp\n",
        encoding="utf-8",
    )

    bundle = verifier.verify_proposal_kit(scratch, generated_at="2026-06-18T00:00:00+00:00")

    assert bundle["status"] == "blocking"
    assert any(
        blocker["id"] == "forbidden:docs/project/pilot-paid-quote-template.md"
        for blocker in bundle["blockers"]
    )
