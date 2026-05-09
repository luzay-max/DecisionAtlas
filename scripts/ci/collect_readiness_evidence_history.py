from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
DEFAULT_HISTORY_ROOT = Path("docs/evidence/readiness")
FAMILY_RELEASE = "release_evidence"
FAMILY_HOSTED = "hosted_readiness"
FAMILY_BENCHMARK = "benchmark_comparison"
FAMILY_LABELS = {
    FAMILY_RELEASE: "Release evidence",
    FAMILY_HOSTED: "Hosted readiness",
    FAMILY_BENCHMARK: "Benchmark comparison",
}
NON_CLEAN_STATUSES = {
    "blocking",
    "caution",
    "failed",
    "incomplete",
    "known_limitation",
    "missing",
    "non_blocking",
    "not_provided",
    "operator_guided",
    "pause",
    "unknown",
    "warning",
}


@dataclass(frozen=True)
class EvidenceSource:
    family: str
    json_path: Path | None
    markdown_path: Path | None


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip().lower()).strip("-")
    return slug or "readiness-evidence"


def _resolve_path(path: Path | None, root: Path) -> Path | None:
    if path is None:
        return None
    return path if path.is_absolute() else root / path


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


def _safe_copy(source: Path | None, entry_dir: Path, target_name: str) -> tuple[str | None, str | None]:
    if source is None:
        return None, None
    if not source.exists():
        return None, f"Provided source path does not exist: {source}"
    if not source.is_file():
        return None, f"Provided source path is not a file: {source}"
    target = entry_dir / target_name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    return target.name, None


def _count_status(items: list[dict[str, Any]], statuses: set[str]) -> int:
    return sum(1 for item in items if str(item.get("status") or "").lower() in statuses)


def _summarize_release(data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"status": "not_provided"}
    required_gates = data.get("required_gates") if isinstance(data.get("required_gates"), list) else []
    advisory_signals = data.get("advisory_signals") if isinstance(data.get("advisory_signals"), list) else []
    evidence_items = data.get("evidence_items") if isinstance(data.get("evidence_items"), list) else required_gates + advisory_signals
    warnings = data.get("warnings") if isinstance(data.get("warnings"), list) else []
    missing_inputs = data.get("missing_inputs") if isinstance(data.get("missing_inputs"), list) else []
    blockers = [
        item
        for item in required_gates
        if str(item.get("status") or "").lower() in {"failed", "warning", "caution", "pause", "missing", "unknown"}
    ]
    return {
        "status": data.get("overall_status") or "unknown",
        "generated_at": data.get("generated_at"),
        "required_gate_statuses": {str(item.get("id")): item.get("status") for item in required_gates},
        "advisory_signal_statuses": {str(item.get("id")): item.get("status") for item in advisory_signals},
        "warning_count": len(warnings),
        "blocker_count": len(blockers),
        "missing_input_count": len(missing_inputs),
        "operator_guided_count": _count_status(evidence_items, {"operator_guided"}),
        "not_provided_count": _count_status(evidence_items, {"not_provided", "missing"}),
        "warnings": warnings,
        "missing_inputs": missing_inputs,
    }


def _summarize_hosted(data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"status": "not_provided", "public_walkthrough_status": "not_provided"}
    lanes = data.get("lanes") if isinstance(data.get("lanes"), list) else []
    blockers = data.get("blockers") if isinstance(data.get("blockers"), list) else []
    warnings = data.get("warnings") if isinstance(data.get("warnings"), list) else []
    operator_guided = [
        lane
        for lane in lanes
        if str(lane.get("status") or "").lower() == "operator_guided"
    ]
    known_limitations = [
        lane
        for lane in lanes
        if str(lane.get("status") or "").lower() == "known_limitation"
    ]
    return {
        "status": data.get("overall_status") or "unknown",
        "generated_at": data.get("generated_at"),
        "public_walkthrough_status": data.get("public_walkthrough_status"),
        "public_walkthrough_decision": data.get("public_walkthrough_decision"),
        "lane_statuses": {str(lane.get("id")): lane.get("status") for lane in lanes},
        "warning_count": len(warnings),
        "blocker_count": len(blockers),
        "operator_guided_count": len(operator_guided),
        "known_limitation_count": len(known_limitations),
        "not_provided_count": _count_status(lanes, {"not_provided"}),
        "warnings": warnings,
        "blockers": blockers,
        "operator_guided_lanes": [lane.get("id") for lane in operator_guided],
        "known_limitation_lanes": [lane.get("id") for lane in known_limitations],
    }


