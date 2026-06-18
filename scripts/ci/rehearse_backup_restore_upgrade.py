from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
STATUS_PASS = "pass"
STATUS_WARNING = "warning"
STATUS_BLOCKING = "blocking"
STATUS_OPERATOR_GUIDED = "operator_guided"
STATUS_NOT_PROVIDED = "not_provided"
STATUS_KNOWN_LIMITATION = "known_limitation"

ALLOWED_STATUSES = {
    STATUS_PASS,
    "passed",
    STATUS_WARNING,
    STATUS_BLOCKING,
    STATUS_OPERATOR_GUIDED,
    STATUS_NOT_PROVIDED,
    STATUS_KNOWN_LIMITATION,
}

REQUIRED_TOP_LEVEL_FIELDS = [
    "schema_version",
    "generated_at",
    "status",
    "evidence_type",
    "target",
    "custody",
    "continuity_lanes",
    "limitations",
    "recommended_next_actions",
    "operator_review",
]

REQUIRED_CONTINUITY_LANES = {
    "database_backup",
    "environment_backup",
    "restore_plan",
    "restore_validation",
    "upgrade_plan",
    "post_upgrade_validation",
    "rollback_plan",
    "handoff_evidence",
}

FORBIDDEN_PATTERNS = [
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}", re.IGNORECASE),
    re.compile(r"ghp_[A-Za-z0-9]{20,}", re.IGNORECASE),
    re.compile(r"sk-[A-Za-z0-9]{16,}", re.IGNORECASE),
    re.compile(r"(LLM_API_KEY|OPENAI_API_KEY|GITHUB_TOKEN|EMBEDDING_API_KEY|DATABASE_URL)\s*=\s*\S+", re.IGNORECASE),
    re.compile(r"postgres(?:ql)?://[^\\s]+:[^\\s]+@", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]

