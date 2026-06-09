from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
from pathlib import Path
import random
import sys
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import collect_real_repo_benchmark_trend as trend_tool
import run_benchmark


DEFAULT_POOL = Path("examples/live-benchmarks/trend-pool.json")
DEFAULT_BASELINE = Path("examples/live-benchmarks/history-snapshot.example.json")
DEFAULT_OUTPUT_DIR = Path(".tmp")
SCHEMA_VERSION = 1


def _read_json(path: Path) -> dict[str, Any]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected JSON object at {path}")
    return loaded


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_markdown(path: Path, markdown: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def _display_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _markdown_cell(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, (dict, list)):
        text = json.dumps(value, sort_keys=True, ensure_ascii=False)
    else:
        text = str(value)
    return text.replace("|", "\\|").replace("\n", "<br>") or "-"


def _artifact_prefix(output_json: Path, explicit_prefix: str | None) -> str:
    if explicit_prefix:
        return explicit_prefix.strip().strip("-") or "real-repo-benchmark-coverage"
    stem = output_json.stem
    if stem.endswith("-rehearsal"):
        stem = stem[: -len("-rehearsal")]
    return stem or "real-repo-benchmark-coverage"


def select_repo_ids(pool: list[dict[str, Any]], *, repo_ids: list[str], random_count: int | None, random_seed: int) -> list[str]:
    available = [str(repo["id"]) for repo in pool if repo.get("id")]
    if repo_ids:
        unknown = sorted(set(repo_ids) - set(available))
        if unknown:
            raise ValueError(f"Unknown trend pool repo id(s): {', '.join(unknown)}")
        selected = repo_ids
    else:
        selected = available
    if random_count is None:
        return selected
    if random_count < 1:
        raise ValueError("--random-count must be greater than zero.")
    if random_count > len(selected):
        raise ValueError("--random-count cannot exceed selected repo count.")
    sampler = random.Random(random_seed)
    return sorted(sampler.sample(selected, random_count))


def _filter_pool(pool: list[dict[str, Any]], repo_ids: list[str]) -> list[dict[str, Any]]:
    requested = set(repo_ids)
    return [repo for repo in pool if repo.get("id") in requested]


def _run_live_current_report(
    *,
    root: Path,
    base_url: str,
    repo_ids: list[str],
    report_path: Path,
    markdown_path: Path,
) -> tuple[str, list[str]]:
    live_dir = root / "examples" / "live-benchmarks"
    repositories = run_benchmark.load_json(live_dir / "repositories.json")
    why_cases = run_benchmark.load_json(live_dir / "why-cases.json")
    drift_cases = run_benchmark.load_json(live_dir / "drift-cases.json")
    repositories, why_cases, drift_cases = run_benchmark._filter_live_repo_inputs(
        repositories=repositories,
        why_cases=why_cases,
        drift_cases=drift_cases,
        repo_ids=repo_ids,
    )
    live_exit = run_benchmark.run_live_real_repo_validation(
        base_url=base_url,
        repositories=repositories,
        why_cases=why_cases,
        drift_cases=drift_cases,
        report_path=report_path,
        markdown_report_path=markdown_path,
    )
    warnings = []
    if live_exit != 0:
        warnings.append("live_real_repo_validation_returned_non_zero")
    return ("warning" if live_exit else "pass"), warnings


def _status_from_trend(trend: dict[str, Any], warnings: list[str]) -> str:
    if warnings:
        return "warning"
    status = str(trend.get("status") or "unknown")
    if status in {"blocking", "failed", "error"}:
        return "blocking"
    if status in {"warning", "caution", "not_provided", "operator_guided"}:
        return "warning"
    return "pass"


def build_rehearsal(
    *,
    root: Path,
    label: str,
    generated_at: str,
    pool_path: Path,
    baseline_snapshot_path: Path,
    output_dir: Path,
    output_json: Path,
    output_markdown: Path,
    current_report_path: Path | None = None,
    current_report_markdown_path: Path | None = None,
    live: bool = False,
    base_url: str = "http://127.0.0.1:3001",
    repo_ids: list[str] | None = None,
    random_count: int | None = None,
    random_seed: int = 9,
    artifact_prefix: str | None = None,
) -> dict[str, Any]:
    warnings: list[str] = []
    pool = trend_tool.load_pool(pool_path)
    selected_repo_ids = select_repo_ids(pool, repo_ids=repo_ids or [], random_count=random_count, random_seed=random_seed)
    selected_pool = _filter_pool(pool, selected_repo_ids)

    current_report = current_report_path
    current_report_markdown = current_report_markdown_path
    live_status = "not_requested"
    if live:
        prefix = _artifact_prefix(output_json, artifact_prefix)
        current_report = output_dir / f"{prefix}-current-report.json"
        current_report_markdown = output_dir / f"{prefix}-current-report.md"
        live_status, live_warnings = _run_live_current_report(
            root=root,
            base_url=base_url,
            repo_ids=selected_repo_ids,
            report_path=current_report,
            markdown_path=current_report_markdown,
        )
        warnings.extend(live_warnings)

    if current_report is None:
        raise ValueError("--current-report-json is required unless --live is used.")
    if not current_report.exists():
        raise ValueError(f"Current report JSON does not exist: {current_report}")
    if not baseline_snapshot_path.exists():
        raise ValueError(f"Baseline snapshot JSON does not exist: {baseline_snapshot_path}")

    current_payload = _read_json(current_report)
    baseline_payload = _read_json(baseline_snapshot_path)
    current_snapshot = run_benchmark._snapshot_from_report_or_snapshot(current_payload)
    baseline_snapshot = run_benchmark._snapshot_from_report_or_snapshot(baseline_payload)

    prefix = _artifact_prefix(output_json, artifact_prefix)
    snapshot_path = output_dir / f"{prefix}-current-snapshot.json"
    comparison_path = output_dir / f"{prefix}-comparison.json"
    comparison_markdown_path = output_dir / f"{prefix}-comparison.md"
    trend_path = output_dir / f"{prefix}-trend.json"
    trend_markdown_path = output_dir / f"{prefix}-trend.md"

    run_benchmark._write_report(snapshot_path, current_snapshot)
    comparison = run_benchmark.compare_benchmark_snapshots(
        current_snapshot=current_snapshot,
        baseline_snapshot=baseline_snapshot,
    )
    run_benchmark._write_report(comparison_path, comparison)
    run_benchmark._write_benchmark_comparison_markdown(comparison_markdown_path, comparison)

    trend = trend_tool.build_trend(
        pool=selected_pool,
        comparison=comparison,
        generated_at=generated_at,
        label=label,
    )
    _write_json(trend_path, trend)
    _write_markdown(trend_markdown_path, trend_tool.render_markdown(trend))

    status = _status_from_trend(trend, warnings)
    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "label": label,
        "status": status,
        "mode": "live" if live else "offline",
        "base_url": base_url if live else None,
        "selected_repo_ids": selected_repo_ids,
        "random_selection": {"enabled": random_count is not None, "count": random_count, "seed": random_seed},
        "live_status": live_status,
        "artifacts": {
            "current_report_json": _display_path(current_report, root),
            "current_report_markdown": _display_path(current_report_markdown, root) if current_report_markdown else None,
            "current_snapshot_json": _display_path(snapshot_path, root),
            "baseline_snapshot_json": _display_path(baseline_snapshot_path, root),
            "comparison_json": _display_path(comparison_path, root),
            "comparison_markdown": _display_path(comparison_markdown_path, root),
            "trend_json": _display_path(trend_path, root),
            "trend_markdown": _display_path(trend_markdown_path, root),
        },
        "summary": {
            "pool_repositories": len(selected_pool),
            "comparison_repositories": comparison.get("summary", {}).get("repositories", 0),
            "covered_repositories": trend.get("summary", {}).get("covered_repositories", 0),
            "missing_repositories": trend.get("summary", {}).get("missing_repositories", 0),
            "regressed": trend.get("summary", {}).get("regressed", 0),
            "operationally_blocked": trend.get("summary", {}).get("operationally_blocked", 0),
            "operator_guided_repositories": trend.get("summary", {}).get("operator_guided_repositories", 0),
        },
        "comparison_summary": comparison.get("summary") or {},
        "trend_status": trend.get("status"),
        "recommended_follow_up": trend.get("recommended_follow_up") or [],
        "warnings": warnings,
        "sensitive_material_note": (
            "Do not include secrets, private repository contents, raw model output, "
            "or unnecessary local-only logs in benchmark coverage rehearsal evidence."
        ),
    }
    _write_json(output_json, report)
    _write_markdown(output_markdown, render_markdown(report))
    return report


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    artifacts = report.get("artifacts") if isinstance(report.get("artifacts"), dict) else {}
    lines = [
        "# Real-Repo Benchmark Coverage Rehearsal",
        "",
        f"- Label: `{report.get('label')}`",
        f"- Generated at: `{report.get('generated_at')}`",
        f"- Status: `{report.get('status')}`",
        f"- Mode: `{report.get('mode')}`",
        f"- Selected repositories: `{', '.join(report.get('selected_repo_ids') or [])}`",
        f"- Pool repositories: `{summary.get('pool_repositories', 0)}`",
        f"- Covered repositories: `{summary.get('covered_repositories', 0)}`",
        f"- Missing repositories: `{summary.get('missing_repositories', 0)}`",
        f"- Regressed: `{summary.get('regressed', 0)}`",
        f"- Operationally blocked: `{summary.get('operationally_blocked', 0)}`",
        "",
        "## Artifacts",
        "",
        "| Artifact | Path |",
        "| --- | --- |",
    ]
    for key, value in artifacts.items():
        lines.append(f"| {_markdown_cell(key)} | {_markdown_cell(value)} |")
    lines.extend(["", "## Recommended Follow-up", ""])
    for item in report.get("recommended_follow_up") or []:
        lines.append(f"- {item}")
    if report.get("warnings"):
        lines.extend(["", "## Warnings", ""])
        for warning in report["warnings"]:
            lines.append(f"- {warning}")
    lines.extend(["", "## Secret Boundary", "", f"- {report.get('sensitive_material_note')}", ""])
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rehearse fixed-pool real-repo benchmark coverage evidence.")
    parser.add_argument("--label", default="real-repo-benchmark-coverage-rehearsal")
    parser.add_argument("--generated-at")
    parser.add_argument("--pool", default=str(DEFAULT_POOL))
    parser.add_argument("--baseline-snapshot-json", default=str(DEFAULT_BASELINE))
    parser.add_argument("--current-report-json")
    parser.add_argument("--current-report-markdown")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--base-url", default="http://127.0.0.1:3001")
    parser.add_argument("--repo-id", action="append", default=[])
    parser.add_argument("--random-count", type=int)
    parser.add_argument("--random-seed", type=int, default=9)
    parser.add_argument("--artifact-prefix", help="Prefix for generated intermediate artifacts. Defaults to output JSON stem.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--output-json", default=".tmp/real-repo-benchmark-coverage-rehearsal.json")
    parser.add_argument("--output-markdown", default=".tmp/real-repo-benchmark-coverage-rehearsal.md")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    output_dir = root / args.output_dir
    try:
        report = build_rehearsal(
            root=root,
            label=args.label,
            generated_at=args.generated_at or datetime.now(UTC).isoformat(),
            pool_path=root / args.pool,
            baseline_snapshot_path=root / args.baseline_snapshot_json,
            output_dir=output_dir,
            output_json=root / args.output_json,
            output_markdown=root / args.output_markdown,
            current_report_path=(root / args.current_report_json) if args.current_report_json else None,
            current_report_markdown_path=(root / args.current_report_markdown) if args.current_report_markdown else None,
            live=args.live,
            base_url=args.base_url,
            repo_ids=args.repo_id,
            random_count=args.random_count,
            random_seed=args.random_seed,
            artifact_prefix=args.artifact_prefix,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Failed to rehearse real-repo benchmark coverage: {exc}", file=sys.stderr)
        return 1
    print(f"Real-repo benchmark coverage rehearsal JSON written to {root / args.output_json}")
    print(f"Real-repo benchmark coverage rehearsal Markdown written to {root / args.output_markdown}")
    print(f"Status: {report['status']}")
    return 1 if report["status"] == "blocking" else 0


if __name__ == "__main__":
    sys.exit(main())
