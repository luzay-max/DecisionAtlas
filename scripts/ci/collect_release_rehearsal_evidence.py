from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
from pathlib import Path
import shutil
import sys
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import collect_multi_repo_live_diagnosis as multi_repo


SCHEMA_VERSION = 1
STATUS_PASS = "pass"
STATUS_WARNING = "warning"
STATUS_BLOCKING = "blocking"
STATUS_NOT_PROVIDED = "not_provided"
STATUS_OPERATOR_GUIDED = "operator_guided"
STATUS_UNKNOWN = "unknown"

PASS_STATUSES = {"pass", "passed", "ok", "success", "succeeded", "clean", "continue", "ready", "true"}
WARNING_STATUSES = {
    "warning",
    "warn",
    "caution",
    "non_blocking",
    "known_limitation",
    "missing",
    "not_provided",
    "operator_guided",
    "pause",
    "unknown",
}
BLOCKING_STATUSES = {"blocking", "blocked", "failed", "failure", "error", "false", "provider_failure", "local_stack_failure"}

DEFAULT_EVIDENCE_PATHS = {
    "release_evidence": ".tmp/release-evidence.json",
    "hosted_readiness": ".tmp/hosted-operator-readiness.json",
    "benchmark_trend": ".tmp/real-repo-benchmark-trend.json",
    "benchmark_comparison": ".tmp/real-repo-benchmark-comparison.json",
    "multi_repo_diagnosis": ".tmp/multi-repo-live-diagnosis.json",
    "guardrail_summary": ".tmp/agent-guardrail.json",
    "readiness_history": "docs/evidence/readiness/index.json",
}


def normalize_status(value: Any, default: str = STATUS_UNKNOWN) -> str:
    if isinstance(value, bool):
        return STATUS_PASS if value else STATUS_BLOCKING
    if value is None:
        return default
    normalized = str(value).strip().lower().replace(" ", "_").replace("-", "_")
    if normalized in PASS_STATUSES:
        return STATUS_PASS
    if normalized in BLOCKING_STATUSES:
        return STATUS_BLOCKING
    if normalized in WARNING_STATUSES:
        if normalized == "operator_guided":
            return STATUS_OPERATOR_GUIDED
        if normalized == "not_provided":
            return STATUS_NOT_PROVIDED
        return STATUS_WARNING
    return normalized or default


def status_rank(status: str) -> int:
    normalized = normalize_status(status, STATUS_UNKNOWN)
    if normalized == STATUS_BLOCKING:
        return 2
    if normalized == STATUS_PASS:
        return 0
    return 1


def combined_status(statuses: list[str]) -> str:
    ranks = [status_rank(status) for status in statuses]
    if any(rank >= 2 for rank in ranks):
        return STATUS_BLOCKING
    if any(rank == 1 for rank in ranks):
        return STATUS_WARNING
    return STATUS_PASS


def _resolve_path(path: str | Path | None, root: Path) -> Path | None:
    if path is None:
        return None
    candidate = Path(path)
    return candidate if candidate.is_absolute() else root / candidate


def _display_path(path: Path | None, root: Path) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return None, f"Failed to read {path}: {exc}"
    except json.JSONDecodeError as exc:
        return None, f"Failed to parse JSON from {path}: {exc}"
    if not isinstance(data, dict):
        return None, f"Expected JSON object in {path}."
    return data, None


def _bounded(value: Any, limit: int = 500) -> Any:
    if isinstance(value, dict):
        return {str(key): _bounded(item, limit=limit) for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))}
    if isinstance(value, list):
        return [_bounded(item, limit=limit) for item in value[:20]]
    if isinstance(value, str):
        return value if len(value) <= limit else value[: limit - 1].rstrip() + "..."
    return value


def _summary_status(data: dict[str, Any] | None) -> str:
    if data is None:
        return STATUS_NOT_PROVIDED
    for key in ("status", "overall_status", "public_walkthrough_status", "agent_status", "result", "outcome"):
        if key in data:
            return normalize_status(data.get(key), STATUS_UNKNOWN)
    summary = data.get("summary")
    if isinstance(summary, dict) and "status" in summary:
        return normalize_status(summary.get("status"), STATUS_UNKNOWN)
    return STATUS_UNKNOWN


