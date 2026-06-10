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
ALLOWED_SOURCE_STATUSES = {"pass", "passed", "warning", "blocking", "operator_guided", "not_provided", "known_limitation"}
NON_BLOCKING_SOURCE_STATUSES = {"pass", "passed", "operator_guided", "not_provided", "warning", "known_limitation"}

REQUIRED_TOP_LEVEL_FIELDS = [
    "schema_version",
    "generated_at",
    "status",
    "evidence_type",
    "repository",
    "credential_custody",
    "redaction",
    "workflow_lanes",
    "metrics",
    "limitations",
    "recommended_next_actions",
    "operator_review",
]

REQUIRED_WORKFLOW_LANES = {
    "token_setup",
    "access_validation",
    "import_run",
    "decision_review",
    "why_search",
    "drift_review",
    "handoff_evidence",
}

REQUIRED_MARKDOWN_PHRASES = [
    "not proof that a real private repository has been evaluated",
    "Repository tokens and provider keys remain on the customer-controlled host",
    "raw private source content",
    "raw private issue or pull-request text",
    "token values",
    "customer identifiers",
    "human operator must confirm redaction",
]

FORBIDDEN_PATTERNS = [
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}", re.IGNORECASE),
    re.compile(r"ghp_[A-Za-z0-9]{20,}", re.IGNORECASE),
    re.compile(r"sk-[A-Za-z0-9]{16,}", re.IGNORECASE),
    re.compile(r"(LLM_API_KEY|OPENAI_API_KEY|GITHUB_TOKEN|EMBEDDING_API_KEY)\s*=\s*\S+", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]


def _status(value: Any) -> str:
    return str(value or "").strip().lower()


def _json_text(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True)


def _contains_forbidden_material(text: str) -> list[str]:
    violations: list[str] = []
    for pattern in FORBIDDEN_PATTERNS:
        if pattern.search(text):
            violations.append(pattern.pattern)
    return violations


def _check(condition: bool, *, check_id: str, label: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "id": check_id,
        "label": label,
        "status": STATUS_PASS if condition else STATUS_BLOCKING,
        "details": details or {},
    }


def _load_json(path: Path) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    if not path.is_file():
        return None, [
            _check(False, check_id="json:file_exists", label="Evidence JSON exists", details={"path": path.as_posix()})
        ]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, [
            _check(
                False,
                check_id="json:valid",
                label="Evidence JSON is valid",
                details={"path": path.as_posix(), "error": str(exc)},
            )
        ]
    if not isinstance(data, dict):
        return None, [_check(False, check_id="json:object", label="Evidence JSON is an object")]
    return data, [
        _check(True, check_id="json:file_exists", label="Evidence JSON exists", details={"path": path.as_posix()}),
        _check(True, check_id="json:valid", label="Evidence JSON is valid", details={"path": path.as_posix()}),
    ]


def _load_markdown(path: Path) -> tuple[str, list[dict[str, Any]]]:
    if not path.is_file():
        return "", [
            _check(False, check_id="markdown:file_exists", label="Evidence Markdown exists", details={"path": path.as_posix()})
        ]
    text = path.read_text(encoding="utf-8", errors="ignore")
    return text, [
        _check(True, check_id="markdown:file_exists", label="Evidence Markdown exists", details={"path": path.as_posix()})
    ]


