from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
from pathlib import Path
import sys
from typing import Any


SCHEMA_VERSION = 1
DEFAULT_POOL = Path("examples/live-benchmarks/trend-pool.json")
DEFAULT_OUTPUT_JSON = Path(".tmp/real-repo-benchmark-trend.json")
DEFAULT_OUTPUT_MARKDOWN = Path(".tmp/real-repo-benchmark-trend.md")
NON_CLEAN_MOVEMENTS = {"regressed", "operationally-blocked", "missing-from-current", "needs-review"}
WARNING_MOVEMENTS = NON_CLEAN_MOVEMENTS | {"missing-from-pool"}
REQUIRED_POOL_FIELDS = {
    "id",
    "repo",
    "workspace_slug",
    "release_role",
    "benchmark_purpose",
    "priority",
    "operator_setup_status",
}


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_markdown(path: Path, markdown: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def _markdown_cell(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, list):
        text = ", ".join(str(item) for item in value)
    elif isinstance(value, dict):
        text = json.dumps(value, sort_keys=True, ensure_ascii=False)
    else:
        text = str(value)
    return text.replace("|", "\\|").replace("\n", "<br>") or "-"


def load_pool(path: Path) -> list[dict[str, Any]]:
    loaded = _read_json(path)
    if not isinstance(loaded, list):
        raise ValueError(f"Expected repository trend pool list at {path}")
    return loaded


def validate_pool(pool: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    if not pool:
        return ["trend_pool_empty"]
    for index, row in enumerate(pool, start=1):
        if not isinstance(row, dict):
            errors.append(f"entry_{index}_not_object")
            continue
        missing = sorted(REQUIRED_POOL_FIELDS - set(row))
        if missing:
            errors.append(f"{row.get('id') or f'entry_{index}'}:missing_fields:{','.join(missing)}")
        repo_id = str(row.get("id") or "").strip()
        repo = str(row.get("repo") or "").strip()
        workspace_slug = str(row.get("workspace_slug") or "").strip()
        if not repo_id:
            errors.append(f"entry_{index}:missing_id")
        elif repo_id in seen:
            errors.append(f"{repo_id}:duplicate_id")
        seen.add(repo_id)
        if "/" not in repo:
            errors.append(f"{repo_id or f'entry_{index}'}:invalid_repo")
        if not workspace_slug.startswith("github-"):
            errors.append(f"{repo_id or f'entry_{index}'}:invalid_workspace_slug")
        if str(row.get("operator_setup_status") or "").strip() not in {"ready", "operator_guided", "not_provided"}:
            errors.append(f"{repo_id or f'entry_{index}'}:invalid_operator_setup_status")
    return errors


def _comparison_by_id(comparison: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not comparison:
        return {}
    rows = comparison.get("repositories") if isinstance(comparison.get("repositories"), list) else []
    return {str(row.get("id")): row for row in rows if isinstance(row, dict) and row.get("id")}


def _movement_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        movement = str(row.get("movement") or "unknown")
        counts[movement] = counts.get(movement, 0) + 1
    return dict(sorted(counts.items()))


def _bounded_reasons(row: dict[str, Any] | None) -> list[str]:
    if not row:
        return []
    reasons = row.get("reasons") if isinstance(row.get("reasons"), list) else []
    return [str(reason)[:240] for reason in reasons[:5]]


def _trend_status(*, pool_errors: list[str], comparison_provided: bool, rows: list[dict[str, Any]]) -> str:
    if pool_errors:
        return "blocking"
    if not comparison_provided:
        return "warning"
    if any(str(row.get("movement") or "") in WARNING_MOVEMENTS for row in rows):
        return "warning"
    return "pass"


def recommended_follow_up(*, summary: dict[str, Any], pool_errors: list[str], comparison_provided: bool) -> list[str]:
    if pool_errors:
        return ["Fix trend pool schema errors before using benchmark trend evidence."]
    follow_up: list[str] = []
    if not comparison_provided:
        follow_up.append("Generate or attach benchmark comparison evidence before claiming fixed-pool trend coverage.")
    if summary.get("missing_repositories"):
        follow_up.append("Run or attach benchmark comparison rows for missing fixed-pool repositories.")
    if summary.get("regressed"):
        follow_up.append("Investigate regressed repositories before claiming release quality improvement.")
    if summary.get("operationally_blocked"):
        follow_up.append("Resolve operationally-blocked repositories or document operator acceptance.")
    if summary.get("operator_guided_repositories"):
        follow_up.append("Review operator-guided repository setup status during release rehearsal.")
    if not follow_up:
        follow_up.append("Fixed-pool benchmark trend evidence is clean for the supplied comparison.")
    return follow_up


def build_trend(
    *,
    pool: list[dict[str, Any]],
    comparison: dict[str, Any] | None,
    generated_at: str,
    label: str,
    commit: str | None = None,
    version_label: str | None = None,
) -> dict[str, Any]:
    pool_errors = validate_pool(pool)
    comparison_rows = _comparison_by_id(comparison)
    comparison_provided = comparison is not None
    rows: list[dict[str, Any]] = []

    for repo in pool:
        repo_id = str(repo.get("id"))
        comparison_row = comparison_rows.get(repo_id)
        if comparison_row:
            movement = str(comparison_row.get("movement") or "needs-review")
            coverage_status = "covered"
        elif comparison_provided:
            movement = "missing-from-pool"
            coverage_status = "missing_from_current_pool"
        else:
            movement = "not_provided"
            coverage_status = "not_provided"

        rows.append(
            {
                "id": repo_id,
                "repo": repo.get("repo"),
                "workspace_slug": repo.get("workspace_slug"),
                "release_role": repo.get("release_role"),
                "benchmark_purpose": repo.get("benchmark_purpose"),
                "priority": repo.get("priority"),
                "operator_setup_status": repo.get("operator_setup_status"),
                "coverage_status": coverage_status,
                "movement": movement,
                "current_value_outcome": comparison_row.get("current_value_outcome") if comparison_row else None,
                "baseline_value_outcome": comparison_row.get("baseline_value_outcome") if comparison_row else None,
                "current_bounded_outcome": comparison_row.get("current_bounded_outcome") if comparison_row else None,
                "baseline_bounded_outcome": comparison_row.get("baseline_bounded_outcome") if comparison_row else None,
                "reasons": _bounded_reasons(comparison_row),
            }
        )

    extra_ids = sorted(set(comparison_rows) - {str(repo.get("id")) for repo in pool})
    covered = sum(1 for row in rows if row["coverage_status"] == "covered")
    missing = sum(1 for row in rows if row["coverage_status"] == "missing_from_current_pool")
    not_provided = sum(1 for row in rows if row["coverage_status"] == "not_provided")
    operator_guided = sum(1 for row in rows if row.get("operator_setup_status") == "operator_guided")
    movement_counts = _movement_counts(rows)
    summary = {
        "repositories": len(pool),
        "covered_repositories": covered,
        "missing_repositories": missing,
        "not_provided_repositories": not_provided,
        "operator_guided_repositories": operator_guided,
        "extra_comparison_repositories": len(extra_ids),
        "movements": movement_counts,
        "regressed": movement_counts.get("regressed", 0),
        "improved": movement_counts.get("improved", 0),
        "operationally_blocked": movement_counts.get("operationally-blocked", 0),
        "missing_from_current": movement_counts.get("missing-from-current", 0) + movement_counts.get("missing-from-pool", 0),
        "release_evidence_ready": comparison_provided and not pool_errors,
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "label": label,
        "commit": commit,
        "version_label": version_label,
        "status": _trend_status(pool_errors=pool_errors, comparison_provided=comparison_provided, rows=rows),
        "comparison_source": {
            "provided": comparison_provided,
            "generated_at": comparison.get("generated_at") if comparison else None,
            "comparison_type": comparison.get("comparison_type") if comparison else None,
            "baseline_generated_at": comparison.get("baseline_generated_at") if comparison else None,
            "current_generated_at": comparison.get("current_generated_at") if comparison else None,
        },
        "summary": summary,
        "pool_errors": pool_errors,
        "extra_comparison_repository_ids": extra_ids,
        "repositories": rows,
        "recommended_follow_up": recommended_follow_up(
            summary=summary,
            pool_errors=pool_errors,
            comparison_provided=comparison_provided,
        ),
        "sensitive_material_note": (
            "Do not include secrets, private repository contents, raw model output, "
            "or unnecessary local-only logs in benchmark trend evidence."
        ),
    }


def render_markdown(trend: dict[str, Any]) -> str:
    summary = trend.get("summary") if isinstance(trend.get("summary"), dict) else {}
    lines = [
        "# Real-Repository Benchmark Trend Evidence",
        "",
        f"- Label: `{trend.get('label')}`",
        f"- Generated at: `{trend.get('generated_at')}`",
        f"- Version: `{trend.get('version_label') or '-'}`",
        f"- Commit: `{trend.get('commit') or '-'}`",
        f"- Status: `{trend.get('status')}`",
        f"- Comparison provided: `{(trend.get('comparison_source') or {}).get('provided')}`",
        f"- Repositories: `{summary.get('repositories', 0)}`",
        f"- Covered repositories: `{summary.get('covered_repositories', 0)}`",
        f"- Missing repositories: `{summary.get('missing_repositories', 0)}`",
        f"- Regressed: `{summary.get('regressed', 0)}`",
        f"- Operationally blocked: `{summary.get('operationally_blocked', 0)}`",
        "",
        "## Repository Trend Pool",
        "",
        "| Repository | Priority | Setup | Coverage | Movement | Value outcome | Bounded outcome | Reasons |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in trend.get("repositories") or []:
        value_outcome = (
            f"{row.get('baseline_value_outcome')} -> {row.get('current_value_outcome')}"
            if row.get("baseline_value_outcome") or row.get("current_value_outcome")
            else "-"
        )
        bounded_outcome = (
            f"{row.get('baseline_bounded_outcome')} -> {row.get('current_bounded_outcome')}"
            if row.get("baseline_bounded_outcome") or row.get("current_bounded_outcome")
            else "-"
        )
        lines.append(
            "| "
            + " | ".join(
                _markdown_cell(value)
                for value in (
                    row.get("repo") or row.get("id"),
                    row.get("priority"),
                    row.get("operator_setup_status"),
                    row.get("coverage_status"),
                    row.get("movement"),
                    value_outcome,
                    bounded_outcome,
                    row.get("reasons") or [],
                )
            )
            + " |"
        )
    lines.extend(["", "## Movement Counts", ""])
    for movement, count in (summary.get("movements") or {}).items():
        lines.append(f"- {movement}: `{count}`")
    lines.extend(["", "## Recommended Follow-up", ""])
    for item in trend.get("recommended_follow_up") or []:
        lines.append(f"- {item}")
    lines.extend(["", "## Secret Boundary", "", f"- {trend.get('sensitive_material_note')}", ""])
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate fixed-pool real-repo benchmark trend evidence.")
    parser.add_argument("--pool", default=str(DEFAULT_POOL))
    parser.add_argument("--comparison-json")
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-markdown", default=str(DEFAULT_OUTPUT_MARKDOWN))
    parser.add_argument("--generated-at")
    parser.add_argument("--label", default="real-repo-benchmark-trend")
    parser.add_argument("--commit")
    parser.add_argument("--version-label")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    pool_path = root / args.pool
    comparison_path = root / args.comparison_json if args.comparison_json else None
    try:
        pool = load_pool(pool_path)
        comparison = _read_json(comparison_path) if comparison_path else None
        if comparison is not None and not isinstance(comparison, dict):
            raise ValueError(f"Expected comparison JSON object at {comparison_path}")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Failed to build benchmark trend evidence: {exc}", file=sys.stderr)
        return 1
    trend = build_trend(
        pool=pool,
        comparison=comparison,
        generated_at=args.generated_at or datetime.now(UTC).isoformat(),
        label=args.label,
        commit=args.commit,
        version_label=args.version_label,
    )
    output_json = root / args.output_json
    output_markdown = root / args.output_markdown
    _write_json(output_json, trend)
    _write_markdown(output_markdown, render_markdown(trend))
    print(f"Real-repo benchmark trend JSON written to {output_json}")
    print(f"Real-repo benchmark trend Markdown written to {output_markdown}")
    print(f"Status: {trend['status']}")
    return 1 if trend["status"] == "blocking" else 0


if __name__ == "__main__":
    sys.exit(main())