REQUIRED_CUSTODY_PHRASES = [
    "database backups",
    ".env",
    "provider keys",
    "repository tokens",
    "operator or customer control",
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


def _load_input(path: Path) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    if not path.is_file():
        return None, [_check(False, check_id="input:file_exists", label="Rehearsal input exists", details={"path": path.as_posix()})]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, [
            _check(
                False,
                check_id="input:valid_json",
                label="Rehearsal input is valid JSON",
                details={"path": path.as_posix(), "error": str(exc)},
            )
        ]
    if not isinstance(data, dict):
        return None, [_check(False, check_id="input:object", label="Rehearsal input is a JSON object")]
    return data, [
        _check(True, check_id="input:file_exists", label="Rehearsal input exists", details={"path": path.as_posix()}),
        _check(True, check_id="input:valid_json", label="Rehearsal input is valid JSON", details={"path": path.as_posix()}),
    ]


def _check_shape(data: dict[str, Any] | None) -> list[dict[str, Any]]:
    if data is None:
        return []
    checks: list[dict[str, Any]] = []
    for field in REQUIRED_TOP_LEVEL_FIELDS:
        checks.append(
            _check(field in data, check_id=f"input:field:{field}", label=f"Input includes {field}", details={"field": field})
        )

    checks.append(
        _check(
            data.get("evidence_type") == "backup_restore_upgrade_rehearsal",
            check_id="input:evidence_type",
            label="Evidence type is backup_restore_upgrade_rehearsal",
        )
    )
    checks.append(
        _check(
            _status(data.get("status")) in ALLOWED_STATUSES,
            check_id="input:status_allowed",
            label="Overall status is recognized",
            details={"status": data.get("status")},
        )
    )

    target = data.get("target") if isinstance(data.get("target"), dict) else {}
    checks.append(
        _check(
            str(target.get("environment") or "").lower() in {"customer_controlled_host", "operator_controlled_host", "local_rehearsal"},
            check_id="target:environment",
            label="Target environment preserves operator/customer control boundary",
            details={"environment": target.get("environment")},
        )
    )

    custody = data.get("custody") if isinstance(data.get("custody"), dict) else {}
    checks.extend(
        [
            _check(
                custody.get("credential_material_included") is False,
                check_id="custody:no_credential_material",
                label="Credential material is not included",
            ),
            _check(
                custody.get("raw_backup_content_included") is False,
                check_id="custody:no_raw_backup_content",
                label="Raw backup content is not included",
            ),
            _check(
                custody.get("database_backup_retained_by_operator") is True,
                check_id="custody:database_backup_retained_by_operator",
                label="Database backup remains operator/customer controlled",
            ),
            _check(
                custody.get("env_backup_retained_by_operator") is True,
                check_id="custody:env_backup_retained_by_operator",
                label=".env backup remains operator/customer controlled",
            ),
        ]
    )
    custody_statement = str(custody.get("custody_statement") or "").lower()
    for phrase in REQUIRED_CUSTODY_PHRASES:
        checks.append(
            _check(
                phrase in custody_statement,
                check_id=f"custody:statement:{phrase}",
                label=f"Custody statement references {phrase}",
            )
        )

    lanes = data.get("continuity_lanes") if isinstance(data.get("continuity_lanes"), list) else []
    lane_ids = {str(lane.get("id")) for lane in lanes if isinstance(lane, dict)}
    for lane_id in sorted(REQUIRED_CONTINUITY_LANES):
        checks.append(
            _check(
                lane_id in lane_ids,
                check_id=f"lane:present:{lane_id}",
                label=f"Continuity lane {lane_id} is present",
            )
        )
    for lane in lanes:
        if not isinstance(lane, dict):
            checks.append(_check(False, check_id="lane:object", label="Continuity lane is an object"))
            continue
        lane_id = str(lane.get("id") or "")
        checks.append(
            _check(
                _status(lane.get("status")) in ALLOWED_STATUSES,
                check_id=f"lane:status:{lane_id}",
                label=f"Continuity lane {lane_id} has recognized status",
                details={"status": lane.get("status")},
            )
        )
        checks.append(
            _check(
                bool(str(lane.get("summary") or "").strip()),
                check_id=f"lane:summary:{lane_id}",
                label=f"Continuity lane {lane_id} includes summary",
            )
        )

    operator_review = data.get("operator_review") if isinstance(data.get("operator_review"), dict) else {}
    checks.extend(
        [
            _check(
                operator_review.get("review_required_before_sharing") is True,
                check_id="operator_review:required",
                label="Operator review is required before sharing",
            ),
            _check(
                "credential" in str(operator_review.get("review_statement") or "").lower()
                or "secret" in str(operator_review.get("review_statement") or "").lower(),
                check_id="operator_review:statement",
                label="Operator review statement references credential or secret safety",
            ),
        ]
    )

    forbidden = _contains_forbidden_material(_json_text(data))
    checks.append(
        _check(
            not forbidden,
            check_id="input:forbidden_material",
            label="Input contains no obvious token, secret, database URL, or private key material",
            details={"matched_patterns": forbidden},
        )
    )
    return checks


def _calculate_status(data: dict[str, Any] | None, checks: list[dict[str, Any]]) -> str:
    if any(check["status"] == STATUS_BLOCKING for check in checks):
        return STATUS_BLOCKING
    lanes = data.get("continuity_lanes") if isinstance(data, dict) and isinstance(data.get("continuity_lanes"), list) else []
    lane_statuses = {_status(lane.get("status")) for lane in lanes if isinstance(lane, dict)}
    if STATUS_BLOCKING in lane_statuses:
        return STATUS_BLOCKING
    source_status = _status(data.get("status") if data else None)
    if source_status == "passed":
        source_status = STATUS_PASS
    if source_status in ALLOWED_STATUSES:
        return source_status
    if lane_statuses & {STATUS_OPERATOR_GUIDED, STATUS_NOT_PROVIDED, STATUS_KNOWN_LIMITATION, STATUS_WARNING}:
        return STATUS_WARNING
    return STATUS_OPERATOR_GUIDED


def rehearse_backup_restore_upgrade(
    *,
    input_json: Path,
    generated_at: str | None = None,
) -> dict[str, Any]:
    data, load_checks = _load_input(input_json)
    checks = [*load_checks, *_check_shape(data)]
    status = _calculate_status(data, checks)
    lanes = data.get("continuity_lanes") if isinstance(data, dict) and isinstance(data.get("continuity_lanes"), list) else []
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at or datetime.now(UTC).isoformat(),
        "status": status,
        "evidence_type": "backup_restore_upgrade_rehearsal_verification",
        "source_evidence": {
            "input_json": input_json.as_posix(),
            "source_status": data.get("status") if data else None,
        },
        "continuity_summary": {
            "required_lanes": sorted(REQUIRED_CONTINUITY_LANES),
            "provided_lanes": [lane.get("id") for lane in lanes if isinstance(lane, dict)],
            "lane_status_counts": _lane_status_counts(lanes),
        },
        "checks": checks,
        "blockers": [check for check in checks if check["status"] == STATUS_BLOCKING],
        "handoff_summary": {
            "continuity_status": status,
            "advisory_only": True,
            "custody_note": "Database backups, .env files, provider keys, repository tokens, and customer-specific artifacts must remain under operator or customer control.",
            "real_restore_note": "This verifier is non-destructive. It does not prove a real restore or upgrade unless operator-supplied evidence references are attached.",
            "recommended_next_actions": data.get("recommended_next_actions") if data else [
                "Provide a valid backup/restore/upgrade rehearsal input JSON."
            ],
        },
    }


