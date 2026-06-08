from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
from pathlib import Path
import sys
from time import sleep
from urllib import error, request
from urllib.parse import urlencode


TERMINAL_JOB_STATUSES = {"succeeded", "failed", "cancelled"}
SETUP_OUTCOMES = {
    "created",
    "reused",
    "missing_workspace",
    "provider_failure",
    "local_stack_failure",
    "operator_guided",
}


def _load_json_list(path: Path) -> list[dict]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, list):
        raise ValueError(f"Expected JSON list at {path}")
    return loaded


def _repository_by_id(repositories: list[dict], repo_id: str) -> dict:
    for repository in repositories:
        if repository.get("id") == repo_id:
            return repository
    known = ", ".join(str(repository.get("id")) for repository in repositories)
    raise ValueError(f"Unknown repository id: {repo_id}. Known repositories: {known}")


def _json_request(
    *,
    base_url: str,
    path: str,
    method: str = "GET",
    body: dict | None = None,
    session_token: str | None = None,
    timeout: int = 30,
) -> tuple[dict | None, dict | None]:
    encoded_body = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Content-Type": "application/json"}
    if session_token:
        headers["x-decisionatlas-session-token"] = session_token
    http_request = request.Request(
        f"{base_url.rstrip('/')}{path}",
        data=encoded_body,
        headers=headers,
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
    except TimeoutError as exc:
        return None, {"type": "timeout", "detail": str(exc)}


def _classify_request_error(error_payload: dict | None) -> str:
    if not error_payload:
        return "operator_guided"
    error_type = error_payload.get("type")
    if error_type in {"url_error", "timeout"}:
        return "local_stack_failure"
    status = error_payload.get("status")
    detail = str(error_payload.get("detail") or "").lower()
    if status in {401, 403}:
        return "operator_guided"
    if "network" in detail or "provider" in detail or "github" in detail:
        return "provider_failure"
    if status in {404, 409}:
        return "operator_guided"
    return "local_stack_failure"


def _next_action_for_outcome(outcome: str, *, job: dict | None = None, lookup: dict | None = None) -> str:
    if outcome == "created":
        status = (job or {}).get("status")
        if status == "succeeded":
            return "run_benchmark"
        if status in {"queued", "running"}:
            return "wait_for_import"
        if status == "failed":
            return "inspect_import_failure"
        return "check_import_job"
    if outcome == "reused":
        status = (job or {}).get("status")
        if status == "succeeded":
            return "run_benchmark"
        if status in {"queued", "running"}:
            return "wait_for_import"
        if status == "failed":
            return "inspect_import_failure"
        if (lookup or {}).get("has_running_import"):
            return "wait_for_import"
        if (lookup or {}).get("has_successful_import"):
            return "run_benchmark"
        return "run_or_resume_import"
    if outcome == "missing_workspace":
        return "run_public_import_rehearsal"
    if outcome == "provider_failure":
        return "retry_when_github_or_network_available"
    if outcome == "local_stack_failure":
        return "start_or_fix_local_stack"
    return "operator_setup"


def _wait_for_job(
    *,
    base_url: str,
    job_id: str,
    session_token: str | None,
    timeout_seconds: int,
    poll_seconds: float,
) -> tuple[dict | None, dict | None]:
    elapsed = 0.0
    latest_payload: dict | None = None
    latest_error: dict | None = None
    while elapsed <= timeout_seconds:
        latest_payload, latest_error = _json_request(
            base_url=base_url,
            path=f"/imports/{job_id}",
            session_token=session_token,
            timeout=30,
        )
        if latest_payload is not None and latest_payload.get("status") in TERMINAL_JOB_STATUSES:
            return latest_payload, None
        if latest_error is not None:
            return None, latest_error
        sleep(poll_seconds)
        elapsed += poll_seconds
    return latest_payload, {"type": "timeout", "detail": f"Import job did not finish within {timeout_seconds}s"}


def build_report(
    *,
    repository: dict,
    base_url: str,
    setup_outcome: str,
    lookup: dict | None = None,
    import_job: dict | None = None,
    error_payload: dict | None = None,
) -> dict:
    if setup_outcome not in SETUP_OUTCOMES:
        raise ValueError(f"Invalid setup outcome: {setup_outcome}")
    workspace_slug = (
        (lookup or {}).get("workspace_slug")
        or (import_job or {}).get("workspace_slug")
        or repository.get("workspace_slug")
    )
    next_action = _next_action_for_outcome(setup_outcome, job=import_job, lookup=lookup)
    benchmark_ready = setup_outcome in {"created", "reused"} and next_action == "run_benchmark"
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "evidence_type": "public-github-import-rehearsal",
        "base_url": base_url,
        "repository": {
            "id": repository.get("id"),
            "repo": repository.get("repo"),
            "workspace_slug": workspace_slug,
            "role": repository.get("role"),
            "benchmark_purpose": repository.get("benchmark_purpose"),
        },
        "setup": {
            "outcome": setup_outcome,
            "benchmark_ready": benchmark_ready,
            "next_action": next_action,
        },
        "lookup": lookup,
        "import_job": import_job,
        "error": error_payload,
    }