def _summarize_benchmark(data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"status": "not_provided"}
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    regressed = int(summary.get("regressed") or 0)
    operationally_blocked = int(summary.get("operationally_blocked") or 0)
    status = "warning" if regressed or operationally_blocked else "passed"
    return {
        "status": status,
        "generated_at": data.get("generated_at"),
        "comparison_type": data.get("comparison_type"),
        "repositories": int(summary.get("repositories") or 0),
        "movements": summary.get("movements") if isinstance(summary.get("movements"), dict) else {},
        "regressed": regressed,
        "improved": int(summary.get("improved") or 0),
        "operationally_blocked": operationally_blocked,
        "release_evidence_ready": summary.get("release_evidence_ready"),
    }


def _family_summary(family: str, data: dict[str, Any] | None) -> dict[str, Any]:
    if family == FAMILY_RELEASE:
        return _summarize_release(data)
    if family == FAMILY_HOSTED:
        return _summarize_hosted(data)
    if family == FAMILY_BENCHMARK:
        return _summarize_benchmark(data)
    raise ValueError(f"Unsupported evidence family: {family}")


def _artifact_names(family: str) -> tuple[str, str]:
    return f"{family}.json", f"{family}.md"


def _entry_status(families: dict[str, dict[str, Any]], warnings: list[str]) -> str:
    if warnings:
        return "warning"
    if any(str(summary.get("status") or "").lower() in NON_CLEAN_STATUSES for summary in families.values()):
        return "warning"
    return "passed"


def _entry_counts(families: dict[str, dict[str, Any]]) -> dict[str, int]:
    return {
        "warnings": sum(int(summary.get("warning_count") or 0) for summary in families.values()),
        "blockers": sum(int(summary.get("blocker_count") or 0) for summary in families.values()),
        "operator_guided": sum(int(summary.get("operator_guided_count") or 0) for summary in families.values()),
        "known_limitations": sum(int(summary.get("known_limitation_count") or 0) for summary in families.values()),
        "not_provided": sum(1 for summary in families.values() if summary.get("status") == "not_provided")
        + sum(int(summary.get("not_provided_count") or 0) for summary in families.values()),
        "benchmark_regressions": int(families.get(FAMILY_BENCHMARK, {}).get("regressed") or 0),
        "benchmark_operational_blockers": int(families.get(FAMILY_BENCHMARK, {}).get("operationally_blocked") or 0),
        "benchmark_improvements": int(families.get(FAMILY_BENCHMARK, {}).get("improved") or 0),
    }


def build_entry(
    *,
    sources: list[EvidenceSource],
    root: Path,
    history_root: Path,
    label: str,
    created_at: str,
    commit: str | None = None,
    version_label: str | None = None,
) -> dict[str, Any]:
    date_prefix = created_at[:10]
    entry_id = f"{date_prefix}-{_slugify(label)}"
    entry_dir = history_root / entry_id
    entry_dir.mkdir(parents=True, exist_ok=True)
    artifacts: dict[str, dict[str, Any]] = {}
    families: dict[str, dict[str, Any]] = {}
    warnings: list[str] = []

    for source in sources:
        json_source = _resolve_path(source.json_path, root)
        markdown_source = _resolve_path(source.markdown_path, root)
        json_name, markdown_name = _artifact_names(source.family)
        copied_json, json_error = _safe_copy(json_source, entry_dir, json_name)
        copied_markdown, markdown_error = _safe_copy(markdown_source, entry_dir, markdown_name)
        if json_error:
            warnings.append(f"{FAMILY_LABELS[source.family]} JSON: {json_error}")
        if markdown_error:
            warnings.append(f"{FAMILY_LABELS[source.family]} Markdown: {markdown_error}")

        data: dict[str, Any] | None = None
        if json_source is not None and json_error is None:
            data, read_error = _read_json(json_source)
            if read_error:
                warnings.append(f"{FAMILY_LABELS[source.family]} JSON: {read_error}")

        family_summary = _family_summary(source.family, data)
        family_summary["label"] = FAMILY_LABELS[source.family]
        family_summary["source_path"] = str(json_source) if json_source is not None else None
        family_summary["source_markdown_path"] = str(markdown_source) if markdown_source is not None else None
        families[source.family] = family_summary
        artifacts[source.family] = {
            "json": copied_json,
            "markdown": copied_markdown,
            "source_json_path": str(json_source) if json_source is not None else None,
            "source_markdown_path": str(markdown_source) if markdown_source is not None else None,
        }

    counts = _entry_counts(families)
    entry = {
        "schema_version": SCHEMA_VERSION,
        "entry_id": entry_id,
        "label": label,
        "created_at": created_at,
        "commit": commit,
        "version_label": version_label,
        "status": _entry_status(families, warnings),
        "artifacts": artifacts,
        "families": families,
        "counts": counts,
        "warnings": warnings,
        "sensitive_material_note": (
            "Do not archive secrets, private repository contents, raw model output, "
            "or unnecessary local-only logs."
        ),
    }
    _write_json(entry_dir / "entry.json", entry)
    return entry


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load_entries(history_root: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    if not history_root.exists():
        return entries
    for entry_path in sorted(history_root.glob("*/entry.json")):
        data, error = _read_json(entry_path)
        if error is None and data is not None:
            entries.append(data)
    return sorted(entries, key=lambda item: (str(item.get("created_at") or ""), str(item.get("entry_id") or "")))


def _index_entry(entry: dict[str, Any]) -> dict[str, Any]:
    families = entry.get("families") if isinstance(entry.get("families"), dict) else {}
    return {
        "entry_id": entry.get("entry_id"),
        "label": entry.get("label"),
        "created_at": entry.get("created_at"),
        "commit": entry.get("commit"),
        "version_label": entry.get("version_label"),
        "status": entry.get("status"),
        "family_statuses": {
            family: (summary or {}).get("status")
            for family, summary in sorted(families.items())
            if isinstance(summary, dict)
        },
        "counts": entry.get("counts") or {},
        "warnings": entry.get("warnings") or [],
    }


def build_index(history_root: Path) -> dict[str, Any]:
    entries = [_index_entry(entry) for entry in _load_entries(history_root)]
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(UTC).isoformat(),
        "history_root": str(history_root),
        "entries": entries,
    }


