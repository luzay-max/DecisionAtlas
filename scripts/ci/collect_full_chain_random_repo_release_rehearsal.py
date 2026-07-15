from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import collect_readiness_evidence_history as readiness_history  # noqa: E402


SCHEMA_VERSION = 1
STATUS_PASS = "pass"
STATUS_WARNING = "warning"
STATUS_BLOCKING = "blocking"
STATUS_OPERATOR_GUIDED = "operator_guided"
STATUS_NOT_PROVIDED = "not_provided"
STATUS_UNKNOWN = "unknown"

PASS_STATUSES = {"pass", "passed", "ok", "success", "succeeded", "clean", "ready", "true"}
BLOCKING_STATUSES = {"blocking", "blocked", "failed", "failure", "error", "false", "provider_failure", "local_stack_failure"}
WARNING_STATUSES = {"warning", "warn", "caution", "known_limitation", "needs_review", "manual_check"}


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
        return STATUS_WARNING
    if normalized in {"operator", "operator_guided", "manual", "manual_required"}:
        return STATUS_OPERATOR_GUIDED
    if normalized in {"missing", "omitted", "not_provided", "not_available"}:
        return STATUS_NOT_PROVIDED
    return normalized or default


def status_rank(status: Any) -> int:
    normalized = normalize_status(status)
    if normalized == STATUS_BLOCKING:
        return 2
    if normalized == STATUS_PASS:
        return 0
    return 1


def combined_status(statuses: list[str]) -> str:
    if any(status_rank(status) >= 2 for status in statuses):
        return STATUS_BLOCKING
    if any(status_rank(status) == 1 for status in statuses):
        return STATUS_WARNING
    return STATUS_PASS


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
        return path.as_posix()


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


def _bounded(value: Any, limit: int = 600) -> Any:
    if isinstance(value, dict):
        return {str(key): _bounded(item, limit=limit) for key, item in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, list):
        return [_bounded(item, limit=limit) for item in value[:30]]
    if isinstance(value, str):
        text = value.strip()
        return text if len(text) <= limit else text[: limit - 1].rstrip() + "..."
    return value


def _source_data(path_text: str | None, root: Path) -> tuple[Path | None, dict[str, Any] | None, str | None]:
    path = _resolve_path(path_text, root)
    if path is None:
        return None, None, None
    if not path.exists():
        return path, None, "source_missing"
    data, error = _read_json(path)
    return path, data, error


def _status_from_data(data: dict[str, Any] | None) -> str:
    if data is None:
        return STATUS_NOT_PROVIDED
    for key in ("status", "overall_status", "public_walkthrough_status", "agent_status", "result", "outcome"):
        if key in data:
            return normalize_status(data.get(key))
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    if "status" in summary:
        return normalize_status(summary.get("status"))
    return STATUS_UNKNOWN


def _multi_repo_summary(data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"status": STATUS_NOT_PROVIDED, "selected_repo_ids": []}
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    return {
        "status": _status_from_data(data),
        "selected_repo_ids": data.get("selected_repo_ids") or [],
        "selected_repositories": summary.get("selected_repositories"),
        "pass": summary.get("pass"),
        "warning": summary.get("warning"),
        "blocking": summary.get("blocking"),
        "recommended_follow_up": _bounded(data.get("recommended_follow_up") or []),
    }


def _release_summary(data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"status": STATUS_NOT_PROVIDED}
    return {
        "status": _status_from_data(data),
        "summary": _bounded(data.get("summary") if isinstance(data.get("summary"), dict) else {}),
        "generated_paths": _bounded(data.get("generated_paths") if isinstance(data.get("generated_paths"), dict) else {}),
        "recommended_follow_up": _bounded(data.get("recommended_follow_up") or []),
    }


def _customer_host_summary(data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"status": STATUS_NOT_PROVIDED, "host_proof_level": "not_provided"}
    return {
        "status": _status_from_data(data),
        "host_proof_level": data.get("host_proof_level"),
        "summary": _bounded(data.get("summary") if isinstance(data.get("summary"), dict) else {}),
        "limitations": _bounded(data.get("limitations") or []),
    }


def _readiness_history_summary(data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"status": STATUS_NOT_PROVIDED, "entry_count": 0}
    entries = data.get("entries") if isinstance(data.get("entries"), list) else []
    latest = entries[-1] if entries and isinstance(entries[-1], dict) else {}
    return {
        "status": normalize_status(latest.get("status"), STATUS_NOT_PROVIDED),
        "entry_count": len(entries),
        "latest_entry_id": latest.get("entry_id"),
    }


def _generic_summary(data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"status": STATUS_NOT_PROVIDED}
    return {"status": _status_from_data(data), "summary": _bounded(data.get("summary") if isinstance(data.get("summary"), dict) else {})}


