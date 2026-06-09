from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
STATUS_PASS = "pass"
STATUS_BLOCKING = "blocking"
STATUS_OPERATOR_GUIDED = "operator_guided"
STATUS_NOT_PROVIDED = "not_provided"

REQUIRED_DOCS = {
    "entry": "docs/project/pilot-customer-delivery-kit.md",
    "demo_script": "docs/project/pilot-demo-script.md",
    "deployment_checklist": "docs/project/pilot-deployment-checklist.md",
    "faq": "docs/project/pilot-customer-faq.md",
    "tier_comparison": "docs/project/pilot-tier-comparison.md",
    "delivery_email": "docs/project/pilot-delivery-email-template.md",
}

REQUIRED_REFERENCES = {
    "docs/project/pilot-customer-delivery-kit.md": [
        "self-hosted package",
        "clean install rehearsal",
        "team handoff report",
        "license/support boundary",
        "billing",
        "hosted multi-tenancy",
        "runtime license enforcement",
    ],
    "docs/project/pilot-demo-script.md": [
        "Repository Setup",
        "Decision Review",
        "Why-Search",
        "Drift And Governance",
        "Evidence And Handoff",
    ],
    "docs/project/pilot-deployment-checklist.md": [
        "DATABASE_URL",
        "REDIS_URL",
        "admin",
        "repository import",
        "clean install rehearsal",
        "team handoff report",
    ],
    "docs/project/pilot-customer-faq.md": [
        "credentials",
        "private repositories",
        "roles",
        "backups",
        "runtime license enforcement",
    ],
    "docs/project/pilot-tier-comparison.md": [
        "Community",
        "Team Self-hosted",
        "Enterprise Self-hosted",
        "Pilot Extension Path",
        "Runtime license enforcement",
    ],
    "docs/project/pilot-delivery-email-template.md": [
        "What This Pilot Covers",
        "Evidence To Review",
        "Not Included In This Pilot",
        "Feedback Requested",
    ],
}

OPTIONAL_CUSTOMER_LANES = [
    {
        "id": "signed_customer_agreement",
        "label": "Signed customer agreement",
        "status": STATUS_OPERATOR_GUIDED,
        "reason": "Commercial agreement is customer-specific and is not stored in the repository.",
    },
    {
        "id": "customer_specific_entitlement",
        "label": "Customer-specific entitlement",
        "status": STATUS_NOT_PROVIDED,
        "reason": "Use templates/self-hosted-entitlement.example.json as a private customer record when applicable.",
    },
    {
        "id": "private_repository_evidence",
        "label": "Private repository pilot evidence",
        "status": STATUS_OPERATOR_GUIDED,
        "reason": "Private repository evidence must be generated on the customer-controlled host.",
    },
]


def _display_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _check_required_docs(root: Path) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for doc_id, relative in REQUIRED_DOCS.items():
        path = root / relative
        checks.append(
            {
                "id": f"doc:{doc_id}",
                "label": f"Required pilot material {relative}",
                "status": STATUS_PASS if path.is_file() else STATUS_BLOCKING,
                "details": {"path": relative},
            }
        )
    return checks


def _check_required_references(root: Path) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for relative, needles in REQUIRED_REFERENCES.items():
        path = root / relative
        text = path.read_text(encoding="utf-8", errors="ignore") if path.is_file() else ""
        for needle in needles:
            checks.append(
                {
                    "id": f"reference:{relative}:{needle}",
                    "label": f"{relative} references {needle}",
                    "status": STATUS_PASS if needle.lower() in text.lower() else STATUS_BLOCKING,
                    "details": {"path": relative, "needle": needle},
                }
            )
    return checks


def calculate_status(checks: list[dict[str, Any]]) -> str:
    return STATUS_BLOCKING if any(check["status"] == STATUS_BLOCKING for check in checks) else STATUS_PASS


def verify_delivery_kit(root: Path, *, generated_at: str | None = None) -> dict[str, Any]:
    checks = [*_check_required_docs(root), *_check_required_references(root)]
    status = calculate_status(checks)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at or datetime.now(UTC).isoformat(),
        "status": status,
        "entrypoint": "docs/project/pilot-customer-delivery-kit.md",
        "materials": {doc_id: relative for doc_id, relative in REQUIRED_DOCS.items()},
        "checks": checks,
        "blockers": [check for check in checks if check["status"] == STATUS_BLOCKING],
        "optional_customer_lanes": OPTIONAL_CUSTOMER_LANES,
        "recommended_next_actions": [
            "Attach package verification, clean install rehearsal, release evidence, hosted readiness, benchmark comparison, handoff report, and license/support boundary before a pilot claim.",
            "Keep customer-specific agreements, entitlements, credentials, and private repository evidence outside the repository unless explicitly sanitized.",
        ],
    }


def _markdown_cell(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, (dict, list)):
        text = json.dumps(value, sort_keys=True, ensure_ascii=False)
    else:
        text = str(value)
    return text.replace("|", "\\|").replace("\n", "<br>") or "-"


def render_markdown(bundle: dict[str, Any]) -> str:
    lines = [
        "# Pilot Customer Delivery Kit Verification",
        "",
        f"- Generated at: `{bundle.get('generated_at')}`",
        f"- Entrypoint: `{bundle.get('entrypoint')}`",
        f"- Status: `{bundle.get('status')}`",
        "",
        "## Materials",
        "",
        "| Material | Path |",
        "| --- | --- |",
    ]
    materials = bundle.get("materials") if isinstance(bundle.get("materials"), dict) else {}
    for material_id in sorted(materials):
        lines.append(f"| {_markdown_cell(material_id)} | `{_markdown_cell(materials[material_id])}` |")

    lines.extend(["", "## Checks", "", "| Check | Status | Details |", "| --- | --- | --- |"])
    for check in bundle.get("checks", []):
        lines.append(f"| {_markdown_cell(check.get('label'))} | {_markdown_cell(check.get('status'))} | {_markdown_cell(check.get('details'))} |")

    lines.extend(["", "## Optional Customer-Specific Lanes", "", "| Lane | Status | Reason |", "| --- | --- | --- |"])
    for lane in bundle.get("optional_customer_lanes", []):
        lines.append(f"| {_markdown_cell(lane.get('label'))} | {_markdown_cell(lane.get('status'))} | {_markdown_cell(lane.get('reason'))} |")

    lines.extend(["", "## Recommended Next Actions", ""])
    for action in bundle.get("recommended_next_actions", []):
        lines.append(f"- {action}")
    lines.append("")
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify DecisionAtlas pilot customer delivery kit materials.")
    parser.add_argument("--output-json", type=Path, default=Path(".tmp/pilot-customer-delivery-kit-verification.json"))
    parser.add_argument("--output-markdown", type=Path, default=Path(".tmp/pilot-customer-delivery-kit-verification.md"))
    parser.add_argument("--generated-at")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    bundle = verify_delivery_kit(root, generated_at=args.generated_at)
    output_json = args.output_json if args.output_json.is_absolute() else root / args.output_json
    output_markdown = args.output_markdown if args.output_markdown.is_absolute() else root / args.output_markdown
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(bundle, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    output_markdown.write_text(render_markdown(bundle), encoding="utf-8")
    print(json.dumps(bundle, indent=2, sort_keys=True, ensure_ascii=False))
    return 1 if bundle["status"] == STATUS_BLOCKING else 0


if __name__ == "__main__":
    raise SystemExit(main())
