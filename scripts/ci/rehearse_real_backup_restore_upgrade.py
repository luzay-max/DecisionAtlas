from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
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
NON_CLEAN_STATUSES = {STATUS_WARNING, STATUS_BLOCKING, STATUS_OPERATOR_GUIDED, STATUS_NOT_PROVIDED, STATUS_KNOWN_LIMITATION}
BLOCKING_STATUSES = {STATUS_BLOCKING, "failed", "failure", "error"}

SECRET_PATTERNS = [
    ("token_like_value", re.compile(r"(ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|glpat-[A-Za-z0-9_-]+|sk-[A-Za-z0-9_-]+|xox[baprs]-[A-Za-z0-9-]+)", re.IGNORECASE)),
    ("env_secret_assignment", re.compile(r"\b[A-Z0-9_]*(TOKEN|SECRET|PASSWORD|API_KEY|PRIVATE_KEY|DATABASE_URL)[A-Z0-9_]*\s*=\s*[^\s\"']+", re.IGNORECASE)),
    ("credentialed_database_url", re.compile(r"postgres(?:ql)?://[^\\s]+:[^\\s]+@", re.IGNORECASE)),
    ("private_key_marker", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("raw_backup_marker", re.compile(r"(\bPGDMP\b|BEGIN DATABASE DUMP|COPY public\.|CREATE TABLE public\.)", re.IGNORECASE)),
    ("private_repo_snippet_marker", re.compile(r"(raw_private_repository|private_source_snippet|private_repo_snippet|BEGIN PRIVATE REPOSITORY CONTENT)", re.IGNORECASE)),
]

DEFAULT_STATE = {
    "workspace": {"slug": "continuity-smoke", "decision_count": 2},
    "decisions": [
        {"id": "decision-1", "state": "accepted", "title": "Use self-hosted deployment"},
        {"id": "decision-2", "state": "candidate", "title": "Keep backups operator controlled"},
    ],
    "audit_events": [{"action": "continuity_rehearsal_seeded", "actor": "system"}],
}


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip().lower()).strip("-")
    return slug or "real-backup-restore-upgrade-rehearsal"


def _resolve_path(path: str | Path | None, root: Path) -> Path | None:
    if path is None or str(path) == "":
        return None
    candidate = Path(path)
    return candidate if candidate.is_absolute() else root / candidate


def _display_path(path: Path | None, root: Path) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name


def _normalize_status(value: Any, default: str = STATUS_NOT_PROVIDED) -> str:
    if value is None:
        return default
    normalized = str(value).strip().lower().replace(" ", "_").replace("-", "_")
    if normalized in {"passed", "success", "succeeded", "ok", "clean"}:
        return STATUS_PASS
    if normalized in {"warn", "warnings", "caution", "needs_review"}:
        return STATUS_WARNING
    if normalized in {"blocked", "failed", "failure", "error"}:
        return STATUS_BLOCKING
    if normalized in {STATUS_PASS, STATUS_WARNING, STATUS_BLOCKING, STATUS_OPERATOR_GUIDED, STATUS_NOT_PROVIDED, STATUS_KNOWN_LIMITATION}:
        return normalized
    return default


def _json_bytes(data: Any) -> bytes:
    return json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _sha256(data: Any) -> str:
    return hashlib.sha256(_json_bytes(data)).hexdigest()


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return None, f"read_error:{exc}"
    except json.JSONDecodeError as exc:
        return None, f"json_error:{exc}"
    if not isinstance(data, dict):
        return None, "json_not_object"
    return data, None


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _safe_reset_owned_dir(path: Path, owned_root: Path) -> None:
    resolved_path = path.resolve()
    resolved_root = owned_root.resolve()
    if resolved_path == resolved_root or resolved_root not in resolved_path.parents:
        raise ValueError(f"Refusing to reset path outside owned scratch root: {path}")
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def _is_within(path: Path, root: Path) -> bool:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    return resolved_path == resolved_root or resolved_root in resolved_path.parents


def _check_path(label: str, path: Path | None, owned_root: Path, repo_root: Path) -> list[dict[str, Any]]:
    if path is None:
        return []
    return [
        {
            "id": f"path_safety:{label}",
            "label": f"{label} path stays inside owned scratch root",
            "status": STATUS_PASS if _is_within(path, owned_root) else STATUS_BLOCKING,
            "details": {"path": _display_path(path, repo_root), "scratch_root": _display_path(owned_root, repo_root)},
        }
    ]