def _lane(lane_id: str, label: str, path_text: str | None, root: Path, summarizer) -> dict[str, Any]:
    path, data, error = _source_data(path_text, root)
    summary = summarizer(data)
    lane = {
        "id": lane_id,
        "label": label,
        "status": normalize_status(summary.get("status"), STATUS_NOT_PROVIDED),
        "source_path": _display_path(path, root),
        "summary": summary,
        "warnings": [],
    }
    if path_text and error:
        lane["status"] = STATUS_WARNING
        lane["warnings"] = [error]
    if not path_text:
        lane["warnings"] = ["source_not_provided"]
    return lane


def _browser_lane(args: argparse.Namespace) -> dict[str, Any]:
    status = normalize_status(args.browser_status, STATUS_OPERATOR_GUIDED)
    return {
        "id": "browser_rehearsal",
        "label": "Browser rehearsal",
        "status": status,
        "source_path": None,
        "summary": {
            "command": args.browser_command,
            "summary": args.browser_summary,
            "status": status,
        },
        "warnings": [] if status == STATUS_PASS else ["browser_rehearsal_not_clean_pass"],
    }


def build_report(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    lanes = [
        _lane("multi_repo_diagnosis", "Random real GitHub repositories", args.multi_repo_diagnosis_json, root, _multi_repo_summary),
        _lane("release_rehearsal", "Release rehearsal", args.release_rehearsal_json, root, _release_summary),
        _lane("customer_host_v2", "Customer-host v2", args.customer_host_v2_json, root, _customer_host_summary),
        _browser_lane(args),
        _lane("readiness_history", "Readiness history", args.readiness_history_json, root, _readiness_history_summary),
    ]
    selected_repo_ids: list[str] = []
    multi_repo_lane = next((lane for lane in lanes if lane["id"] == "multi_repo_diagnosis"), None)
    if multi_repo_lane:
        selected_repo_ids = [str(repo_id) for repo_id in multi_repo_lane.get("summary", {}).get("selected_repo_ids") or []]
    status = combined_status([str(lane.get("status") or STATUS_UNKNOWN) for lane in lanes])
    non_pass = [lane["id"] for lane in lanes if status_rank(lane.get("status")) > 0]
    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": args.generated_at or datetime.now(UTC).isoformat(),
        "evidence_type": "full-chain-random-repo-release-rehearsal",
        "label": args.label,
        "version_label": args.version_label,
        "commit": args.commit,
        "status": status,
        "selected_repo_ids": selected_repo_ids,
        "summary": {
            "lanes": len(lanes),
            "pass": sum(1 for lane in lanes if status_rank(lane.get("status")) == 0),
            "warning": sum(1 for lane in lanes if status_rank(lane.get("status")) == 1),
            "blocking": sum(1 for lane in lanes if status_rank(lane.get("status")) >= 2),
            "operator_guided": sum(1 for lane in lanes if normalize_status(lane.get("status")) == STATUS_OPERATOR_GUIDED),
            "not_provided": sum(1 for lane in lanes if normalize_status(lane.get("status")) == STATUS_NOT_PROVIDED),
            "selected_repositories": len(selected_repo_ids),
        },
        "lanes": lanes,
        "blockers": [lane for lane in lanes if normalize_status(lane.get("status")) == STATUS_BLOCKING],
        "limitations": [
            "This bundle composes bounded evidence; it does not embed raw logs, secrets, or private repository content.",
            "Random real repository diagnosis depends on local stack, GitHub, and provider availability.",
            "Customer-host proof is only as strong as the supplied customer-host v2 evidence.",
        ],
        "recommended_next_actions": _recommended_next_actions(status, non_pass, selected_repo_ids),
    }
    return report


def _recommended_next_actions(status: str, non_pass: list[str], selected_repo_ids: list[str]) -> list[str]:
    actions: list[str] = []
    if not selected_repo_ids:
        actions.append("Run random real GitHub repository diagnosis and attach the multi-repo evidence.")
    if non_pass:
        actions.append(f"Review or disclose non-pass full-chain lanes: {', '.join(non_pass)}.")
    if status == STATUS_BLOCKING:
        actions.append("Resolve blocking lanes before claiming full-chain release readiness.")
    actions.append("Archive this full-chain rehearsal with release/customer-host evidence before handoff.")
    return actions