def _check_json_shape(data: dict[str, Any] | None) -> list[dict[str, Any]]:
    if data is None:
        return []
    checks: list[dict[str, Any]] = []
    for field in REQUIRED_TOP_LEVEL_FIELDS:
        checks.append(
            _check(field in data, check_id=f"json:field:{field}", label=f"JSON includes {field}", details={"field": field})
        )

    checks.append(
        _check(
            data.get("evidence_type") == "private_repo_pilot_evidence",
            check_id="json:evidence_type",
            label="Evidence type is private_repo_pilot_evidence",
        )
    )
    checks.append(
        _check(
            _status(data.get("status")) in ALLOWED_SOURCE_STATUSES,
            check_id="json:status_allowed",
            label="Overall status is recognized",
            details={"status": data.get("status")},
        )
    )

    repository = data.get("repository") if isinstance(data.get("repository"), dict) else {}
    checks.append(
        _check(
            repository.get("visibility") == "private",
            check_id="json:repository_visibility_private",
            label="Repository visibility is private",
        )
    )
    checks.append(
        _check(
            str(repository.get("identity_status") or "").lower() in {"redacted", "category_only", "customer_controlled"},
            check_id="json:repository_identity_redacted",
            label="Repository identity is redacted or category-only",
            details={"identity_status": repository.get("identity_status")},
        )
    )

    custody = data.get("credential_custody") if isinstance(data.get("credential_custody"), dict) else {}
    checks.extend(
        [
            _check(custody.get("token_material_retained") is False, check_id="json:no_token_retained", label="Token material is not retained"),
            _check(custody.get("token_echoed_to_output") is False, check_id="json:no_token_echoed", label="Token material is not echoed"),
            _check(custody.get("provider_key_retained") is False, check_id="json:no_provider_key_retained", label="Provider key is not retained"),
            _check(
                "customer-controlled host" in str(custody.get("custody_statement") or "").lower()
                or "customer controlled host" in str(custody.get("custody_statement") or "").lower(),
                check_id="json:custody_statement",
                label="Credential custody statement is present",
            ),
        ]
    )

    redaction = data.get("redaction") if isinstance(data.get("redaction"), dict) else {}
    for field in (
        "raw_source_content_included",
        "raw_issue_or_pr_text_included",
        "raw_model_output_included",
        "customer_identifiers_included",
        "local_paths_included",
    ):
        checks.append(
            _check(redaction.get(field) is False, check_id=f"json:redaction:{field}", label=f"Redaction excludes {field}")
        )
    checks.append(
        _check(
            "redacted" in str(redaction.get("redaction_statement") or "").lower(),
            check_id="json:redaction_statement",
            label="Redaction statement is present",
        )
    )

    lanes = data.get("workflow_lanes") if isinstance(data.get("workflow_lanes"), list) else []
    lane_ids = {str(lane.get("id")) for lane in lanes if isinstance(lane, dict)}
    for lane_id in sorted(REQUIRED_WORKFLOW_LANES):
        checks.append(
            _check(
                lane_id in lane_ids,
                check_id=f"json:workflow_lane:{lane_id}",
                label=f"Workflow lane {lane_id} is present",
            )
        )
    for lane in lanes:
        if not isinstance(lane, dict):
            continue
        checks.append(
            _check(
                _status(lane.get("status")) in ALLOWED_SOURCE_STATUSES,
                check_id=f"json:workflow_lane_status:{lane.get('id')}",
                label=f"Workflow lane {lane.get('id')} has recognized status",
                details={"status": lane.get("status")},
            )
        )

    operator_review = data.get("operator_review") if isinstance(data.get("operator_review"), dict) else {}
    checks.extend(
        [
            _check(
                operator_review.get("review_required_before_sharing") is True,
                check_id="json:operator_review_required",
                label="Operator review is required before sharing",
            ),
            _check(
                "redaction" in str(operator_review.get("review_statement") or "").lower(),
                check_id="json:operator_review_statement",
                label="Operator review statement references redaction",
            ),
        ]
    )

    forbidden = _contains_forbidden_material(_json_text(data))
    checks.append(
        _check(
            not forbidden,
            check_id="json:forbidden_material",
            label="JSON contains no obvious token or secret material",
            details={"matched_patterns": forbidden},
        )
    )
    return checks


def _check_markdown(text: str) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    lowered = text.lower()
    for phrase in REQUIRED_MARKDOWN_PHRASES:
        checks.append(
            _check(
                phrase.lower() in lowered,
                check_id=f"markdown:phrase:{phrase[:32]}",
                label=f"Markdown includes required statement: {phrase}",
            )
        )
    forbidden = _contains_forbidden_material(text)
    checks.append(
        _check(
            not forbidden,
            check_id="markdown:forbidden_material",
            label="Markdown contains no obvious token or secret material",
            details={"matched_patterns": forbidden},
        )
    )
    return checks


def _result_status(checks: list[dict[str, Any]], source_status: str | None) -> str:
    if any(check["status"] == STATUS_BLOCKING for check in checks):
        return STATUS_BLOCKING
    normalized = _status(source_status)
    if normalized == "passed":
        return STATUS_PASS
    if normalized in NON_BLOCKING_SOURCE_STATUSES:
        return normalized
    return STATUS_OPERATOR_GUIDED