def _detect_sensitive(payload: Any) -> list[dict[str, Any]]:
    text = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    findings = []
    for finding_id, pattern in SECRET_PATTERNS:
        if pattern.search(text):
            findings.append({"id": finding_id, "status": STATUS_BLOCKING})
    return findings


def _lane(lane_id: str, label: str, status: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"id": lane_id, "label": label, "status": status, "details": details or {}}


def _status_from_lanes(lanes: list[dict[str, Any]], redaction_findings: list[dict[str, Any]]) -> str:
    statuses = {_normalize_status(lane.get("status")) for lane in lanes}
    if redaction_findings or statuses & BLOCKING_STATUSES:
        return STATUS_BLOCKING
    if statuses & NON_CLEAN_STATUSES:
        return STATUS_WARNING
    return STATUS_PASS


def _safe_text(value: Any, limit: int = 500) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if any(pattern.search(text) for _, pattern in SECRET_PATTERNS):
        return "[redacted]"
    return text[: limit - 1].rstrip() + "..." if len(text) > limit else text


def build_rehearsal(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    label = _slugify(args.label)
    scratch_root = _resolve_path(args.scratch_root, root) or root / ".tmp" / "real-backup-restore-upgrade-rehearsal"
    assert scratch_root is not None
    rehearsal_dir = scratch_root / label
    source_dir = rehearsal_dir / "source"
    backup_dir = rehearsal_dir / "backup"
    restore_dir = rehearsal_dir / "restore"
    source_state_path = _resolve_path(args.source_state_json, root) if args.source_state_json else source_dir / "state.json"
    backup_artifact_path = backup_dir / "state-backup.json"
    restored_state_path = restore_dir / "state.json"

    lanes: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    path_checks = [
        *_check_path("rehearsal_dir", rehearsal_dir, scratch_root, root),
        *_check_path("source_state", source_state_path, scratch_root, root),
        *_check_path("backup_artifact", backup_artifact_path, scratch_root, root),
        *_check_path("restore_state", restored_state_path, scratch_root, root),
    ]
    blockers.extend(check for check in path_checks if check["status"] == STATUS_BLOCKING)

    source_state: dict[str, Any] | None = None
    restored_state: dict[str, Any] | None = None
    if not blockers:
        try:
            if args.source_state_json:
                rehearsal_dir.mkdir(parents=True, exist_ok=True)
                source_dir.mkdir(parents=True, exist_ok=True)
                _safe_reset_owned_dir(backup_dir, scratch_root)
                _safe_reset_owned_dir(restore_dir, scratch_root)
            else:
                _safe_reset_owned_dir(rehearsal_dir, scratch_root)
                source_dir.mkdir(parents=True, exist_ok=True)
                backup_dir.mkdir(parents=True, exist_ok=True)
                restore_dir.mkdir(parents=True, exist_ok=True)
            if args.source_state_json:
                source_state_path = _resolve_path(args.source_state_json, root)
                assert source_state_path is not None
                source_state, error = _read_json(source_state_path)
                if error or source_state is None:
                    blockers.append(_lane("source_state", "Source state is readable", STATUS_BLOCKING, {"error": error}))
            else:
                source_state = DEFAULT_STATE
                _write_json(source_state_path, source_state)
            if source_state is not None:
                _write_json(backup_artifact_path, source_state)
                backup_state, backup_error = _read_json(backup_artifact_path)
                if backup_error or backup_state is None:
                    blockers.append(_lane("backup_artifact", "Backup artifact is readable", STATUS_BLOCKING, {"error": backup_error}))
                else:
                    restored_state = dict(backup_state)
                    if args.inject_restore_mismatch:
                        restored_state["restore_mismatch"] = True
                    _write_json(restored_state_path, restored_state)
        except (OSError, ValueError) as exc:
            blockers.append(_lane("scratch_workspace", "Scratch workspace can be prepared", STATUS_BLOCKING, {"error": str(exc)}))

    source_hash = _sha256(source_state) if source_state is not None else None
    restored_hash = _sha256(restored_state) if restored_state is not None else None
    restore_match = source_hash is not None and restored_hash == source_hash
    lanes.extend(
        [
            _lane(
                "scratch_workspace",
                "Scratch workspace",
                STATUS_BLOCKING if blockers else STATUS_PASS,
                {"path": _display_path(rehearsal_dir, root)},
            ),
            _lane(
                "database_backup",
                "Scratch state backup",
                STATUS_PASS if source_state is not None and not blockers else STATUS_BLOCKING,
                {"backup_artifact": _display_path(backup_artifact_path, root), "source_sha256": source_hash},
            ),
            _lane(
                "restore_validation",
                "Scratch restore validation",
                STATUS_PASS if restore_match else STATUS_BLOCKING,
                {"restored_state": _display_path(restored_state_path, root), "restored_sha256": restored_hash, "matches_source": restore_match},
            ),
            _lane(
                "upgrade_transition",
                "Upgrade transition metadata",
                STATUS_PASS if args.previous_version and args.target_version else STATUS_OPERATOR_GUIDED,
                {"previous_version": args.previous_version, "target_version": args.target_version},
            ),
            _lane(
                "post_upgrade_validation",
                "Post-upgrade validation",
                _normalize_status(args.post_upgrade_status, STATUS_OPERATOR_GUIDED),
                {"status_source": "argument"},
            ),
            _lane(
                "rollback_plan",
                "Rollback plan",
                _normalize_status(args.rollback_plan_status, STATUS_OPERATOR_GUIDED),
                {"status_source": "argument"},
            ),
        ]
    )
    lanes.extend(path_checks)

    redaction_payload = {
        "label": label,
        "source_state": source_state,
        "upgrade_notes": args.upgrade_notes,
        "rollback_notes": args.rollback_notes,
    }
    redaction_findings = _detect_sensitive(redaction_payload)
    if redaction_findings:
        lanes.append(_lane("redaction", "Sensitive material scan", STATUS_BLOCKING, {"finding_count": len(redaction_findings)}))
    else:
        lanes.append(_lane("redaction", "Sensitive material scan", STATUS_PASS, {"finding_count": 0}))

    status = _status_from_lanes(lanes, redaction_findings)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": args.generated_at or datetime.now(UTC).isoformat(),
        "label": label,
        "status": status,
        "evidence_type": "real_backup_restore_upgrade_rehearsal",
        "scratch_scope": {
            "scratch_root": _display_path(scratch_root, root),
            "rehearsal_dir": _display_path(rehearsal_dir, root),
            "source_state": _display_path(source_state_path, root),
            "backup_artifact": _display_path(backup_artifact_path, root),
            "restored_state": _display_path(restored_state_path, root),
            "scratch_only": True,
        },
        "continuity_lanes": lanes,
        "integrity": {
            "source_sha256": source_hash,
            "restored_sha256": restored_hash,
            "restore_matches_source": restore_match,
            "source_record_count": len(source_state.get("decisions", [])) if isinstance(source_state, dict) and isinstance(source_state.get("decisions"), list) else None,
            "restored_record_count": len(restored_state.get("decisions", [])) if isinstance(restored_state, dict) and isinstance(restored_state.get("decisions"), list) else None,
        },
        "upgrade": {
            "previous_version": args.previous_version,
            "target_version": args.target_version,
            "post_upgrade_status": _normalize_status(args.post_upgrade_status, STATUS_OPERATOR_GUIDED),
            "upgrade_notes": _safe_text(args.upgrade_notes),
        },
        "rollback": {
            "rollback_plan_status": _normalize_status(args.rollback_plan_status, STATUS_OPERATOR_GUIDED),
            "rollback_notes": _safe_text(args.rollback_notes),
        },
        "redaction_findings": redaction_findings,
        "blockers": [lane for lane in lanes if _normalize_status(lane.get("status")) == STATUS_BLOCKING],
        "limitations": [
            "This rehearsal proves backup/restore mechanics only for explicit scratch state, not production customer data.",
            "Raw database dumps, .env files, provider keys, repository tokens, and private repository content remain outside generated evidence.",
            "Full Web/API/Engine post-upgrade smoke must be attached separately when customer-facing upgrade readiness is claimed.",
        ],
        "recommended_next_actions": _recommended_next_actions(status, restore_match),
    }


