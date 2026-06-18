from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
STATUS_PASS = "pass"
STATUS_BLOCKING = "blocking"
STATUS_OPERATOR_GUIDED = "operator_guided"
STATUS_NOT_PROVIDED = "not_provided"

REQUIRED_DOCS = {
    "entry": "docs/project/pilot-commercial-proposal-kit.md",
    "quote_template": "docs/project/pilot-paid-quote-template.md",
    "acceptance_checklist": "docs/project/pilot-acceptance-checklist.md",
    "support_renewal_upgrade": "docs/project/pilot-support-renewal-upgrade-boundary.md",
}

REQUIRED_REFERENCES = {
    "docs/project/pilot-commercial-proposal-kit.md": [
        "paid pilot",
        "quote assumptions",
        "acceptance checklist",
        "support boundary",
        "renewal",
        "upgrade",
        "package verification",
        "release evidence",
        "hosted/operator readiness",
        "readiness evidence history",
        "real-repo benchmark",
        "private-repo evidence",
        "backup/restore/upgrade",
        "billing",
        "hosted multi-tenancy",
        "runtime license enforcement",
        "not legal contracts",
    ],
    "docs/project/pilot-paid-quote-template.md": [
        "editable draft assumptions",
        "not a legal contract",
        "not_provided",
        "operator_guided",
        "billing implementation",
        "runtime license enforcement",
        "payment processing",
        "customer-controlled",
    ],
    "docs/project/pilot-acceptance-checklist.md": [
        "Package verification",
        "Clean self-hosted install rehearsal",
        "Release evidence",
        "Hosted/operator readiness",
        "Readiness evidence history",
        "Real-repo benchmark",
        "Private-repo pilot evidence",
        "Backup/restore/upgrade",
        "Code Decision Audit",
        "Governance guardrail",
    ],
    "docs/project/pilot-support-renewal-upgrade-boundary.md": [
        "support response boundary",
        "renewal path",
        "upgrade path",
        "not a service-level agreement",
        "managed hosted operations",
        "billing",
        "hosted secret vault",
        "runtime license enforcement",
    ],
}

FORBIDDEN_PATTERNS = [
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}", re.IGNORECASE),
    re.compile(r"ghp_[A-Za-z0-9]{20,}", re.IGNORECASE),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}", re.IGNORECASE),
    re.compile(r"BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY", re.IGNORECASE),
    re.compile(r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b"),
    re.compile(r"\b(?:wire transfer account|bank account number|routing number)\b", re.IGNORECASE),
    re.compile(r"\b(?:signed customer agreement attached|fully executed agreement attached|customer legal name:)", re.IGNORECASE),
    re.compile(r"\b(?:private issue text|private pull request text|raw private source content included)\b", re.IGNORECASE),
]

OPTIONAL_CUSTOMER_LANES = [
    {
        "id": "filled_customer_quote",
        "label": "Filled customer quote",
        "status": STATUS_OPERATOR_GUIDED,
        "reason": "Filled pricing, payment, and customer-specific terms must remain outside the public repository.",
    },
    {
        "id": "signed_customer_agreement",
        "label": "Signed customer agreement",
        "status": STATUS_NOT_PROVIDED,
        "reason": "Signed legal terms are customer-specific and are not committed with template materials.",
    },
    {
        "id": "billing_implementation",
        "label": "Billing implementation",
        "status": STATUS_NOT_PROVIDED,
        "reason": "The proposal kit is template material and does not implement checkout, invoicing, or payment processing.",
    },
]


def _check_required_docs(root: Path) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for doc_id, relative in REQUIRED_DOCS.items():
        path = root / relative
        checks.append(
            {
                "id": f"doc:{doc_id}",
                "label": f"Required proposal material {relative}",
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


def _check_forbidden_material(root: Path) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for relative in REQUIRED_DOCS.values():
        path = root / relative
        text = path.read_text(encoding="utf-8", errors="ignore") if path.is_file() else ""
        matched = any(pattern.search(text) for pattern in FORBIDDEN_PATTERNS)
        checks.append(
            {
                "id": f"forbidden:{relative}",
                "label": f"{relative} contains no obvious secret, payment, signed-contract, or raw private material",
                "status": STATUS_BLOCKING if matched else STATUS_PASS,
                "details": {"path": relative, "matched": matched},
            }
        )
    return checks


def calculate_status(checks: list[dict[str, Any]]) -> str:
    return STATUS_BLOCKING if any(check["status"] == STATUS_BLOCKING for check in checks) else STATUS_PASS


def verify_proposal_kit(root: Path, *, generated_at: str | None = None) -> dict[str, Any]:
    checks = [
        *_check_required_docs(root),
        *_check_required_references(root),
        *_check_forbidden_material(root),
    ]
    status = calculate_status(checks)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at or datetime.now(UTC).isoformat(),
        "evidence_type": "pilot_commercial_proposal_kit_verification",
        "status": status,
        "entrypoint": REQUIRED_DOCS["entry"],
        "materials": {doc_id: relative for doc_id, relative in REQUIRED_DOCS.items()},
        "checks": checks,
        "blockers": [check for check in checks if check["status"] == STATUS_BLOCKING],
        "optional_customer_lanes": OPTIONAL_CUSTOMER_LANES,
        "recommended_next_actions": [
            "Attach proposal kit verification, package verification, release evidence, readiness history, benchmark evidence, private-repo evidence when applicable, and backup/restore/upgrade evidence before paid pilot claims.",
            "Keep filled quotes, payment data, signed agreements, customer contact details, private repository names, tokens, provider keys, and raw source content outside committed artifacts.",
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
        "# Pilot Commercial Proposal Kit Verification",
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
    parser = argparse.ArgumentParser(description="Verify DecisionAtlas pilot commercial proposal kit materials.")
    parser.add_argument("--output-json", type=Path, default=Path(".tmp/pilot-commercial-proposal-kit-verification.json"))
    parser.add_argument("--output-markdown", type=Path, default=Path(".tmp/pilot-commercial-proposal-kit-verification.md"))
    parser.add_argument("--generated-at")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    bundle = verify_proposal_kit(root, generated_at=args.generated_at)
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
