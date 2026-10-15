from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
DEFAULT_OUTPUT_JSON = Path(".tmp/trend-comparison.json")
DEFAULT_OUTPUT_MARKDOWN = Path(".tmp/trend-comparison.md")
DEFAULT_HISTORY_DIR = Path("docs/evidence/readiness")


def _read_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_markdown(path: Path, markdown: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def load_previous_evidence(history_dir: Path) -> dict[str, Any] | None:
    index_path = history_dir / "index.json"
    index = _read_json(index_path)
    if not index or not isinstance(index, dict):
        return None
    entries = index.get("entries", [])
    if not entries:
        return None
    latest = entries[-1]
    evidence_path = history_dir / latest.get("id", "") / "evidence.json"
    return _read_json(evidence_path)


def load_current_benchmark(benchmark_json: Path) -> dict[str, Any] | None:
    return _read_json(benchmark_json)


def load_current_guardrail(guardrail_json: Path) -> dict[str, Any] | None:
    return _read_json(guardrail_json)


def compare_metrics(previous: dict[str, Any] | None, current: dict[str, Any]) -> list[dict[str, Any]]:
    comparisons = []
    if not previous:
        comparisons.append({
            "metric": "baseline_available",
            "previous": None,
            "current": "yes",
            "movement": "first-release",
            "note": "No previous release evidence found for comparison.",
        })
        return comparisons

    metric_pairs = [
        ("accepted_decisions", "Accepted decisions"),
        ("artifacts", "Artifacts imported"),
        ("reviewable_candidates", "Reviewable candidates"),
        ("drift_alerts", "Drift alerts"),
        ("open_spec_specs", "OpenSpec specs"),
    ]

    for key, label in metric_pairs:
        prev_val = _extract_metric(previous, key)
        curr_val = _extract_metric(current, key)
        movement = _classify_movement(prev_val, curr_val)
        comparisons.append({
            "metric": key,
            "label": label,
            "previous": prev_val,
            "current": curr_val,
            "movement": movement,
        })

    return comparisons


def _extract_metric(evidence: dict[str, Any], key: str) -> int | str | None:
    if key in evidence:
        return evidence[key]
    summary = evidence.get("summary", {})
    if key in summary:
        return summary[key]
    return None


def _classify_movement(prev: Any, curr: Any) -> str:
    if prev is None and curr is None:
        return "unchanged"
    if prev is None:
        return "first-measurement"
    if curr is None:
        return "missing-from-current"
    try:
        prev_num = float(prev)
        curr_num = float(curr)
        if curr_num > prev_num:
            return "improved"
        if curr_num < prev_num:
            return "regressed"
        return "unchanged"
    except (ValueError, TypeError):
        if str(prev) == str(curr):
            return "unchanged"
        return "changed"


def overall_status(comparisons: list[dict[str, Any]], guardrail_status: str | None) -> str:
    non_clean = {"regressed", "missing-from-current", "operationally-blocked"}
    has_regressions = any(c["movement"] in non_clean for c in comparisons)
    if has_regressions:
        return "warning"
    if guardrail_status in {"pause", "caution", "blocked"}:
        return "caution"
    return "passed"


def render_markdown(
    comparisons: list[dict[str, Any]],
    guardrail_status: str | None,
    status: str,
    generated_at: str,
) -> str:
    lines = [
        f"# Trend Comparison Report",
        f"",
        f"Generated: {generated_at}",
        f"Status: **{status}**",
        f"",
    ]

    if guardrail_status:
        lines.append(f"Guardrail status: {guardrail_status}")
        lines.append("")

    lines.append("## Metric Comparison")
    lines.append("")
    lines.append("| Metric | Previous | Current | Movement |")
    lines.append("|--------|----------|---------|----------|")

    for c in comparisons:
        label = c.get("label", c["metric"])
        prev = c["previous"] if c["previous"] is not None else "-"
        curr = c["current"] if c["current"] is not None else "-"
        movement = c["movement"]
        emoji = {
            "improved": "+",
            "regressed": "-",
            "unchanged": "=",
            "first-measurement": "*",
            "missing-from-current": "!",
            "changed": "~",
            "first-release": "*",
        }.get(movement, "?")
        lines.append(f"| {label} | {prev} | {curr} | {emoji} {movement} |")

    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- Metrics marked with `*` indicate first-release or first-measurement baselines.")
    lines.append("- Metrics marked with `!` indicate data present in previous release but missing from current.")
    lines.append("- This report is advisory and does not block releases by default.")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare release trend metrics against previous evidence.")
    parser.add_argument("--history-dir", type=Path, default=DEFAULT_HISTORY_DIR)
    parser.add_argument("--benchmark-json", type=Path, default=Path(".tmp/current-real-repo-benchmark-snapshot.json"))
    parser.add_argument("--guardrail-json", type=Path, default=Path(".tmp/guardrail-summary.json"))
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-markdown", type=Path, default=DEFAULT_OUTPUT_MARKDOWN)
    parser.add_argument("--generated-at", type=str, default=None)
    args = parser.parse_args()

    generated_at = args.generated_at or datetime.now(UTC).isoformat()

    previous = load_previous_evidence(args.history_dir)
    current_benchmark = load_current_benchmark(args.benchmark_json)
    current_guardrail = load_current_guardrail(args.guardrail_json)

    current = current_benchmark or {}
    if current_guardrail:
        current["guardrail_status"] = current_guardrail.get("status")

    guardrail_status = current.get("guardrail_status")
    comparisons = compare_metrics(previous, current)
    status = overall_status(comparisons, guardrail_status)

    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": status,
        "guardrail_status": guardrail_status,
        "has_previous_baseline": previous is not None,
        "comparisons": comparisons,
    }

    _write_json(args.output_json, payload)
    _write_markdown(args.output_markdown, render_markdown(comparisons, guardrail_status, status, generated_at))

    print(f"Trend comparison: {status}")
    print(f"JSON: {args.output_json}")
    print(f"Markdown: {args.output_markdown}")

    if status == "warning":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