def _recommended_next_actions(status: str, restore_match: bool) -> list[str]:
    if status == STATUS_BLOCKING:
        actions = ["Resolve blocking scratch continuity rehearsal lanes before claiming tested backup/restore/upgrade readiness."]
        if not restore_match:
            actions.append("Inspect source and restored state summaries; do not attach raw backup content.")
        return actions
    if status == STATUS_WARNING:
        return [
            "Review operator-guided continuity lanes and attach post-upgrade smoke evidence before customer handoff.",
            "Archive real continuity evidence into readiness history when making durable self-hosted claims.",
        ]
    return ["Attach this real continuity evidence to delivery, handoff, and Code Decision Audit reports."]


def _markdown_cell(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, (dict, list)):
        text = json.dumps(value, sort_keys=True, ensure_ascii=False)
    else:
        text = str(value)
    return text.replace("|", "\\|").replace("\n", "<br>") or "-"


def render_markdown(bundle: dict[str, Any]) -> str:
    scope = bundle.get("scratch_scope") if isinstance(bundle.get("scratch_scope"), dict) else {}
    integrity = bundle.get("integrity") if isinstance(bundle.get("integrity"), dict) else {}
    lines = [
        "# Real Backup Restore Upgrade Rehearsal",
        "",
        f"- Label: `{bundle.get('label')}`",
        f"- Generated at: `{bundle.get('generated_at')}`",
        f"- Status: `{bundle.get('status')}`",
        f"- Scratch only: `{scope.get('scratch_only')}`",
        f"- Rehearsal dir: `{scope.get('rehearsal_dir') or '-'}`",
        "",
        "## Restore Integrity",
        "",
        f"- Source SHA256: `{integrity.get('source_sha256') or '-'}`",
        f"- Restored SHA256: `{integrity.get('restored_sha256') or '-'}`",
        f"- Restore matches source: `{integrity.get('restore_matches_source')}`",
        f"- Source records: `{integrity.get('source_record_count')}`",
        f"- Restored records: `{integrity.get('restored_record_count')}`",
        "",
        "## Continuity Lanes",
        "",
        "| Lane | Status | Details |",
        "| --- | --- | --- |",
    ]
    for lane in bundle.get("continuity_lanes", []):
        if isinstance(lane, dict):
            lines.append(
                f"| {_markdown_cell(lane.get('label'))} | {_markdown_cell(lane.get('status'))} | {_markdown_cell(lane.get('details'))} |"
            )

    lines.extend(["", "## Limitations", ""])
    for item in bundle.get("limitations") or []:
        lines.append(f"- {item}")
    lines.extend(["", "## Recommended Next Actions", ""])
    for item in bundle.get("recommended_next_actions") or []:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def write_outputs(bundle: dict[str, Any], output_json: Path, output_markdown: Path) -> None:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(bundle, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    output_markdown.write_text(render_markdown(bundle), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a real scratch-only DecisionAtlas backup/restore/upgrade rehearsal.")
    parser.add_argument("--label", default="real-backup-restore-upgrade-rehearsal")
    parser.add_argument("--scratch-root", default=".tmp/real-backup-restore-upgrade-rehearsal")
    parser.add_argument("--source-state-json")
    parser.add_argument("--previous-version")
    parser.add_argument("--target-version")
    parser.add_argument("--post-upgrade-status", default=STATUS_OPERATOR_GUIDED)
    parser.add_argument("--rollback-plan-status", default=STATUS_OPERATOR_GUIDED)
    parser.add_argument("--upgrade-notes")
    parser.add_argument("--rollback-notes")
    parser.add_argument("--inject-restore-mismatch", action="store_true")
    parser.add_argument("--generated-at")
    parser.add_argument("--output-json", default=".tmp/real-backup-restore-upgrade-rehearsal.json")
    parser.add_argument("--output-markdown", default=".tmp/real-backup-restore-upgrade-rehearsal.md")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    bundle = build_rehearsal(args, root)
    output_json = _resolve_path(args.output_json, root)
    output_markdown = _resolve_path(args.output_markdown, root)
    assert output_json is not None
    assert output_markdown is not None
    write_outputs(bundle, output_json, output_markdown)
    print(f"Real continuity rehearsal JSON written to {output_json}")
    print(f"Real continuity rehearsal Markdown written to {output_markdown}")
    print(f"Status: {bundle['status']}")
    return 1 if bundle["status"] == STATUS_BLOCKING else 0


if __name__ == "__main__":
    raise SystemExit(main())
