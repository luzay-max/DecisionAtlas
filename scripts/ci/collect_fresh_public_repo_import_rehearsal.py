from __future__ import annotations

import argparse
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import random
import re
import secrets
import sys
from typing import Any
from urllib.parse import urlencode


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.ci import collect_imported_workspace_core_loop as core_loop
from scripts.ci import rehearse_public_github_import as public_import


SCHEMA_VERSION = 1
MAX_CANDIDATES = 50
STATUS_RANK = {"pass": 0, "warning": 1, "blocking": 2}


def _slug_part(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _candidate_from_repo(repo: str) -> dict[str, Any]:
    normalized = repo.strip().strip("/")
    parts = normalized.split("/")
    if len(parts) != 2 or not all(parts):
        raise ValueError(f"Invalid GitHub repository identity: {repo!r}")
    owner, name = parts
    return {
        "id": f"{_slug_part(owner)}-{_slug_part(name)}",
        "repo": f"{owner}/{name}",
        "workspace_slug": f"github-{_slug_part(owner)}-{_slug_part(name)}",
        "role": "fresh_public_rehearsal_candidate",
        "benchmark_purpose": "Prove a fresh public GitHub import and governed core loop.",
    }


def normalize_candidates(rows: list[Any], *, max_candidates: int = MAX_CANDIDATES) -> list[dict[str, Any]]:
    if max_candidates < 1 or max_candidates > MAX_CANDIDATES:
        raise ValueError(f"max_candidates must be between 1 and {MAX_CANDIDATES}")
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        candidate = _candidate_from_repo(row) if isinstance(row, str) else dict(row) if isinstance(row, dict) else None
        if not candidate or not candidate.get("repo"):
            raise ValueError("Every candidate must be a repository string or object containing repo")
        base = _candidate_from_repo(str(candidate["repo"]))
        merged = {**base, **{key: value for key, value in candidate.items() if value is not None}}
        repo_key = str(merged["repo"]).lower()
        if repo_key in seen:
            continue
        seen.add(repo_key)
        normalized.append(merged)
        if len(normalized) >= max_candidates:
            break
    if not normalized:
        raise ValueError("At least one public GitHub repository candidate is required")
    return normalized


def load_candidates(path: Path | None, inline_repositories: list[str], *, max_candidates: int) -> list[dict[str, Any]]:
    rows: list[Any] = []
    if path is not None:
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(loaded, list):
            raise ValueError(f"Expected a JSON list at {path}")
        rows.extend(loaded)
    rows.extend(inline_repositories)
    return normalize_candidates(rows, max_candidates=max_candidates)


def candidate_pool_digest(candidates: list[dict[str, Any]]) -> str:
    identities = sorted(str(candidate["repo"]).lower() for candidate in candidates)
    return hashlib.sha256("\n".join(identities).encode("utf-8")).hexdigest()


def seeded_candidate_order(candidates: list[dict[str, Any]], seed: str) -> list[dict[str, Any]]:
    ordered = [dict(candidate) for candidate in candidates]
    random.Random(seed).shuffle(ordered)
    return ordered


def select_fresh_candidate(
    *,
    candidates: list[dict[str, Any]],
    seed: str,
    base_url: str,
    session_token: str | None,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    considered: list[dict[str, Any]] = []
    for candidate in seeded_candidate_order(candidates, seed):
        query = urlencode({"repo": candidate["repo"]})
        lookup, lookup_error = public_import._json_request(
            base_url=base_url,
            path=f"/imports/lookup?{query}",
            session_token=session_token,
            timeout=30,
        )
        if lookup_error is not None or lookup is None:
            considered.append(
                {
                    "repo": candidate["repo"],
                    "outcome": "lookup_failed",
                    "classification": public_import._classify_request_error(lookup_error),
                    "error": lookup_error,
                }
            )
            continue
        if lookup.get("workspace_exists"):
            considered.append(
                {
                    "repo": candidate["repo"],
                    "workspace_slug": lookup.get("workspace_slug"),
                    "outcome": "reused_not_eligible",
                    "lookup": lookup,
                }
            )
            continue
        if lookup.get("access_requirement"):
            considered.append(
                {
                    "repo": candidate["repo"],
                    "outcome": "access_not_eligible",
                    "classification": "operator_guided",
                    "lookup": lookup,
                }
            )
            continue
        considered.append({"repo": candidate["repo"], "outcome": "selected_fresh", "lookup": lookup})
        return candidate, considered
    return None, considered


def _overall_status(import_lane: dict[str, Any], core_loop_report: dict[str, Any] | None, browser: dict[str, Any]) -> str:
    statuses = [str(import_lane.get("status") or "warning"), str(browser.get("status") or "not_provided")]
    if core_loop_report:
        statuses.append(str(core_loop_report.get("status") or "warning"))
    ranks = [STATUS_RANK.get("warning" if status in {"not_provided", "operator_guided"} else status, 1) for status in statuses]
    rank = max(ranks, default=1)
    return "blocking" if rank >= 2 else "warning" if rank == 1 else "pass"


def _next_actions(
    *,
    selected: dict[str, Any] | None,
    import_lane: dict[str, Any],
    core_loop_report: dict[str, Any] | None,
    browser: dict[str, Any],
) -> list[str]:
    actions: set[str] = set()
    if selected is None:
        actions.add("supply_unseen_public_repository_candidates")
    if import_lane.get("outcome") != "fresh_import":
        actions.add(str(import_lane.get("next_action") or "inspect_fresh_import_evidence"))
    if core_loop_report:
        actions.update(str(value) for value in core_loop_report.get("recommended_next_actions") or [] if value)
        baseline = core_loop_report.get("accepted_baseline") or {}
        if int(baseline.get("accepted_count") or 0) == 0 and int(baseline.get("candidate_count") or 0) > 0:
            actions.add("review_candidates_before_accepted_baseline_claim")
    if browser.get("status") != "pass":
        actions.add("run_human_browser_rehearsal_for_fresh_workspace")
    return sorted(actions)


def collect_rehearsal(
    *,
    root: Path,
    candidates: list[dict[str, Any]],
    seed: str,
    base_url: str,
    session_token: str | None,
    timeout_seconds: int,
    poll_seconds: float,
    why_question: str,
    evaluate_drift: bool,
    run_guardrail: bool,
    browser_status: str,
    browser_summary: str | None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    selected, considered = select_fresh_candidate(
        candidates=candidates,
        seed=seed,
        base_url=base_url,
        session_token=session_token,
    )
    import_report: dict[str, Any] | None = None
    core_loop_report: dict[str, Any] | None = None
    if selected is None:
        import_lane = {
            "status": "warning",
            "outcome": "no_fresh_candidate",
            "next_action": "supply_unseen_public_repository_candidates",
            "summary": "No candidate had owner-scoped no-workspace proof.",
        }
    else:
        import_report = public_import.rehearse_public_import(
            repository=selected,
            base_url=base_url,
            session_token=session_token,
            wait=True,
            timeout_seconds=timeout_seconds,
            poll_seconds=poll_seconds,
        )
        setup = import_report.get("setup") or {}
        import_job = import_report.get("import_job") or {}
        if setup.get("outcome") == "created" and import_job.get("status") == "succeeded":
            import_lane = {
                "status": "pass",
                "outcome": "fresh_import",
                "next_action": "probe_fresh_workspace_core_loop",
                "summary": "No-workspace preflight was followed by a successful full import.",
            }
            repository = import_report.get("repository") or {}
            core_loop_report = core_loop.build_report(
                root=root,
                base_url=base_url,
                repo=str(repository.get("repo") or selected["repo"]),
                workspace_slug=str(repository.get("workspace_slug") or import_job.get("workspace_slug")),
                import_rehearsal_json=None,
                guardrail_json=None,
                run_guardrail=run_guardrail,
                session_token=session_token,
                why_question=why_question,
                evaluate_drift=evaluate_drift,
                generated_at=generated_at,
            )
        elif setup.get("outcome") == "reused":
            import_lane = {
                "status": "warning",
                "outcome": "reuse_race",
                "next_action": "select_another_fresh_repository",
                "summary": "Repository became reusable after preflight; it is not fresh-import proof.",
            }
        else:
            import_lane = {
                "status": "warning",
                "outcome": str(setup.get("outcome") or "import_incomplete"),
                "next_action": str(setup.get("next_action") or "inspect_import_failure"),
                "summary": "Fresh import did not reach a successful terminal state.",
            }
    browser = {
        "status": browser_status,
        "summary": browser_summary or "Human browser rehearsal has not been attached.",
    }
    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at or datetime.now(UTC).isoformat(),
        "evidence_type": "fresh-public-repo-import-rehearsal",
        "status": _overall_status(import_lane, core_loop_report, browser),
        "base_url": base_url,
        "selection": {
            "mode": "seeded_candidate_pool",
            "seed": seed,
            "candidate_pool_digest": candidate_pool_digest(candidates),
            "candidate_count": len(candidates),
            "selected_repository": selected.get("repo") if selected else None,
            "considered": considered,
        },
        "fresh_import": import_lane,
        "import_rehearsal": import_report,
        "core_loop": core_loop_report,
        "browser": browser,
        "limitations": [
            "A seeded bounded pool is random and reproducible but is not an unbounded sample of GitHub.",
            "GitHub and the real local stack are external runtime dependencies.",
            "A successful import can still yield evidence-limited decision quality.",
            "Evidence excludes credentials, raw private source, raw model output, and unbounded logs.",
        ],
    }
    report["recommended_next_actions"] = _next_actions(
        selected=selected,
        import_lane=import_lane,
        core_loop_report=core_loop_report,
        browser=browser,
    )
    report["summary"] = {
        "fresh_import": import_lane.get("outcome") == "fresh_import",
        "selected_repository": report["selection"]["selected_repository"],
        "workspace_slug": ((import_report or {}).get("repository") or {}).get("workspace_slug"),
        "imported_count": ((import_report or {}).get("import_job") or {}).get("imported_count"),
        "core_loop_status": (core_loop_report or {}).get("status"),
        "browser_status": browser_status,
    }
    return report


def attach_browser_evidence(report: dict[str, Any], *, status: str, summary: str, generated_at: str | None = None) -> dict[str, Any]:
    if report.get("evidence_type") != "fresh-public-repo-import-rehearsal":
        raise ValueError("Browser evidence can only be attached to fresh public repo rehearsal evidence")
    updated = json.loads(json.dumps(report))
    updated["browser"] = {"status": status, "summary": summary}
    updated["generated_at"] = generated_at or datetime.now(UTC).isoformat()
    updated["status"] = _overall_status(updated.get("fresh_import") or {}, updated.get("core_loop"), updated["browser"])
    selection = updated.get("selection") or {}
    selected = {"repo": selection.get("selected_repository")} if selection.get("selected_repository") else None
    updated["recommended_next_actions"] = _next_actions(
        selected=selected,
        import_lane=updated.get("fresh_import") or {},
        core_loop_report=updated.get("core_loop"),
        browser=updated["browser"],
    )
    summary_payload = updated.get("summary") if isinstance(updated.get("summary"), dict) else {}
    summary_payload["browser_status"] = status
    updated["summary"] = summary_payload
    return updated


def render_markdown(report: dict[str, Any]) -> str:
    selection = report.get("selection") or {}
    fresh_import = report.get("fresh_import") or {}
    import_job = ((report.get("import_rehearsal") or {}).get("import_job") or {})
    core_report = report.get("core_loop") or {}
    browser = report.get("browser") or {}
    lines = [
        "# Fresh Public Repository Import Rehearsal",
        "",
        f"- Generated at: `{report.get('generated_at')}`",
        f"- Status: `{report.get('status')}`",
        f"- Selection mode: `{selection.get('mode')}`",
        f"- Seed: `{selection.get('seed')}`",
        f"- Candidate pool digest: `{selection.get('candidate_pool_digest')}`",
        f"- Selected repository: `{selection.get('selected_repository') or '-'}`",
        f"- Fresh import outcome: `{fresh_import.get('outcome')}`",
        f"- Workspace slug: `{(report.get('summary') or {}).get('workspace_slug') or '-'}`",
        f"- Import job: `{import_job.get('job_id') or '-'}`",
        f"- Imported count: `{import_job.get('imported_count') if import_job else '-'}`",
        f"- Core-loop status: `{core_report.get('status') or '-'}`",
        f"- Browser status: `{browser.get('status') or '-'}`",
        "",
        "## Candidate Preflight",
        "",
        "| Repository | Outcome | Classification | Workspace |",
        "| --- | --- | --- | --- |",
    ]
    for row in selection.get("considered") or []:
        lines.append(
            f"| {row.get('repo', '-')} | {row.get('outcome', '-')} | {row.get('classification', '-')} | {row.get('workspace_slug') or ((row.get('lookup') or {}).get('workspace_slug')) or '-'} |"
        )
    lines.extend(
        [
            "",
            "## Browser Evidence",
            "",
            f"- {browser.get('summary')}",
            "",
            "## Limitations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report.get("limitations") or [])
    lines.extend(["", "## Recommended Next Actions", ""])
    lines.extend(f"- `{item}`" for item in report.get("recommended_next_actions") or [])
    lines.append("")
    return "\n".join(lines)


def _write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(report), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect proof of a fresh random public GitHub repository import.")
    parser.add_argument("--candidates-json", default="examples/live-benchmarks/fresh-repositories.json")
    parser.add_argument("--candidate-repo", action="append", default=[])
    parser.add_argument("--max-candidates", type=int, default=20)
    parser.add_argument("--seed")
    parser.add_argument("--base-url", default="http://127.0.0.1:3001")
    parser.add_argument("--session-token")
    parser.add_argument("--timeout-seconds", type=int, default=1200)
    parser.add_argument("--poll-seconds", type=float, default=5.0)
    parser.add_argument("--why-question", default="What important implementation decision was made and why?")
    parser.add_argument("--evaluate-drift", action="store_true")
    parser.add_argument("--run-guardrail", action="store_true")
    parser.add_argument("--browser-status", default="not_provided", choices=["pass", "warning", "blocking", "not_provided", "operator_guided"])
    parser.add_argument("--browser-summary")
    parser.add_argument("--augment-evidence-json")
    parser.add_argument("--generated-at")
    parser.add_argument("--output-json", default=".tmp/fresh-public-repo-import-rehearsal.json")
    parser.add_argument("--output-markdown", default=".tmp/fresh-public-repo-import-rehearsal.md")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.augment_evidence_json:
            existing = json.loads((ROOT / args.augment_evidence_json).read_text(encoding="utf-8"))
            if not args.browser_summary:
                raise ValueError("--browser-summary is required when augmenting browser evidence")
            report = attach_browser_evidence(
                existing,
                status=args.browser_status,
                summary=args.browser_summary,
                generated_at=args.generated_at,
            )
        else:
            candidate_path = (ROOT / args.candidates_json) if args.candidates_json else None
            candidates = load_candidates(candidate_path, args.candidate_repo, max_candidates=args.max_candidates)
            report = collect_rehearsal(
                root=ROOT,
                candidates=candidates,
                seed=str(args.seed or secrets.randbits(64)),
                base_url=args.base_url,
                session_token=args.session_token,
                timeout_seconds=args.timeout_seconds,
                poll_seconds=args.poll_seconds,
                why_question=args.why_question,
                evaluate_drift=args.evaluate_drift,
                run_guardrail=args.run_guardrail,
                browser_status=args.browser_status,
                browser_summary=args.browser_summary,
                generated_at=args.generated_at,
            )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Failed to collect fresh public repo import rehearsal: {exc}", file=sys.stderr)
        return 1
    json_path = ROOT / args.output_json
    markdown_path = ROOT / args.output_markdown
    _write_json(json_path, report)
    _write_markdown(markdown_path, report)
    print(f"Fresh public repo rehearsal JSON written to {json_path}")
    print(f"Fresh public repo rehearsal Markdown written to {markdown_path}")
    print(f"Status: {report['status']}")
    return 1 if report["status"] == "blocking" else 0


if __name__ == "__main__":
    raise SystemExit(main())