def render_index_markdown(index: dict[str, Any]) -> str:
    lines = [
        "# Readiness Evidence History",
        "",
        f"- Generated at: `{index.get('generated_at')}`",
        f"- Entries: `{len(index.get('entries') or [])}`",
        "",
        "| Entry | Created | Status | Release | Hosted | Benchmark | Warnings | Blockers | Benchmark movement |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for entry in index.get("entries") or []:
        statuses = entry.get("family_statuses") or {}
        counts = entry.get("counts") or {}
        movement = (
            f"improved={counts.get('benchmark_improvements', 0)}, "
            f"regressed={counts.get('benchmark_regressions', 0)}, "
            f"operationally_blocked={counts.get('benchmark_operational_blockers', 0)}"
        )
        lines.append(
            "| "
            + " | ".join(
                _markdown_cell(value)
                for value in (
                    entry.get("entry_id"),
                    entry.get("created_at"),
                    entry.get("status"),
                    statuses.get(FAMILY_RELEASE),
                    statuses.get(FAMILY_HOSTED),
                    statuses.get(FAMILY_BENCHMARK),
                    counts.get("warnings", 0),
                    counts.get("blockers", 0),
                    movement,
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- `.tmp` remains scratch output. Durable history is created only from explicit archive command inputs.",
            "- Non-clean states such as warning, blocking, operator_guided, known_limitation, and not_provided are preserved.",
            "- Do not archive secrets, private repository contents, raw model output, or unnecessary local-only logs.",
            "",
        ]
    )
    return "\n".join(lines)


def render_trend_markdown(entries: list[dict[str, Any]], limit: int) -> str:
    selected = entries[-limit:] if limit > 0 else entries
    lines = [
        "# Readiness Evidence Trend",
        "",
        f"- Entries compared: `{len(selected)}`",
        "",
    ]
    if not selected:
        lines.extend(["No readiness evidence history entries found.", ""])
        return "\n".join(lines)

    lines.extend(
        [
            "| Entry | Status | Release | Hosted walkthrough | Benchmark regressions | Benchmark blockers | Warnings | Operator-guided | Not provided |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for entry in selected:
        families = entry.get("families") or {}
        counts = entry.get("counts") or {}
        release = (families.get(FAMILY_RELEASE) or {}).get("status")
        hosted = (families.get(FAMILY_HOSTED) or {}).get("public_walkthrough_status") or (families.get(FAMILY_HOSTED) or {}).get("status")
        lines.append(
            "| "
            + " | ".join(
                _markdown_cell(value)
                for value in (
                    entry.get("entry_id"),
                    entry.get("status"),
                    release,
                    hosted,
                    counts.get("benchmark_regressions", 0),
                    counts.get("benchmark_operational_blockers", 0),
                    counts.get("warnings", 0),
                    counts.get("operator_guided", 0),
                    counts.get("not_provided", 0),
                )
            )
            + " |"
        )

    latest = selected[-1]
    counts = latest.get("counts") or {}
    follow_up: list[str] = []
    if counts.get("benchmark_regressions"):
        follow_up.append("Investigate benchmark regressions before claiming product-quality improvement.")
    if counts.get("benchmark_operational_blockers"):
        follow_up.append("Resolve benchmark operational blockers and rerun comparison.")
    if counts.get("operator_guided"):
        follow_up.append("Complete operator-guided hosted readiness lanes before external preview.")
    if counts.get("not_provided"):
        follow_up.append("Attach missing optional evidence if it is part of the release or preview claim.")
    if not follow_up:
        follow_up.append("No non-clean trend follow-up detected in the latest entry.")

    lines.extend(["", "## Recommended Follow-up", ""])
    lines.extend(f"- {item}" for item in follow_up)
    lines.append("")
    return "\n".join(lines)


def _markdown_cell(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, dict):
        text = json.dumps(value, sort_keys=True)
    elif isinstance(value, list):
        text = ", ".join(str(item) for item in value)
    else:
        text = str(value)
    return text.replace("|", "\\|").replace("\n", "<br>") or "-"


def archive_history(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    created_at = args.created_at or datetime.now(UTC).isoformat()
    history_root = _resolve_path(Path(args.history_root), root) or (root / DEFAULT_HISTORY_ROOT)
    sources = [
        EvidenceSource(FAMILY_RELEASE, Path(args.release_evidence_json) if args.release_evidence_json else None, Path(args.release_evidence_markdown) if args.release_evidence_markdown else None),
        EvidenceSource(FAMILY_HOSTED, Path(args.hosted_readiness_json) if args.hosted_readiness_json else None, Path(args.hosted_readiness_markdown) if args.hosted_readiness_markdown else None),
        EvidenceSource(FAMILY_BENCHMARK, Path(args.benchmark_comparison_json) if args.benchmark_comparison_json else None, Path(args.benchmark_comparison_markdown) if args.benchmark_comparison_markdown else None),
    ]
    entry = build_entry(
        sources=sources,
        root=root,
        history_root=history_root,
        label=args.label,
        created_at=created_at,
        commit=args.commit,
        version_label=args.version_label,
    )
    index = build_index(history_root)
    _write_json(history_root / "index.json", index)
    (history_root / "index.md").write_text(render_index_markdown(index), encoding="utf-8")
    trend_markdown = render_trend_markdown(_load_entries(history_root), args.trend_limit)
    (history_root / "trend.md").write_text(trend_markdown, encoding="utf-8")
    return entry


def summarize_history(args: argparse.Namespace, root: Path) -> str:
    history_root = _resolve_path(Path(args.history_root), root) or (root / DEFAULT_HISTORY_ROOT)
    index = build_index(history_root)
    _write_json(history_root / "index.json", index)
    index_markdown = render_index_markdown(index)
    (history_root / "index.md").write_text(index_markdown, encoding="utf-8")
    trend_markdown = render_trend_markdown(_load_entries(history_root), args.trend_limit)
    if args.trend_output:
        trend_path = _resolve_path(Path(args.trend_output), root)
        assert trend_path is not None
        trend_path.parent.mkdir(parents=True, exist_ok=True)
        trend_path.write_text(trend_markdown, encoding="utf-8")
    return trend_markdown


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Archive selected readiness evidence into durable local history.")
    parser.add_argument("--history-root", default=str(DEFAULT_HISTORY_ROOT), help="Durable readiness evidence history directory.")
    parser.add_argument("--trend-limit", type=int, default=5, help="Number of recent entries to include in trend Markdown.")
    subparsers = parser.add_subparsers(dest="command")

    archive = subparsers.add_parser("archive", help="Archive explicitly supplied evidence files into history.")
    archive.add_argument("--label", required=True, help="Human-readable entry label used in the entry id.")
    archive.add_argument("--created-at", help="Override created_at timestamp for deterministic runs.")
    archive.add_argument("--commit", help="Commit hash or reference associated with this evidence.")
    archive.add_argument("--version-label", help="Release, preview, or project version label.")
    archive.add_argument("--release-evidence-json", help="Explicit release evidence JSON path.")
    archive.add_argument("--release-evidence-markdown", help="Explicit release evidence Markdown path.")
    archive.add_argument("--hosted-readiness-json", help="Explicit hosted readiness JSON path.")
    archive.add_argument("--hosted-readiness-markdown", help="Explicit hosted readiness Markdown path.")
    archive.add_argument("--benchmark-comparison-json", help="Explicit real-repo benchmark comparison JSON path.")
    archive.add_argument("--benchmark-comparison-markdown", help="Explicit real-repo benchmark comparison Markdown path.")

    summarize = subparsers.add_parser("summarize", help="Regenerate index and trend summary from archived entries.")
    summarize.add_argument("--trend-output", help="Optional path for trend Markdown output.")
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    if args.command == "archive":
        entry = archive_history(args, root)
        print(f"Readiness evidence entry archived: {entry['entry_id']}")
        print(f"Status: {entry['status']}")
        return 0
    if args.command == "summarize":
        print(summarize_history(args, root))
        return 0
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
