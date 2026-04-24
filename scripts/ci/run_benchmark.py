from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
from pathlib import Path
import sys
from urllib import error, request
from urllib.parse import urlencode


def load_json(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def _json_request(
    *,
    base_url: str,
    path: str,
    method: str = "GET",
    body: dict | None = None,
    timeout: int = 30,
) -> tuple[dict | None, dict | None]:
    encoded_body = json.dumps(body).encode("utf-8") if body is not None else None
    http_request = request.Request(
        f"{base_url.rstrip('/')}{path}",
        data=encoded_body,
        headers={"Content-Type": "application/json"},
        method=method,
    )
    try:
        with request.urlopen(http_request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8")), None
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        return None, {"type": "http_error", "status": exc.code, "detail": detail}
    except error.URLError as exc:
        return None, {"type": "url_error", "detail": str(exc)}


def _operational_outcome(error_payload: dict | None, *, missing_workspace_on_404: bool = False) -> str:
    if missing_workspace_on_404 and error_payload and error_payload.get("status") == 404:
        return "missing_workspace"
    return "operational_failure"


def _nested_int(payload: dict | None, *keys: str) -> int:
    current: object = payload or {}
    for key in keys:
        if not isinstance(current, dict):
            return 0
        current = current.get(key)
    try:
        return int(current or 0)
    except (TypeError, ValueError):
        return 0


def _latest_import_summary(dashboard_payload: dict) -> dict:
    latest_import = dashboard_payload.get("latest_import") or {}
    summary = latest_import.get("summary")
    return summary if isinstance(summary, dict) else {}


def _decision_total(decision_counts: dict) -> int:
    return sum(int(decision_counts.get(state, 0) or 0) for state in ("candidate", "accepted", "rejected", "superseded"))


def _write_report(path: Path, report: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_live_repo_set(repositories: list[dict]) -> int:
    if not repositories:
        print("Live benchmark repository set is empty.", file=sys.stderr)
        return 1

    print(f"Loaded {len(repositories)} live benchmark repositories.")
    for repository in repositories:
        expectations = repository.get("expectations", {})
        if not repository.get("repo") or "/" not in repository["repo"]:
            print(f"Invalid repository entry: {repository}", file=sys.stderr)
            return 1
        if expectations.get("minimum_candidate_decisions", 0) < 0:
            print(f"Invalid minimum candidate count for {repository['repo']}.", file=sys.stderr)
            return 1
        if expectations.get("minimum_reviewable_candidates", 0) < 0:
            print(f"Invalid minimum reviewable candidate count for {repository['repo']}.", file=sys.stderr)
            return 1
        if expectations.get("minimum_accepted_decisions", 0) < 0:
            print(f"Invalid minimum accepted decision count for {repository['repo']}.", file=sys.stderr)
            return 1
        if expectations.get("minimum_screened_in_artifacts", 0) < 0:
            print(f"Invalid minimum screened-in count for {repository['repo']}.", file=sys.stderr)
            return 1
        if not expectations.get("expected_readiness_states"):
            print(f"Missing readiness expectations for {repository['repo']}.", file=sys.stderr)
            return 1
        if not expectations.get("expected_why_states"):
            print(f"Missing why expectations for {repository['repo']}.", file=sys.stderr)
            return 1
        if not expectations.get("expected_drift_states"):
            print(f"Missing drift expectations for {repository['repo']}.", file=sys.stderr)
            return 1
        if expectations.get("minimum_accepted_decisions", 0) > 0 and not expectations.get(
            "expected_why_states_after_first_acceptance"
        ):
            print(
                f"Missing first-acceptance why expectations for {repository['repo']}.",
                file=sys.stderr,
            )
            return 1
        print(
            f"{repository['id']}: repo={repository['repo']} "
            f"min_candidates={expectations.get('minimum_candidate_decisions', 0)} "
            f"min_reviewable={expectations.get('minimum_reviewable_candidates', 0)} "
            f"min_accepted={expectations.get('minimum_accepted_decisions', 0)} "
            f"min_screened_in={expectations.get('minimum_screened_in_artifacts', 0)}"
        )
    return 0


def _repo_ids(repositories: list[dict]) -> set[str]:
    return {repository["id"] for repository in repositories if repository.get("id")}


def validate_why_cases(why_cases: list[dict], repositories: list[dict]) -> int:
    if not why_cases:
        print("Live benchmark why-case set is empty.", file=sys.stderr)
        return 1

    repo_ids = _repo_ids(repositories)
    seen_ids: set[str] = set()
    print(f"Loaded {len(why_cases)} real-repo why benchmark cases.")
    for case in why_cases:
        case_id = case.get("id")
        if not case_id or case_id in seen_ids:
            print(f"Invalid or duplicate why case id: {case}", file=sys.stderr)
            return 1
        seen_ids.add(case_id)
        if case.get("repo_id") not in repo_ids:
            print(f"Why case {case_id} references unknown repo_id: {case.get('repo_id')}", file=sys.stderr)
            return 1
        if not case.get("repo") or "/" not in case["repo"]:
            print(f"Invalid repo for why case {case_id}: {case.get('repo')}", file=sys.stderr)
            return 1
        if not case.get("workspace_slug", "").startswith("github-"):
            print(f"Invalid workspace_slug for why case {case_id}: {case.get('workspace_slug')}", file=sys.stderr)
            return 1
        if not case.get("question", "").strip():
            print(f"Missing question for why case {case_id}.", file=sys.stderr)
            return 1
        if not case.get("expected_status"):
            print(f"Missing expected_status for why case {case_id}.", file=sys.stderr)
            return 1
        if case.get("min_citations", 0) < 1:
            print(f"Invalid min_citations for why case {case_id}.", file=sys.stderr)
            return 1
        if not case.get("expected_terms"):
            print(f"Missing expected_terms for why case {case_id}.", file=sys.stderr)
            return 1
        print(
            f"{case_id}: workspace={case['workspace_slug']} "
            f"status={case['expected_status']} min_citations={case['min_citations']}"
        )
    return 0


def validate_drift_cases(drift_cases: list[dict], repositories: list[dict]) -> int:
    if not drift_cases:
        print("Live benchmark drift-case set is empty.", file=sys.stderr)
        return 1

    repo_ids = _repo_ids(repositories)
    seen_ids: set[str] = set()
    print(f"Loaded {len(drift_cases)} real-repo drift benchmark cases.")
    for case in drift_cases:
        case_id = case.get("id")
        if not case_id or case_id in seen_ids:
            print(f"Invalid or duplicate drift case id: {case}", file=sys.stderr)
            return 1
        seen_ids.add(case_id)
        if case.get("repo_id") not in repo_ids:
            print(f"Drift case {case_id} references unknown repo_id: {case.get('repo_id')}", file=sys.stderr)
            return 1
        if not case.get("workspace_slug", "").startswith("github-"):
            print(f"Invalid workspace_slug for drift case {case_id}: {case.get('workspace_slug')}", file=sys.stderr)
            return 1
        if not case.get("artifact_title_pattern", "").strip():
            print(f"Missing artifact_title_pattern for drift case {case_id}.", file=sys.stderr)
            return 1
        if not case.get("accepted_decision_title", "").strip():
            print(f"Missing accepted_decision_title for drift case {case_id}.", file=sys.stderr)
            return 1
        if not case.get("forbidden_alert_types"):
            print(f"Missing forbidden_alert_types for drift case {case_id}.", file=sys.stderr)
            return 1
        if not case.get("allowed_outcomes"):
            print(f"Missing allowed_outcomes for drift case {case_id}.", file=sys.stderr)
            return 1
        print(
            f"{case_id}: workspace={case['workspace_slug']} "
            f"forbidden={','.join(case['forbidden_alert_types'])}"
        )
    return 0


def validate_fixtures(queries: list[dict], expected_answers: list[dict]) -> int:
    root = Path(__file__).resolve().parents[2]
    query_ids = [item["id"] for item in queries]
    expected_ids = [item["id"] for item in expected_answers]

    if query_ids != expected_ids:
        print("Benchmark fixture mismatch between queries and expected answers.", file=sys.stderr)
        return 1

    print(f"Loaded {len(queries)} benchmark queries.")
    for query, expected in zip(queries, expected_answers):
        print(
            f"{query['id']}: {query['question']} -> topic={expected['expected_topic']} "
            f"min_citations={expected['min_citations']}"
        )
    return 0


def _evaluate_why_payload(payload: dict, expected: dict) -> tuple[bool, str]:
    answer = (payload.get("answer") or "").lower()
    expected_terms = [term.lower() for term in expected.get("expected_terms", [])]
    observed_status = payload.get("status")
    citations = payload.get("citations", [])
    status_matches = observed_status == expected.get("expected_status", "ok")
    citations_match = len(citations) >= expected["min_citations"]
    term_matches = all(term in answer for term in expected_terms)
    passed = status_matches and citations_match and term_matches
    if passed:
        return True, "passed"
    return (
        False,
        "expected "
        f"status={expected.get('expected_status', 'ok')} min_citations={expected['min_citations']} "
        f"terms={expected_terms}; observed status={observed_status} citations={len(citations)}",
    )


def run_live_benchmark(*, base_url: str, workspace_slug: str, queries: list[dict], expected_answers: list[dict]) -> int:
    failures = 0
    for query, expected in zip(queries, expected_answers):
        body = json.dumps(
            {
                "workspace_slug": workspace_slug,
                "question": query["question"],
            }
        ).encode("utf-8")
        http_request = request.Request(
            f"{base_url.rstrip('/')}/query/why",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except error.URLError as exc:
            print(f"Live benchmark request failed for {query['id']}: {exc}", file=sys.stderr)
            return 1

        passed, reason = _evaluate_why_payload(payload, expected)
        print(
            f"{query['id']}: status={payload.get('status')} citations={len(payload.get('citations', []))} "
            f"passed={passed}"
        )
        if not passed:
            print(f"Demo benchmark failed for {query['id']}: {reason}", file=sys.stderr)
            failures += 1
    if failures:
        print(f"Live benchmark failed for {failures} queries.", file=sys.stderr)
        return 1
    return 0


def run_live_real_repo_why_cases(*, base_url: str, why_cases: list[dict]) -> int:
    failures = 0
    for case in why_cases:
        body = json.dumps(
            {
                "workspace_slug": case["workspace_slug"],
                "question": case["question"],
            }
        ).encode("utf-8")
        http_request = request.Request(
            f"{base_url.rstrip('/')}/query/why",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except error.URLError as exc:
            print(
                f"Live real-repo why case failed for {case['id']} "
                f"workspace={case['workspace_slug']}: {exc}",
                file=sys.stderr,
            )
            return 1

        passed, reason = _evaluate_why_payload(payload, case)
        print(
            f"{case['id']}: workspace={case['workspace_slug']} "
            f"status={payload.get('status')} citations={len(payload.get('citations', []))} passed={passed}"
        )
        if not passed:
            print(
                f"Live real-repo why case failed for {case['id']} "
                f"workspace={case['workspace_slug']}: {reason}",
                file=sys.stderr,
            )
            failures += 1
    if failures:
        print(f"Live real-repo why benchmark failed for {failures} cases.", file=sys.stderr)
        return 1
    return 0


def _evaluate_dashboard_payload(repository: dict, payload: dict) -> tuple[bool, dict]:
    expectations = repository.get("expectations", {})
    readiness = payload.get("workspace_readiness") or {}
    drift_status = payload.get("drift_status") or {}
    decision_counts = payload.get("decision_counts") or {}
    import_summary = _latest_import_summary(payload)
    extraction_summary = import_summary.get("extraction_summary") if isinstance(import_summary, dict) else {}
    extraction_summary = extraction_summary if isinstance(extraction_summary, dict) else {}

    readiness_state = readiness.get("state")
    why_state = readiness.get("why_state")
    drift_state = drift_status.get("state") or readiness.get("drift_state")
    candidate_count = int(decision_counts.get("candidate", 0) or 0)
    accepted_count = int(decision_counts.get("accepted", 0) or 0)
    total_decisions = _decision_total(decision_counts)
    screened_in_count = _nested_int({"extraction_summary": extraction_summary}, "extraction_summary", "screened_in_artifacts")

    checks = {
        "readiness_allowed": readiness_state in expectations.get("expected_readiness_states", []),
        "why_allowed": why_state in expectations.get("expected_why_states", []) if why_state else True,
        "drift_allowed": drift_state in expectations.get("expected_drift_states", []) if drift_state else True,
        "minimum_candidate_decisions": total_decisions >= int(expectations.get("minimum_candidate_decisions", 0) or 0),
        "minimum_reviewable_candidates": candidate_count >= int(expectations.get("minimum_reviewable_candidates", 0) or 0),
        "minimum_accepted_decisions": accepted_count >= int(expectations.get("minimum_accepted_decisions", 0) or 0),
        "minimum_screened_in_artifacts": screened_in_count >= int(expectations.get("minimum_screened_in_artifacts", 0) or 0),
    }
    row = {
        "workspace_slug": repository["workspace_slug"],
        "workspace_mode": payload.get("workspace_mode"),
        "bounded_outcome": readiness_state or "unknown",
        "readiness_state": readiness_state,
        "review_state": readiness.get("review_state"),
        "why_state": why_state,
        "drift_state": drift_state,
        "next_action": readiness.get("next_action"),
        "recommended_actions": readiness.get("recommended_actions") or [],
        "candidate_decision_count": candidate_count,
        "accepted_decision_count": accepted_count,
        "total_decision_count": total_decisions,
        "screened_in_artifact_count": screened_in_count,
        "latest_import_status": payload.get("import_status"),
        "checks": checks,
    }
    return all(checks.values()), row


def _evaluate_drift_cases_for_workspace(*, payload: dict, cases: list[dict]) -> tuple[bool, list[dict], str | None]:
    evaluation = payload.get("evaluation") or {}
    observed_state = evaluation.get("state")
    alerts = payload.get("alerts") or []
    case_results: list[dict] = []
    failures = 0
    for case in cases:
        title_pattern = case["artifact_title_pattern"].lower()
        forbidden_types = set(case.get("forbidden_alert_types", []))
        matching_forbidden_alerts = []
        for alert in alerts:
            artifact = alert.get("artifact") or {}
            artifact_title = str(artifact.get("title") or "").lower()
            if title_pattern in artifact_title and alert.get("alert_type") in forbidden_types:
                matching_forbidden_alerts.append(
                    {
                        "alert_type": alert.get("alert_type"),
                        "artifact_title": artifact.get("title"),
                        "decision_title": (alert.get("decision") or {}).get("title"),
                    }
                )
        passed = not matching_forbidden_alerts
        failures += 0 if passed else 1
        case_results.append(
            {
                "id": case["id"],
                "passed": passed,
                "forbidden_alert_types": case.get("forbidden_alert_types", []),
                "matching_forbidden_alerts": matching_forbidden_alerts,
            }
        )
    return failures == 0, case_results, observed_state


def run_live_real_repo_validation(
    *,
    base_url: str,
    repositories: list[dict],
    why_cases: list[dict],
    drift_cases: list[dict],
    report_path: Path,
) -> int:
    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "base_url": base_url,
        "repositories": [],
        "summary": {"repositories": len(repositories), "passed": 0, "failed": 0},
    }
    failures = 0
    why_cases_by_repo: dict[str, list[dict]] = {}
    drift_cases_by_repo: dict[str, list[dict]] = {}
    for case in why_cases:
        why_cases_by_repo.setdefault(case["repo_id"], []).append(case)
    for case in drift_cases:
        drift_cases_by_repo.setdefault(case["repo_id"], []).append(case)

    for repository in repositories:
        query = urlencode({"workspace_slug": repository["workspace_slug"]})
        dashboard_payload, dashboard_error = _json_request(base_url=base_url, path=f"/dashboard/summary?{query}")
        row = {
            "id": repository["id"],
            "repo": repository["repo"],
            "workspace_slug": repository["workspace_slug"],
            "passed": False,
            "bounded_outcome": "unknown",
            "operational_error": None,
            "dashboard": None,
            "why_cases": [],
            "drift": None,
        }
        if dashboard_error is not None or dashboard_payload is None:
            row["bounded_outcome"] = _operational_outcome(dashboard_error, missing_workspace_on_404=True)
            row["operational_error"] = dashboard_error
            failures += 1
            report["repositories"].append(row)
            print(f"{repository['id']}: outcome={row['bounded_outcome']} passed=False")
            continue

        dashboard_passed, dashboard_row = _evaluate_dashboard_payload(repository, dashboard_payload)
        row["bounded_outcome"] = dashboard_row["bounded_outcome"]
        row["dashboard"] = dashboard_row
        repo_passed = dashboard_passed

        for case in why_cases_by_repo.get(repository["id"], []):
            why_payload, why_error = _json_request(
                base_url=base_url,
                path="/query/why",
                method="POST",
                body={"workspace_slug": case["workspace_slug"], "question": case["question"]},
            )
            if why_error is not None or why_payload is None:
                case_result = {
                    "id": case["id"],
                    "passed": False,
                    "status": "operational_failure",
                    "operational_error": why_error,
                }
            else:
                passed, reason = _evaluate_why_payload(why_payload, case)
                case_result = {
                    "id": case["id"],
                    "passed": passed,
                    "status": why_payload.get("status"),
                    "citations": len(why_payload.get("citations", [])),
                    "reason": reason,
                    "readiness_state": ((why_payload.get("answer_context") or {}).get("workspace_readiness") or {}).get(
                        "state"
                    ),
                }
            row["why_cases"].append(case_result)
            repo_passed = repo_passed and bool(case_result["passed"])

        drift_payload, drift_error = _json_request(base_url=base_url, path=f"/drift?{query}")
        repo_drift_cases = drift_cases_by_repo.get(repository["id"], [])
        if drift_error is not None or drift_payload is None:
            drift_result = {
                "passed": False,
                "state": "operational_failure",
                "operational_error": drift_error,
                "cases": [],
            }
        else:
            drift_passed, case_results, drift_state = _evaluate_drift_cases_for_workspace(
                payload=drift_payload,
                cases=repo_drift_cases,
            )
            drift_allowed = (
                drift_state in repository.get("expectations", {}).get("expected_drift_states", [])
                if drift_state
                else True
            )
            drift_result = {
                "passed": drift_passed and drift_allowed,
                "state": drift_state,
                "state_allowed": drift_allowed,
                "cases": case_results,
            }
        row["drift"] = drift_result
        repo_passed = repo_passed and bool(drift_result["passed"])

        row["passed"] = repo_passed
        failures += 0 if repo_passed else 1
        report["repositories"].append(row)
        print(
            f"{repository['id']}: outcome={row['bounded_outcome']} "
            f"readiness={dashboard_row['readiness_state']} drift={row['drift']['state']} passed={repo_passed}"
        )

    report["summary"]["passed"] = len(repositories) - failures
    report["summary"]["failed"] = failures
    _write_report(report_path, report)
    print(f"Live real-repo validation report written to {report_path}")
    if failures:
        print(f"Live real-repo validation failed for {failures} repositories.", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Run benchmark against a live API endpoint.")
    parser.add_argument(
        "--live-real-repos",
        action="store_true",
        help="Run real-repo readiness, why, and drift benchmark checks against a live API endpoint and existing imported workspaces.",
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:3001", help="API base URL for live benchmark mode.")
    parser.add_argument("--workspace-slug", default="demo-workspace", help="Workspace slug for live benchmark mode.")
    parser.add_argument(
        "--live-real-repos-report",
        default=".tmp/live-real-repo-validation-report.json",
        help="Output path for the live real-repo validation report.",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    workspace_dir = root / "examples" / "demo-workspace"
    live_repo_dir = root / "examples" / "live-benchmarks"
    queries = load_json(workspace_dir / "queries.json")
    expected_answers = load_json(workspace_dir / "expected-answers.json")
    live_repositories = load_json(live_repo_dir / "repositories.json")
    why_cases = load_json(live_repo_dir / "why-cases.json")
    drift_cases = load_json(live_repo_dir / "drift-cases.json")

    fixture_status = validate_fixtures(queries, expected_answers)
    if fixture_status != 0:
        return fixture_status

    live_repo_status = validate_live_repo_set(live_repositories)
    if live_repo_status != 0:
        return live_repo_status

    why_case_status = validate_why_cases(why_cases, live_repositories)
    if why_case_status != 0:
        return why_case_status

    drift_case_status = validate_drift_cases(drift_cases, live_repositories)
    if drift_case_status != 0:
        return drift_case_status

    if args.live_real_repos:
        return run_live_real_repo_validation(
            base_url=args.base_url,
            repositories=live_repositories,
            why_cases=why_cases,
            drift_cases=drift_cases,
            report_path=(root / args.live_real_repos_report).resolve(),
        )

    if not args.live:
        return 0

    return run_live_benchmark(
        base_url=args.base_url,
        workspace_slug=args.workspace_slug,
        queries=queries,
        expected_answers=expected_answers,
    )


if __name__ == "__main__":
    raise SystemExit(main())
