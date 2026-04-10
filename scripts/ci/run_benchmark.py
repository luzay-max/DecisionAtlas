from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from urllib import error, request


def load_json(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


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
        print(
            f"{repository['id']}: repo={repository['repo']} "
            f"min_candidates={expectations.get('minimum_candidate_decisions', 0)} "
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Run benchmark against a live API endpoint.")
    parser.add_argument(
        "--live-real-repos",
        action="store_true",
        help="Run real-repo why benchmark cases against a live API endpoint and existing imported workspaces.",
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:3001", help="API base URL for live benchmark mode.")
    parser.add_argument("--workspace-slug", default="demo-workspace", help="Workspace slug for live benchmark mode.")
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
        return run_live_real_repo_why_cases(base_url=args.base_url, why_cases=why_cases)

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
