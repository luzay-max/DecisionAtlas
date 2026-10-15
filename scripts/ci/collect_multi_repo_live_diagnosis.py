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

import collect_imported_workspace_core_loop as core_loop
import rehearse_public_github_import as public_import


SCHEMA_VERSION = 1
DEFAULT_POOL = Path("examples/live-benchmarks/trend-pool.json")
PASS_STATUSES = {"pass", "passed", "ok", "continue", "clean", "created", "reused", "provided"}
WARNING_STATUSES = {
    "warning",
    "caution",
    "operator_guided",
    "not_provided",
    "evidence_limited",
    "review_required",
    "unknown",
}
BLOCKING_STATUSES = {"blocking", "blocked", "failed", "failure", "error", "pause", "provider_failure", "local_stack_failure"}


def _read_json_list(path: Path) -> list[dict[str, Any]]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, list):
        raise ValueError(f"Expected JSON list at {path}")
    return [row for row in loaded if isinstance(row, dict)]


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_markdown(path: Path, markdown: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def _status_rank(status: str) -> int:
    normalized = str(status or "unknown").lower()
    if normalized in BLOCKING_STATUSES:
        return 2
    if normalized in WARNING_STATUSES:
        return 1
    if normalized in PASS_STATUSES:
        return 0
    return 1


def _combined_status(statuses: list[str]) -> str:
    ranks = [_status_rank(status) for status in statuses]
    if any(rank >= 2 for rank in ranks):
        return "blocking"
    if any(rank == 1 for rank in ranks):
        return "warning"
    return "pass"


ACTION_CATEGORY_KEYS = ("product_controlled", "operator_setup", "external_dependency", "not_provided", "blocking")


def _empty_action_categories() -> dict[str, int]:
    return {key: 0 for key in ACTION_CATEGORY_KEYS}


def _import_action_categories(import_report: dict[str, Any]) -> dict[str, int]:
    counts = _empty_action_categories()
    setup = import_report.get("setup") if isinstance(import_report.get("setup"), dict) else {}
    setup_outcome = str(setup.get("outcome") or "unknown")
    next_action = str(setup.get("next_action") or "")
    if setup_outcome in {"provider_failure", "local_stack_failure"}:
        counts["blocking"] += 1
        counts["external_dependency"] += 1
    elif next_action == "wait_for_import" or setup.get("benchmark_ready") is False:
        counts["operator_setup"] += 1
    elif setup_outcome in {"created", "reused", "provided"}:
        pass
    else:
        counts["operator_setup"] += 1
    return counts


def _merge_action_categories(*items: dict[str, int]) -> dict[str, int]:
    merged = _empty_action_categories()
    for item in items:
        for key in ACTION_CATEGORY_KEYS:
            merged[key] += int(item.get(key) or 0)
    return merged


def select_repo_ids(pool: list[dict[str, Any]], *, repo_ids: list[str], random_count: int | None, random_seed: int) -> list[str]:
    available = [str(row["id"]) for row in pool if row.get("id")]
    if repo_ids:
        unknown = sorted(set(repo_ids) - set(available))
        if unknown:
            raise ValueError(f"Unknown repository id(s): {', '.join(unknown)}")
        selected = repo_ids
    else:
        selected = available
    if random_count is None:
        return selected
    if random_count < 1:
        raise ValueError("--random-count must be greater than zero.")
    if random_count > len(selected):
        raise ValueError("--random-count cannot exceed selected repository count.")
    sampler = random.Random(random_seed)
    return sorted(sampler.sample(selected, random_count))


def _repository_by_id(pool: list[dict[str, Any]], repo_id: str) -> dict[str, Any]:
    for row in pool:
        if row.get("id") == repo_id:
            return row
    raise ValueError(f"Unknown repository id: {repo_id}")


def _core_loop_input_from_import(import_report: dict[str, Any]) -> tuple[str | None, str | None]:
    repository = import_report.get("repository") if isinstance(import_report.get("repository"), dict) else {}
    return repository.get("repo"), repository.get("workspace_slug")


def diagnose_repository(
    *,
    root: Path,
    repository: dict[str, Any],
    base_url: str,
    session_token: str | None,
    wait_import: bool,
    timeout_seconds: int,
    poll_seconds: float,
    guardrail_json: Path | None,
    run_guardrail: bool,
    why_question: str,
    evaluate_drift: bool,
) -> dict[str, Any]:
    import_report = public_import.rehearse_public_import(
        repository=repository,
        base_url=base_url,
        session_token=session_token,
        wait=wait_import,
        timeout_seconds=timeout_seconds,
        poll_seconds=poll_seconds,
    )
    repo, workspace_slug = _core_loop_input_from_import(import_report)
    setup_outcome = str((import_report.get("setup") or {}).get("outcome") or "unknown")
    core_report = core_loop.build_report(
        root=root,
        base_url=base_url,
        repo=repo or repository.get("repo"),
        workspace_slug=workspace_slug,
        import_rehearsal_json=None,
        guardrail_json=guardrail_json,
        run_guardrail=run_guardrail,
        session_token=session_token,
        why_question=why_question,
        evaluate_drift=evaluate_drift,
    )
    lane_statuses = {
        name: lane.get("status")
        for name, lane in (core_report.get("lanes") or {}).items()
        if isinstance(lane, dict)
    }
    core_summary = core_report.get("summary") if isinstance(core_report.get("summary"), dict) else {}
    lane_reasons = core_report.get("lane_reasons") if isinstance(core_report.get("lane_reasons"), dict) else {}
    grounding_summary = core_summary.get("grounding_summary") if isinstance(core_summary.get("grounding_summary"), dict) else {}
    accepted_baseline = (
        core_report.get("accepted_baseline")
        if isinstance(core_report.get("accepted_baseline"), dict)
        else core_summary.get("accepted_baseline")
        if isinstance(core_summary.get("accepted_baseline"), dict)
        else {}
    )
    core_action_categories = (
        core_summary.get("action_categories")
        if isinstance(core_summary.get("action_categories"), dict)
        else _empty_action_categories()
    )
    action_categories = _merge_action_categories(_import_action_categories(import_report), core_action_categories)
    status = _combined_status([setup_outcome, str(core_report.get("status") or "unknown")])
    return {
        "id": repository.get("id"),
        "repo": repository.get("repo"),
        "workspace_slug": workspace_slug,
        "priority": repository.get("priority"),
        "operator_setup_status": repository.get("operator_setup_status"),
        "status": status,
        "setup_outcome": setup_outcome,
        "core_loop_status": core_report.get("status"),
        "lane_statuses": lane_statuses,
        "lane_reasons": lane_reasons,
        "grounding_summary": grounding_summary,
        "accepted_baseline": accepted_baseline,
        "action_categories": action_categories,
        "recommended_next_actions": sorted(
            set((core_report.get("recommended_next_actions") or []) + [(import_report.get("setup") or {}).get("next_action")])
            - {None, ""}
        ),
        "import_rehearsal": {
            "setup": import_report.get("setup"),
            "error": import_report.get("error"),
        },
        "core_loop_summary": core_summary,
    }


def build_report(
    *,
    root: Path,
    pool_path: Path,
    base_url: str,
    repo_ids: list[str],
    random_count: int | None,
    random_seed: int,
    session_token: str | None = None,
    wait_import: bool = False,
    timeout_seconds: int = 900,
    poll_seconds: float = 5.0,
    guardrail_json: Path | None = None,
    run_guardrail: bool = False,
    why_question: str = "why is this repository architected this way",
    evaluate_drift: bool = False,
    generated_at: str | None = None,
) -> dict[str, Any]:
    pool = _read_json_list(pool_path)
    selected_ids = select_repo_ids(pool, repo_ids=repo_ids, random_count=random_count, random_seed=random_seed)
    repositories = [_repository_by_id(pool, repo_id) for repo_id in selected_ids]
    results = [
        diagnose_repository(
            root=root,
            repository=repository,
            base_url=base_url,
            session_token=session_token,
            wait_import=wait_import,
            timeout_seconds=timeout_seconds,
            poll_seconds=poll_seconds,
            guardrail_json=guardrail_json,
            run_guardrail=run_guardrail,
            why_question=why_question,
            evaluate_drift=evaluate_drift,
        )
        for repository in repositories
    ]
    status = _combined_status([str(row.get("status") or "unknown") for row in results])
    summary = {
        "selected_repositories": len(results),
        "pass": sum(1 for row in results if _status_rank(str(row.get("status"))) == 0),
        "warning": sum(1 for row in results if _status_rank(str(row.get("status"))) == 1),
        "blocking": sum(1 for row in results if _status_rank(str(row.get("status"))) >= 2),
        "operator_guided": sum(
            1
            for row in results
            if "operator_guided" in {str(value) for value in [row.get("setup_outcome"), *(row.get("lane_statuses") or {}).values()]}
        ),
        "action_categories": _merge_action_categories(
            *[
                row.get("action_categories") if isinstance(row.get("action_categories"), dict) else _empty_action_categories()
                for row in results
            ]
        ),
        "grounding_reason_codes": sorted(
            {
                str(code)
                for row in results
                for code in (
                    ((row.get("grounding_summary") or {}).get("reason_codes") or [])
                    if isinstance(row.get("grounding_summary"), dict)
                    else []
                )
                if code
            }
        ),
        "accepted_baseline_statuses": sorted(
            {
                str((row.get("accepted_baseline") or {}).get("status"))
                for row in results
                if isinstance(row.get("accepted_baseline"), dict) and (row.get("accepted_baseline") or {}).get("status")
            }
        ),
    }
    recommended_follow_up = sorted(
        {
            action
            for row in results
            for action in (row.get("recommended_next_actions") or [])
            if action
        }
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at or datetime.now(UTC).isoformat(),
        "evidence_type": "multi-repo-live-diagnosis-rotation",
        "status": status,
        "base_url": base_url,
        "selected_repo_ids": selected_ids,
        "random_selection": {"enabled": random_count is not None, "count": random_count, "seed": random_seed},
        "summary": summary,
        "repositories": results,
        "recommended_follow_up": recommended_follow_up,
        "sensitive_material_note": "This diagnosis stores compact statuses/counts only. Do not include tokens, raw private source, or raw model output.",
    }


def _markdown_cell(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value).replace("|", "\\|").replace("\n", "<br>") or "-"


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    action_summary = summary.get("action_categories") if isinstance(summary.get("action_categories"), dict) else {}
    lines = [
        "# Multi-Repo Live Diagnosis Rotation",
        "",
        f"- Generated at: `{report.get('generated_at')}`",
        f"- Status: `{report.get('status')}`",
        f"- Base URL: `{report.get('base_url')}`",
        f"- Selected repositories: `{', '.join(report.get('selected_repo_ids') or [])}`",
        f"- Pass: `{summary.get('pass', 0)}`",
        f"- Warning: `{summary.get('warning', 0)}`",
        f"- Blocking: `{summary.get('blocking', 0)}`",
        f"- Product actions: `{action_summary.get('product_controlled', 0)}`",
        f"- Operator/setup actions: `{action_summary.get('operator_setup', 0)}`",
        "",
        "## Repository Results",
        "",
        "| Repo | Status | Setup | Core loop | Accepted baseline | Review | Why | Drift | Guardrail | Grounding | Product actions | Operator/setup actions |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in report.get("repositories") or []:
        lanes = row.get("lane_statuses") if isinstance(row.get("lane_statuses"), dict) else {}
        categories = row.get("action_categories") if isinstance(row.get("action_categories"), dict) else {}
        lines.append(
            "| "
            + " | ".join(
                [
                    _markdown_cell(row.get("repo")),
                    _markdown_cell(row.get("status")),
                    _markdown_cell(row.get("setup_outcome")),
                    _markdown_cell(row.get("core_loop_status")),
                    _markdown_cell(row.get("accepted_baseline")),
                    _markdown_cell(lanes.get("review")),
                    _markdown_cell(lanes.get("why_search")),
                    _markdown_cell(lanes.get("drift")),
                    _markdown_cell(lanes.get("guardrail")),
                    _markdown_cell(row.get("grounding_summary")),
                    _markdown_cell(categories.get("product_controlled", 0)),
                    _markdown_cell(categories.get("operator_setup", 0)),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Recommended Follow-up", ""])
    for action in report.get("recommended_follow_up") or []:
        lines.append(f"- `{action}`")
    lines.extend(["", "## Evidence Boundary", "", f"- {report.get('sensitive_material_note')}", ""])
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect multi-repo live diagnosis rotation evidence.")
    parser.add_argument("--pool", default=str(DEFAULT_POOL))
    parser.add_argument("--base-url", default="http://127.0.0.1:3001")
    parser.add_argument("--repo-id", action="append", default=[])
    parser.add_argument("--random-count", type=int)
    parser.add_argument("--random-seed", type=int, default=13)
    parser.add_argument("--session-token")
    parser.add_argument("--wait-import", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=900)
    parser.add_argument("--poll-seconds", type=float, default=5.0)
    parser.add_argument("--guardrail-json")
    parser.add_argument("--run-guardrail", action="store_true")
    parser.add_argument("--why-question", default="why is this repository architected this way")
    parser.add_argument("--evaluate-drift", action="store_true")
    parser.add_argument("--generated-at")
    parser.add_argument("--output-json", default=".tmp/multi-repo-live-diagnosis.json")
    parser.add_argument("--output-markdown", default=".tmp/multi-repo-live-diagnosis.md")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    try:
        report = build_report(
            root=root,
            pool_path=root / args.pool,
            base_url=args.base_url,
            repo_ids=args.repo_id,
            random_count=args.random_count,
            random_seed=args.random_seed,
            session_token=args.session_token,
            wait_import=args.wait_import,
            timeout_seconds=args.timeout_seconds,
            poll_seconds=args.poll_seconds,
            guardrail_json=(root / args.guardrail_json) if args.guardrail_json else None,
            run_guardrail=args.run_guardrail,
            why_question=args.why_question,
            evaluate_drift=args.evaluate_drift,
            generated_at=args.generated_at,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Failed to collect multi-repo diagnosis: {exc}", file=sys.stderr)
        return 1
    _write_json(root / args.output_json, report)
    _write_markdown(root / args.output_markdown, render_markdown(report))
    print(f"Multi-repo diagnosis JSON written to {root / args.output_json}")
    print(f"Multi-repo diagnosis Markdown written to {root / args.output_markdown}")
    print(f"Status: {report['status']}")
    return 1 if report["status"] == "blocking" else 0


if __name__ == "__main__":
    raise SystemExit(main())