def _benchmark_status_from_summary(data: dict[str, Any], summary: dict[str, Any]) -> str:
    explicit_status = normalize_status(data.get("status") or data.get("overall_status"), "")
    if explicit_status:
        return explicit_status
    regressed = int(summary.get("regressed") or 0)
    operationally_blocked = int(summary.get("operationally_blocked") or 0)
    release_ready = summary.get("release_evidence_ready")
    if operationally_blocked:
        return STATUS_BLOCKING
    if regressed:
        return STATUS_WARNING
    if release_ready is True:
        return STATUS_PASS
    return STATUS_UNKNOWN


def summarize_lane(lane_id: str, data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"status": STATUS_NOT_PROVIDED}
    if lane_id == "release_evidence":
        return {
            "status": normalize_status(data.get("overall_status"), STATUS_UNKNOWN),
            "required_gate_count": len(data.get("required_gates") if isinstance(data.get("required_gates"), list) else []),
            "advisory_signal_count": len(data.get("advisory_signals") if isinstance(data.get("advisory_signals"), list) else []),
            "missing_input_count": len(data.get("missing_inputs") if isinstance(data.get("missing_inputs"), list) else []),
            "warning_count": len(data.get("warnings") if isinstance(data.get("warnings"), list) else []),
        }
    if lane_id == "hosted_readiness":
        lanes = data.get("lanes") if isinstance(data.get("lanes"), list) else []
        return {
            "status": normalize_status(data.get("overall_status") or data.get("public_walkthrough_status"), STATUS_UNKNOWN),
            "public_walkthrough_status": normalize_status(data.get("public_walkthrough_status"), STATUS_NOT_PROVIDED),
            "operator_guided_count": sum(1 for lane in lanes if isinstance(lane, dict) and normalize_status(lane.get("status")) == STATUS_OPERATOR_GUIDED),
            "not_provided_count": sum(1 for lane in lanes if isinstance(lane, dict) and normalize_status(lane.get("status")) == STATUS_NOT_PROVIDED),
        }
    if lane_id in {"benchmark_trend", "benchmark_comparison"}:
        summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
        return {
            "status": _benchmark_status_from_summary(data, summary),
            "repositories": summary.get("repositories") or summary.get("pool_repositories"),
            "covered_repositories": summary.get("covered_repositories"),
            "regressed": int(summary.get("regressed") or 0),
            "operationally_blocked": int(summary.get("operationally_blocked") or 0),
            "release_evidence_ready": summary.get("release_evidence_ready"),
            "recommended_follow_up": _bounded(data.get("recommended_follow_up") or []),
        }
    if lane_id == "multi_repo_diagnosis":
        summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
        return {
            "status": normalize_status(data.get("status"), STATUS_UNKNOWN),
            "selected_repo_ids": data.get("selected_repo_ids") or [],
            "selected_repositories": summary.get("selected_repositories"),
            "pass": summary.get("pass"),
            "warning": summary.get("warning"),
            "blocking": summary.get("blocking"),
            "action_categories": _bounded(summary.get("action_categories") if isinstance(summary.get("action_categories"), dict) else {}),
            "recommended_follow_up": _bounded(data.get("recommended_follow_up") or []),
        }
    if lane_id == "guardrail_summary":
        return {
            "status": normalize_status(data.get("agent_status"), STATUS_UNKNOWN),
            "summary": _bounded(data.get("summary")),
            "handoff_summary": _bounded(data.get("handoff_summary")),
        }
    if lane_id == "readiness_history":
        entries = data.get("entries") if isinstance(data.get("entries"), list) else []
        latest = entries[-1] if entries and isinstance(entries[-1], dict) else {}
        return {
            "status": normalize_status(latest.get("status"), STATUS_NOT_PROVIDED),
            "entry_count": len(entries),
            "latest_entry_id": latest.get("entry_id"),
        }
    return {"status": _summary_status(data), "summary": _bounded(data.get("summary") if isinstance(data, dict) else None)}


def build_lane_from_path(
    *,
    lane_id: str,
    label: str,
    path: Path | None,
    root: Path,
    required: bool = False,
) -> tuple[dict[str, Any], list[str]]:
    lane = {
        "id": lane_id,
        "label": label,
        "required": required,
        "status": STATUS_NOT_PROVIDED,
        "source_path": _display_path(path, root),
        "summary": {},
        "warnings": [],
    }
    warnings: list[str] = []
    if path is None:
        lane["warnings"] = ["source_not_provided"]
        lane["summary"] = {"reason": "source_not_provided"}
        return lane, warnings
    if not path.exists():
        lane["status"] = STATUS_BLOCKING if required else STATUS_NOT_PROVIDED
        warning = f"{lane_id}: source path does not exist: {_display_path(path, root)}"
        lane["warnings"] = [warning]
        lane["summary"] = {"reason": "source_missing"}
        return lane, [warning] if required else []
    data, error = _read_json(path)
    if error:
        lane["status"] = STATUS_BLOCKING if required else STATUS_WARNING
        lane["warnings"] = [error]
        lane["summary"] = {"reason": "source_unreadable", "error": error}
        return lane, [error]
    summary = summarize_lane(lane_id, data)
    lane["status"] = normalize_status(summary.get("status"), STATUS_UNKNOWN)
    lane["summary"] = summary
    return lane, warnings


