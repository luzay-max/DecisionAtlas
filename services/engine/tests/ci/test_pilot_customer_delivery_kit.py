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


def _scratch_dir(name: str) -> Path:
    root = Path(__file__).resolve().parents[4]
    path = root / ".tmp" / "ci-test-scratch" / name
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path


def test_pilot_customer_delivery_kit_verifier_passes_current_docs() -> None:
    verifier = _load_script("verify_pilot_customer_delivery_kit")
    root = Path(__file__).resolve().parents[4]

    bundle = verifier.verify_delivery_kit(root, generated_at="2026-06-09T00:00:00+00:00")
    markdown = verifier.render_markdown(bundle)

    assert bundle["status"] == "pass"
    assert bundle["blockers"] == []
    assert bundle["entrypoint"] == "docs/project/pilot-customer-delivery-kit.md"
    assert bundle["materials"]["sales_page"] == "docs/project/commercial-sales-page-draft.md"
    assert bundle["materials"]["one_page_brief"] == "docs/project/commercial-one-page-brief.md"
    assert bundle["materials"]["use_cases"] == "docs/project/commercial-use-cases.md"
    assert bundle["materials"]["private_repo_evidence_template"] == "docs/project/private-repo-pilot-evidence-template.md"
    assert bundle["materials"]["private_repo_evidence_example"] == "docs/project/private-repo-pilot-evidence-example.md"
    assert "Pilot Customer Delivery Kit Verification" in markdown
    assert "customer-specific entitlement" in markdown.lower()
    assert "commercial-use-cases.md" in markdown
    assert "Private repository pilot evidence" in markdown


def test_pilot_customer_delivery_kit_verifier_blocks_missing_reference() -> None:
    verifier = _load_script("verify_pilot_customer_delivery_kit")
    root = _scratch_dir("pilot-kit-missing-reference")
    project = root / "docs" / "project"
    project.mkdir(parents=True)
    for relative in verifier.REQUIRED_DOCS.values():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("placeholder", encoding="utf-8")

    bundle = verifier.verify_delivery_kit(root, generated_at="2026-06-09T00:00:00+00:00")

    assert bundle["status"] == "blocking"
    assert any(blocker["id"].startswith("reference:docs/project/pilot-customer-delivery-kit.md") for blocker in bundle["blockers"])
    assert any(blocker["id"].startswith("reference:docs/project/commercial-sales-page-draft.md") for blocker in bundle["blockers"])


def test_pilot_customer_delivery_kit_verifier_blocks_missing_doc() -> None:
    verifier = _load_script("verify_pilot_customer_delivery_kit")
    root = _scratch_dir("pilot-kit-missing-doc")

    bundle = verifier.verify_delivery_kit(root, generated_at="2026-06-09T00:00:00+00:00")

    assert bundle["status"] == "blocking"
    assert any(blocker["id"] == "doc:entry" for blocker in bundle["blockers"])