def _lane_status_counts(lanes: list[Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for lane in lanes:
        if not isinstance(lane, dict):
            continue
        status = _status(lane.get("status")) or "unknown"
        counts[status] = counts.get(status, 0) + 1
    return counts


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
        "# Backup Restore Upgrade Rehearsal",
        "",
        f"- Generated at: `{bundle.get('generated_at')}`",
        f"- Status: `{bundle.get('status')}`",
        f"- Source input: `{(bundle.get('source_evidence') or {}).get('input_json')}`",
        "",
        "This report is non-destructive. It does not run database backup, restore, migration, upgrade, or rollback commands. It verifies whether operator-supplied continuity evidence is bounded and safe to hand off.",
        "",
        "## Continuity Summary",
        "",
        f"- Required lanes: `{', '.join((bundle.get('continuity_summary') or {}).get('required_lanes') or [])}`",
        f"- Provided lanes: `{', '.join(str(item) for item in ((bundle.get('continuity_summary') or {}).get('provided_lanes') or []))}`",
        f"- Lane status counts: `{json.dumps((bundle.get('continuity_summary') or {}).get('lane_status_counts') or {}, sort_keys=True)}`",
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

    summary = bundle.get("handoff_summary") if isinstance(bundle.get("handoff_summary"), dict) else {}
    lines.extend(
        [
            "",
            "## Handoff Summary",
            "",
            f"- Continuity status: `{summary.get('continuity_status')}`",
            f"- Advisory only: `{summary.get('advisory_only')}`",
            f"- Custody note: {summary.get('custody_note')}",
            f"- Real restore note: {summary.get('real_restore_note')}",
            "",
            "## Recommended Next Actions",
            "",
        ]
    )
    for action in summary.get("recommended_next_actions") or []:
        lines.append(f"- {action}")
    lines.append("")
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate non-destructive backup/restore/upgrade rehearsal evidence.")
    parser.add_argument("--input-json", type=Path, default=Path("templates/backup-restore-upgrade-rehearsal.example.json"))
    parser.add_argument("--output-json", type=Path, default=Path(".tmp/backup-restore-upgrade-rehearsal.json"))
    parser.add_argument("--output-markdown", type=Path, default=Path(".tmp/backup-restore-upgrade-rehearsal.md"))
    parser.add_argument("--generated-at")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    input_json = args.input_json if args.input_json.is_absolute() else root / args.input_json
    output_json = args.output_json if args.output_json.is_absolute() else root / args.output_json
    output_markdown = args.output_markdown if args.output_markdown.is_absolute() else root / args.output_markdown

    bundle = rehearse_backup_restore_upgrade(input_json=input_json, generated_at=args.generated_at)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(bundle, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    output_markdown.write_text(render_markdown(bundle), encoding="utf-8")
    print(json.dumps(bundle, indent=2, sort_keys=True, ensure_ascii=False))
    return 1 if bundle["status"] == STATUS_BLOCKING else 0


if __name__ == "__main__":
    raise SystemExit(main())
