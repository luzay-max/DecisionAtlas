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
        print(
            f"{repository['id']}: repo={repository['repo']} "
            f"min_candidates={expectations.get('minimum_candidate_decisions', 0)}"
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

        answer = (payload.get("answer") or "").lower()
        expected_terms = [term.lower() for term in expected.get("expected_terms", [])]
        status_matches = payload.get("status") == expected.get("expected_status", "ok")
        citations_match = len(payload.get("citations", [])) >= expected["min_citations"]
        term_matches = all(term in answer for term in expected_terms)
        passed = status_matches and citations_match and term_matches
        print(
            f"{query['id']}: status={payload.get('status')} citations={len(payload.get('citations', []))} "
            f"passed={passed}"
        )
        if not passed:
            failures += 1
    if failures:
        print(f"Live benchmark failed for {failures} queries.", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Run benchmark against a live API endpoint.")
    parser.add_argument("--base-url", default="http://127.0.0.1:3001", help="API base URL for live benchmark mode.")
    parser.add_argument("--workspace-slug", default="demo-workspace", help="Workspace slug for live benchmark mode.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    workspace_dir = root / "examples" / "demo-workspace"
    live_repo_dir = root / "examples" / "live-benchmarks"
    queries = load_json(workspace_dir / "queries.json")
    expected_answers = load_json(workspace_dir / "expected-answers.json")
    live_repositories = load_json(live_repo_dir / "repositories.json")

    fixture_status = validate_fixtures(queries, expected_answers)
    if fixture_status != 0:
        return fixture_status

    live_repo_status = validate_live_repo_set(live_repositories)
    if live_repo_status != 0:
        return live_repo_status

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
