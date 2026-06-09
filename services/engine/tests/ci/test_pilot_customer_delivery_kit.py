from __future__ import annotations

import importlib.util
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


def test_pilot_customer_delivery_kit_verifier_passes_current_docs() -> None:
    verifier = _load_script("verify_pilot_customer_delivery_kit")
    root = Path(__file__).resolve().parents[4]

    bundle = verifier.verify_delivery_kit(root, generated_at="2026-06-09T00:00:00+00:00")
    markdown = verifier.render_markdown(bundle)

    assert bundle["status"] == "pass"
    assert bundle["blockers"] == []
    assert bundle["entrypoint"] == "docs/project/pilot-customer-delivery-kit.md"
    assert "Pilot Customer Delivery Kit Verification" in markdown
    assert "customer-specific entitlement" in markdown.lower()


def test_pilot_customer_delivery_kit_verifier_blocks_missing_reference(tmp_path: Path) -> None:
    verifier = _load_script("verify_pilot_customer_delivery_kit")
    root = tmp_path
    project = root / "docs" / "project"
    project.mkdir(parents=True)
    for relative in verifier.REQUIRED_DOCS.values():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("placeholder", encoding="utf-8")

    bundle = verifier.verify_delivery_kit(root, generated_at="2026-06-09T00:00:00+00:00")

    assert bundle["status"] == "blocking"
    assert any(blocker["id"].startswith("reference:docs/project/pilot-customer-delivery-kit.md") for blocker in bundle["blockers"])


def test_pilot_customer_delivery_kit_verifier_blocks_missing_doc(tmp_path: Path) -> None:
    verifier = _load_script("verify_pilot_customer_delivery_kit")

    bundle = verifier.verify_delivery_kit(tmp_path, generated_at="2026-06-09T00:00:00+00:00")

    assert bundle["status"] == "blocking"
    assert any(blocker["id"] == "doc:entry" for blocker in bundle["blockers"])