def _default_path(root: Path, lane_id: str, explicit: str | None, no_default_discovery: bool) -> Path | None:
    if explicit:
        return _resolve_path(explicit, root)
    if no_default_discovery:
        return None
    default = DEFAULT_EVIDENCE_PATHS.get(lane_id)
    return _resolve_path(default, root) if default else None


def run_multi_repo_diagnosis(args: argparse.Namespace, root: Path) -> tuple[Path, Path, dict[str, Any]]:
    output_json = _resolve_path(args.multi_repo_output_json, root)
    output_markdown = _resolve_path(args.multi_repo_output_markdown, root)
    assert output_json is not None
    assert output_markdown is not None
    report = multi_repo.build_report(
        root=root,
        pool_path=_resolve_path(args.multi_repo_pool, root) or (root / multi_repo.DEFAULT_POOL),
        base_url=args.base_url,
        repo_ids=args.repo_id,
        random_count=args.random_count,
        random_seed=args.random_seed,
        session_token=args.session_token,
        wait_import=args.wait_import,
        timeout_seconds=args.timeout_seconds,
        poll_seconds=args.poll_seconds,
        guardrail_json=_resolve_path(args.guardrail_report, root),
        run_guardrail=args.run_guardrail,
        why_question=args.why_question,
        evaluate_drift=args.evaluate_drift,
        generated_at=args.generated_at,
    )
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_markdown.write_text(multi_repo.render_markdown(report), encoding="utf-8")
    return output_json, output_markdown, report


def build_report(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    generated_paths: dict[str, str] = {}
    live_warnings: list[str] = []
    multi_repo_path = _default_path(root, "multi_repo_diagnosis", args.multi_repo_diagnosis_report, args.no_default_discovery)
    if args.run_multi_repo_diagnosis:
        try:
            output_json, output_markdown, _ = run_multi_repo_diagnosis(args, root)
            multi_repo_path = output_json
            generated_paths["multi_repo_diagnosis_json"] = _display_path(output_json, root) or str(output_json)
            generated_paths["multi_repo_diagnosis_markdown"] = _display_path(output_markdown, root) or str(output_markdown)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            live_warnings.append(f"multi_repo_diagnosis: {exc}")

    lane_specs = [
        ("release_evidence", "Release evidence", _default_path(root, "release_evidence", args.release_evidence_report, args.no_default_discovery), False),
        ("hosted_readiness", "Hosted/operator readiness", _default_path(root, "hosted_readiness", args.hosted_readiness_report, args.no_default_discovery), False),
        ("benchmark_trend", "Benchmark trend", _default_path(root, "benchmark_trend", args.benchmark_trend_report, args.no_default_discovery), False),
        ("benchmark_comparison", "Benchmark comparison", _default_path(root, "benchmark_comparison", args.benchmark_comparison_report, args.no_default_discovery), False),
        ("multi_repo_diagnosis", "Multi-repo live diagnosis", multi_repo_path, False),
        ("guardrail_summary", "Governance guardrail", _default_path(root, "guardrail_summary", args.guardrail_report, args.no_default_discovery), False),
        ("readiness_history", "Readiness history", _default_path(root, "readiness_history", args.readiness_history_report, args.no_default_discovery), False),
    ]
    lanes: list[dict[str, Any]] = []
    warnings = list(live_warnings)
    recommended_follow_up: list[str] = []
    for lane_id, label, path, required in lane_specs:
        lane, lane_warnings = build_lane_from_path(lane_id=lane_id, label=label, path=path, root=root, required=required)
        lanes.append(lane)
        warnings.extend(lane_warnings)
        follow_up = lane.get("summary", {}).get("recommended_follow_up")
        if isinstance(follow_up, list):
            recommended_follow_up.extend(str(item) for item in follow_up if item)

    status = combined_status([str(lane.get("status") or STATUS_UNKNOWN) for lane in lanes] + ([STATUS_WARNING] if warnings else []))
    missing_lanes = [lane["id"] for lane in lanes if normalize_status(lane.get("status")) == STATUS_NOT_PROVIDED]
    operator_guided_lanes = [lane["id"] for lane in lanes if normalize_status(lane.get("status")) == STATUS_OPERATOR_GUIDED]
    summary = {
        "lanes": len(lanes),
        "pass": sum(1 for lane in lanes if status_rank(str(lane.get("status"))) == 0),
        "warning": sum(1 for lane in lanes if status_rank(str(lane.get("status"))) == 1),
        "blocking": sum(1 for lane in lanes if status_rank(str(lane.get("status"))) >= 2),
        "missing_lanes": len(missing_lanes),
        "operator_guided_lanes": len(operator_guided_lanes),
    }
    if missing_lanes:
        recommended_follow_up.append("Attach or generate missing optional release evidence lanes before claiming a clean release.")
    if operator_guided_lanes:
        recommended_follow_up.append("Complete or explicitly disclose operator-guided release rehearsal lanes.")
    if status != STATUS_PASS:
        recommended_follow_up.append("Review warning/blocking lanes and decide whether to rerun collectors or disclose limitations.")

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": args.generated_at or datetime.now(UTC).isoformat(),
        "evidence_type": "release-rehearsal-one-command-evidence",
        "label": args.label,
        "status": status,
        "summary": summary,
        "lanes": lanes,
        "missing_lanes": missing_lanes,
        "operator_guided_lanes": operator_guided_lanes,
        "warnings": warnings,
        "generated_paths": generated_paths,
        "recommended_follow_up": sorted(dict.fromkeys(recommended_follow_up)),
        "sensitive_material_note": "This bundle stores compact statuses/counts only. Do not include tokens, raw private source, raw model output, or unbounded local logs.",
    }