def write_report(path: Path, report: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_markdown_report(path: Path, report: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    repository = report.get("repository") or {}
    setup = report.get("setup") or {}
    error_payload = report.get("error") or {}
    import_job = report.get("import_job") or {}
    lines = [
        "# Public GitHub Import Rehearsal",
        "",
        f"- Generated at: `{report.get('generated_at', '-')}`",
        f"- Base URL: `{report.get('base_url', '-')}`",
        f"- Repository: `{repository.get('repo', '-')}`",
        f"- Repository id: `{repository.get('id', '-')}`",
        f"- Workspace slug: `{repository.get('workspace_slug', '-')}`",
        f"- Setup outcome: `{setup.get('outcome', '-')}`",
        f"- Benchmark ready: `{setup.get('benchmark_ready', False)}`",
        f"- Next action: `{setup.get('next_action', '-')}`",
        "",
    ]
    if import_job:
        lines.extend(
            [
                "## Import Job",
                "",
                f"- Job id: `{import_job.get('job_id', '-')}`",
                f"- Status: `{import_job.get('status', '-')}`",
                f"- Mode: `{import_job.get('mode', '-')}`",
                f"- Imported count: `{import_job.get('imported_count', '-')}`",
                "",
            ]
        )
    if error_payload:
        lines.extend(
            [
                "## Error",
                "",
                f"- Type: `{error_payload.get('type', '-')}`",
                f"- Status: `{error_payload.get('status', '-')}`",
                f"- Detail: `{str(error_payload.get('detail', '-')).replace('|', '/')}`",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def rehearse_public_import(
    *,
    repository: dict,
    base_url: str,
    session_token: str | None,
    wait: bool,
    timeout_seconds: int,
    poll_seconds: float,
) -> dict:
    query = urlencode({"repo": repository["repo"]})
    lookup, lookup_error = _json_request(
        base_url=base_url,
        path=f"/imports/lookup?{query}",
        session_token=session_token,
        timeout=30,
    )
    if lookup_error is not None or lookup is None:
        return build_report(
            repository=repository,
            base_url=base_url,
            setup_outcome=_classify_request_error(lookup_error),
            error_payload=lookup_error,
        )

    if lookup.get("workspace_exists"):
        active_import = lookup.get("active_import") if isinstance(lookup.get("active_import"), dict) else None
        if wait and active_import and active_import.get("job_id"):
            latest_job, wait_error = _wait_for_job(
                base_url=base_url,
                job_id=str(active_import["job_id"]),
                session_token=session_token,
                timeout_seconds=timeout_seconds,
                poll_seconds=poll_seconds,
            )
            if wait_error is not None:
                return build_report(
                    repository=repository,
                    base_url=base_url,
                    setup_outcome=_classify_request_error(wait_error),
                    lookup=lookup,
                    import_job=latest_job or active_import,
                    error_payload=wait_error,
                )
            if (latest_job or {}).get("status") == "failed":
                return build_report(
                    repository=repository,
                    base_url=base_url,
                    setup_outcome="provider_failure",
                    lookup=lookup,
                    import_job=latest_job,
                    error_payload={"type": "import_failed", "detail": (latest_job or {}).get("error_message")},
                )
            return build_report(
                repository=repository,
                base_url=base_url,
                setup_outcome="reused",
                lookup=lookup,
                import_job=latest_job or active_import,
            )
        return build_report(
            repository=repository,
            base_url=base_url,
            setup_outcome="reused",
            lookup=lookup,
        )

    if lookup.get("access_requirement"):
        return build_report(
            repository=repository,
            base_url=base_url,
            setup_outcome="operator_guided",
            lookup=lookup,
            error_payload={
                "type": "access_requirement",
                "detail": lookup.get("access_requirement_detail") or lookup.get("access_requirement"),
            },
        )

    import_job, import_error = _json_request(
        base_url=base_url,
        path="/imports/github",
        method="POST",
        body={"repo": repository["repo"], "mode": "full"},
        session_token=session_token,
        timeout=30,
    )
    if import_error is not None or import_job is None:
        return build_report(
            repository=repository,
            base_url=base_url,
            setup_outcome=_classify_request_error(import_error),
            lookup=lookup,
            error_payload=import_error,
        )

    latest_job = import_job
    wait_error = None
    if wait and import_job.get("job_id"):
        latest_job, wait_error = _wait_for_job(
            base_url=base_url,
            job_id=str(import_job["job_id"]),
            session_token=session_token,
            timeout_seconds=timeout_seconds,
            poll_seconds=poll_seconds,
        )
    if wait_error is not None:
        return build_report(
            repository=repository,
            base_url=base_url,
            setup_outcome=_classify_request_error(wait_error),
            lookup=lookup,
            import_job=latest_job or import_job,
            error_payload=wait_error,
        )
    if (latest_job or {}).get("status") == "failed":
        return build_report(
            repository=repository,
            base_url=base_url,
            setup_outcome="provider_failure",
            lookup=lookup,
            import_job=latest_job,
            error_payload={"type": "import_failed", "detail": (latest_job or {}).get("error_message")},
        )
    return build_report(
        repository=repository,
        base_url=base_url,
        setup_outcome="created",
        lookup=lookup,
        import_job=latest_job,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-id", default="fastapi", help="Repository id from examples/live-benchmarks/repositories.json.")
    parser.add_argument("--base-url", default="http://127.0.0.1:3001", help="Engine/API base URL.")
    parser.add_argument("--session-token", help="Optional DecisionAtlas session token.")
    parser.add_argument("--wait", action="store_true", help="Wait for queued import job to finish.")
    parser.add_argument("--timeout-seconds", type=int, default=900, help="Maximum wait time for import completion.")
    parser.add_argument("--poll-seconds", type=float, default=5.0, help="Polling interval while waiting for import completion.")
    parser.add_argument(
        "--output-json",
        default=".tmp/public-github-import-rehearsal.json",
        help="Machine-readable evidence output path.",
    )
    parser.add_argument(
        "--output-markdown",
        default=".tmp/public-github-import-rehearsal.md",
        help="Operator-readable evidence output path.",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    repositories = _load_json_list(root / "examples" / "live-benchmarks" / "repositories.json")
    try:
        repository = _repository_by_id(repositories, args.repo_id)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    report = rehearse_public_import(
        repository=repository,
        base_url=args.base_url,
        session_token=args.session_token,
        wait=args.wait,
        timeout_seconds=args.timeout_seconds,
        poll_seconds=args.poll_seconds,
    )
    json_path = (root / args.output_json).resolve()
    markdown_path = (root / args.output_markdown).resolve()
    write_report(json_path, report)
    write_markdown_report(markdown_path, report)
    print(f"Public GitHub import rehearsal JSON written to {json_path}")
    print(f"Public GitHub import rehearsal Markdown written to {markdown_path}")
    outcome = (report.get("setup") or {}).get("outcome")
    return 0 if outcome in {"created", "reused", "operator_guided", "provider_failure", "local_stack_failure"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