def _markdown_cell(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, (dict, list)):
        text = json.dumps(value, sort_keys=True, ensure_ascii=False)
    else:
        text = str(value)
    return text.replace("|", "\\|").replace("\n", "<br>") or "-"


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    lines = [
        "# Full-Chain Random Repo Release Rehearsal",
        "",
        f"- Label: `{report.get('label')}`",
        f"- Generated at: `{report.get('generated_at')}`",
        f"- Status: `{report.get('status')}`",
        f"- Selected real repositories: `{', '.join(report.get('selected_repo_ids') or []) or '-'}`",
        f"- Pass lanes: `{summary.get('pass', 0)}`",
        f"- Warning lanes: `{summary.get('warning', 0)}`",
        f"- Blocking lanes: `{summary.get('blocking', 0)}`",
        "",
        "## Evidence Lanes",
        "",
        "| Lane | Status | Source | Summary |",
        "| --- | --- | --- | --- |",
    ]
    for lane in report.get("lanes") or []:
        lines.append(
            f"| {_markdown_cell(lane.get('label'))} | {_markdown_cell(lane.get('status'))} | "
            f"{_markdown_cell(lane.get('source_path'))} | {_markdown_cell(lane.get('summary'))} |"
        )
    lines.extend(["", "## Limitations", ""])
    for limitation in report.get("limitations") or []:
        lines.append(f"- {limitation}")
    lines.extend(["", "## Recommended Next Actions", ""])
    for action in report.get("recommended_next_actions") or []:
        lines.append(f"- {action}")
    lines.append("")
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


def archive_report(root: Path, report: dict[str, Any], json_path: Path, markdown_path: Path, args: argparse.Namespace) -> dict[str, Any]:
    history_root = _resolve_path(args.history_root, root)
    assert history_root is not None
    entry = readiness_history.build_entry(
        sources=[
            readiness_history.EvidenceSource(
                readiness_history.FAMILY_FULL_CHAIN_RANDOM_REPO_RELEASE,
                json_path,
                markdown_path,
            )
        ],
        root=root,
        history_root=history_root,
        label=args.archive_label or args.label,
        created_at=str(report.get("generated_at") or datetime.now(UTC).isoformat()),
        commit=args.commit,
        version_label=args.version_label,
    )
    index = readiness_history.build_index(history_root)
    (history_root / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (history_root / "index.md").write_text(readiness_history.render_index_markdown(index), encoding="utf-8")
    trend = readiness_history.render_trend_markdown(readiness_history._load_entries(history_root), args.trend_limit)
    (history_root / "trend.md").write_text(trend, encoding="utf-8")
    return {
        "entry_id": entry.get("entry_id"),
        "entry_path": _display_path(history_root / str(entry.get("entry_id")), root),
        "index_path": _display_path(history_root / "index.json", root),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect full-chain random repo release rehearsal evidence.")
    parser.add_argument("--label", default="full-chain-random-repo-release-rehearsal")
    parser.add_argument("--generated-at")
    parser.add_argument("--version-label")
    parser.add_argument("--commit")
    parser.add_argument("--multi-repo-diagnosis-json", default=".tmp/multi-repo-live-diagnosis.json")
    parser.add_argument("--release-rehearsal-json", default=".tmp/release-rehearsal-evidence.json")
    parser.add_argument("--customer-host-v2-json", default=".tmp/external-customer-host-rehearsal-v2.json")
    parser.add_argument("--readiness-history-json", default="docs/evidence/readiness/index.json")
    parser.add_argument("--browser-status", default=STATUS_OPERATOR_GUIDED)
    parser.add_argument("--browser-command", default="pnpm --filter @decisionatlas/web exec playwright test team-self-hosted-rehearsal.spec.ts --config playwright.config.ts --reporter=line")
    parser.add_argument("--browser-summary", default="Browser rehearsal not supplied in this bundle.")
    parser.add_argument("--output-json", default=".tmp/full-chain-random-repo-release-rehearsal.json")
    parser.add_argument("--output-markdown", default=".tmp/full-chain-random-repo-release-rehearsal.md")
    parser.add_argument("--archive-history", action="store_true")
    parser.add_argument("--archive-label")
    parser.add_argument("--history-root", default="docs/evidence/readiness")
    parser.add_argument("--trend-limit", type=int, default=5)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    report = build_report(args, root)
    json_path, markdown_path = write_report(root, report, args.output_json, args.output_markdown)
    if args.archive_history:
        report["history_archive"] = archive_report(root, report, json_path, markdown_path, args)
        json_path, markdown_path = write_report(root, report, args.output_json, args.output_markdown)
    print(f"Full-chain rehearsal JSON written to {json_path}")
    print(f"Full-chain rehearsal Markdown written to {markdown_path}")
    if report.get("history_archive"):
        print(f"Archived to {report['history_archive']['entry_path']}")
    print(f"Status: {report['status']}")
    return 1 if report["status"] == STATUS_BLOCKING else 0


if __name__ == "__main__":
    raise SystemExit(main())