def _markdown_cell(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value).replace("|", "\\|").replace("\n", "<br>") or "-"


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    lines = [
        "# Release Rehearsal Evidence Bundle",
        "",
        f"- Label: `{report.get('label')}`",
        f"- Generated at: `{report.get('generated_at')}`",
        f"- Status: `{report.get('status')}`",
        f"- Pass lanes: `{summary.get('pass', 0)}`",
        f"- Warning lanes: `{summary.get('warning', 0)}`",
        f"- Blocking lanes: `{summary.get('blocking', 0)}`",
        f"- Missing lanes: `{summary.get('missing_lanes', 0)}`",
        f"- Operator-guided lanes: `{summary.get('operator_guided_lanes', 0)}`",
        "",
        "## Evidence Lanes",
        "",
        "| Lane | Status | Source | Summary |",
        "| --- | --- | --- | --- |",
    ]
    for lane in report.get("lanes") or []:
        lines.append(
            "| "
            + " | ".join(
                [
                    _markdown_cell(lane.get("label")),
                    _markdown_cell(lane.get("status")),
                    _markdown_cell(lane.get("source_path")),
                    _markdown_cell(lane.get("summary")),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Missing Lanes", ""])
    for lane_id in report.get("missing_lanes") or []:
        lines.append(f"- `{lane_id}`")
    if not report.get("missing_lanes"):
        lines.append("- None")
    lines.extend(["", "## Operator-Guided Lanes", ""])
    for lane_id in report.get("operator_guided_lanes") or []:
        lines.append(f"- `{lane_id}`")
    if not report.get("operator_guided_lanes"):
        lines.append("- None")
    lines.extend(["", "## Recommended Follow-up", ""])
    for action in report.get("recommended_follow_up") or []:
        lines.append(f"- {action}")
    if not report.get("recommended_follow_up"):
        lines.append("- None")
    lines.extend(["", "## Warnings", ""])
    for warning in report.get("warnings") or []:
        lines.append(f"- {warning}")
    if not report.get("warnings"):
        lines.append("- None")
    lines.extend(["", "## Evidence Boundary", "", f"- {report.get('sensitive_material_note')}", ""])
    return "\n".join(lines)


def write_report(root: Path, report: dict[str, Any], output_json: str, output_markdown: str) -> tuple[Path, Path]:
    json_path = _resolve_path(output_json, root)
    markdown_path = _resolve_path(output_markdown, root)
    assert json_path is not None
    assert markdown_path is not None
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, markdown_path


def archive_bundle(root: Path, report: dict[str, Any], json_path: Path, markdown_path: Path, history_root_text: str) -> dict[str, Any]:
    history_root = _resolve_path(history_root_text, root)
    assert history_root is not None
    created_at = str(report.get("generated_at") or datetime.now(UTC).isoformat())
    date_prefix = created_at[:10]
    entry_id = f"{date_prefix}-release-rehearsal-one-command"
    entry_dir = history_root / entry_id
    entry_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(json_path, entry_dir / "release_rehearsal.json")
    shutil.copyfile(markdown_path, entry_dir / "release_rehearsal.md")
    entry = {
        "schema_version": SCHEMA_VERSION,
        "entry_id": entry_id,
        "label": report.get("label"),
        "created_at": report.get("generated_at"),
        "status": report.get("status"),
        "family_statuses": {str(lane.get("id")): lane.get("status") for lane in report.get("lanes") or []},
        "summary": report.get("summary"),
        "artifacts": {"release_rehearsal_json": "release_rehearsal.json", "release_rehearsal_markdown": "release_rehearsal.md"},
    }
    (entry_dir / "entry.json").write_text(json.dumps(entry, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    index_path = history_root / "release-rehearsal-index.json"
    existing: list[dict[str, Any]] = []
    if index_path.exists():
        data, _ = _read_json(index_path)
        if data and isinstance(data.get("entries"), list):
            existing = [item for item in data["entries"] if isinstance(item, dict) and item.get("entry_id") != entry_id]
    existing.append(entry)
    index = {"schema_version": SCHEMA_VERSION, "generated_at": datetime.now(UTC).isoformat(), "entries": sorted(existing, key=lambda item: str(item.get("created_at") or ""))}
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"entry_id": entry_id, "entry_path": _display_path(entry_dir, root), "index_path": _display_path(index_path, root)}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect one-command release rehearsal evidence.")
    parser.add_argument("--label", default="release-rehearsal-one-command")
    parser.add_argument("--generated-at")
    parser.add_argument("--output-json", default=".tmp/release-rehearsal-evidence.json")
    parser.add_argument("--output-markdown", default=".tmp/release-rehearsal-evidence.md")
    parser.add_argument("--no-default-discovery", action="store_true")
    parser.add_argument("--release-evidence-report")
    parser.add_argument("--hosted-readiness-report")
    parser.add_argument("--benchmark-trend-report")
    parser.add_argument("--benchmark-comparison-report")
    parser.add_argument("--multi-repo-diagnosis-report")
    parser.add_argument("--guardrail-report")
    parser.add_argument("--readiness-history-report")
    parser.add_argument("--run-multi-repo-diagnosis", action="store_true")
    parser.add_argument("--multi-repo-output-json", default=".tmp/multi-repo-live-diagnosis.json")
    parser.add_argument("--multi-repo-output-markdown", default=".tmp/multi-repo-live-diagnosis.md")
    parser.add_argument("--multi-repo-pool", default=str(multi_repo.DEFAULT_POOL))
    parser.add_argument("--base-url", default="http://127.0.0.1:3001")
    parser.add_argument("--repo-id", action="append", default=[])
    parser.add_argument("--random-count", type=int)
    parser.add_argument("--random-seed", type=int, default=13)
    parser.add_argument("--session-token")
    parser.add_argument("--wait-import", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=900)
    parser.add_argument("--poll-seconds", type=float, default=5.0)
    parser.add_argument("--run-guardrail", action="store_true")
    parser.add_argument("--why-question", default="why is this repository architected this way")
    parser.add_argument("--evaluate-drift", action="store_true")
    parser.add_argument("--archive-history", action="store_true")
    parser.add_argument("--history-root", default="docs/evidence/readiness")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    report = build_report(args, root)
    json_path, markdown_path = write_report(root, report, args.output_json, args.output_markdown)
    if args.archive_history:
        report["history_archive"] = archive_bundle(root, report, json_path, markdown_path, args.history_root)
        json_path, markdown_path = write_report(root, report, args.output_json, args.output_markdown)
    print(f"Release rehearsal JSON written to {json_path}")
    print(f"Release rehearsal Markdown written to {markdown_path}")
    if report.get("history_archive"):
        print(f"Release rehearsal archived to {report['history_archive']['entry_path']}")
    print(f"Status: {report['status']}")
    return 1 if report["status"] == STATUS_BLOCKING else 0


if __name__ == "__main__":
    raise SystemExit(main())