def verify_private_repo_pilot_evidence(
    *,
    evidence_json: Path,
    evidence_markdown: Path,
    generated_at: str | None = None,
) -> dict[str, Any]:
    data, json_checks = _load_json(evidence_json)
    markdown_text, markdown_checks = _load_markdown(evidence_markdown)
    checks = [
        *json_checks,
        *_check_json_shape(data),
        *markdown_checks,
        *_check_markdown(markdown_text),
    ]
    status = _result_status(checks, data.get("status") if data else None)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at or datetime.now(UTC).isoformat(),
        "status": status,
        "evidence_type": "private_repo_pilot_evidence_verification",
        "source_evidence": {
            "json": evidence_json.as_posix(),
            "markdown": evidence_markdown.as_posix(),
            "source_status": data.get("status") if data else None,
        },
        "checks": checks,
        "blockers": [check for check in checks if check["status"] == STATUS_BLOCKING],
        "handoff_summary": {
            "private_repo_proof_status": status,
            "advisory_only": True,
            "sensitive_material_note": "Verifier checks bounded evidence shape and obvious token patterns, but human review is still required before sharing.",
            "recommended_next_actions": [
                "Generate real private-repo evidence only in the customer-controlled environment.",
                "Preserve operator_guided/not_provided states when real proof is absent.",
                "Do not attach raw private repository content, token material, provider keys, or customer identifiers.",
            ],
        },
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
        "# Private Repo Pilot Evidence Verification",
        "",
        f"- Generated at: `{bundle.get('generated_at')}`",
        f"- Status: `{bundle.get('status')}`",
        f"- Source JSON: `{(bundle.get('source_evidence') or {}).get('json')}`",
        f"- Source Markdown: `{(bundle.get('source_evidence') or {}).get('markdown')}`",
        "",
        "## Checks",
        "",
        "| Check | Status | Details |",
        "| --- | --- | --- |",
    ]
    for check in bundle.get("checks", []):
        lines.append(
            "| "
            + " | ".join(_markdown_cell(value) for value in (check.get("label"), check.get("status"), check.get("details")))
            + " |"
        )

    lines.extend(["", "## Handoff Summary", ""])
    summary = bundle.get("handoff_summary") if isinstance(bundle.get("handoff_summary"), dict) else {}
    lines.append(f"- Private repo proof status: `{summary.get('private_repo_proof_status')}`")
    lines.append(f"- Advisory only: `{summary.get('advisory_only')}`")
    lines.append(f"- Sensitive material note: {summary.get('sensitive_material_note')}")
    lines.extend(["", "## Recommended Next Actions", ""])
    for action in summary.get("recommended_next_actions") or []:
        lines.append(f"- {action}")
    lines.append("")
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify sanitized private-repo pilot evidence.")
    parser.add_argument("--evidence-json", type=Path, default=Path("templates/private-repo-pilot-evidence.example.json"))
    parser.add_argument("--evidence-markdown", type=Path, default=Path("docs/project/private-repo-pilot-evidence-example.md"))
    parser.add_argument("--output-json", type=Path, default=Path(".tmp/private-repo-pilot-evidence-verification.json"))
    parser.add_argument("--output-markdown", type=Path, default=Path(".tmp/private-repo-pilot-evidence-verification.md"))
    parser.add_argument("--generated-at")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    evidence_json = args.evidence_json if args.evidence_json.is_absolute() else root / args.evidence_json
    evidence_markdown = args.evidence_markdown if args.evidence_markdown.is_absolute() else root / args.evidence_markdown
    output_json = args.output_json if args.output_json.is_absolute() else root / args.output_json
    output_markdown = args.output_markdown if args.output_markdown.is_absolute() else root / args.output_markdown

    bundle = verify_private_repo_pilot_evidence(
        evidence_json=evidence_json,
        evidence_markdown=evidence_markdown,
        generated_at=args.generated_at,
    )
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(bundle, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    output_markdown.write_text(render_markdown(bundle), encoding="utf-8")
    print(json.dumps(bundle, indent=2, sort_keys=True, ensure_ascii=False))
    return 1 if bundle["status"] == STATUS_BLOCKING else 0


if __name__ == "__main__":
    raise SystemExit(main())
