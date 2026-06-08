from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.ci import rehearse_public_github_import as rehearsal


REPOSITORY = {
    "id": "fastapi",
    "repo": "fastapi/fastapi",
    "workspace_slug": "github-fastapi-fastapi",
    "role": "large_python_framework",
    "benchmark_purpose": "Stress imported analysis on a large framework.",
}


def test_rehearsal_reports_reused_workspace(monkeypatch) -> None:
    def fake_json_request(**kwargs):
        assert kwargs["path"].startswith("/imports/lookup?")
        return (
            {
                "workspace_exists": True,
                "workspace_slug": "github-fastapi-fastapi",
                "has_successful_import": True,
                "has_running_import": False,
            },
            None,
        )

    monkeypatch.setattr(rehearsal, "_json_request", fake_json_request)

    report = rehearsal.rehearse_public_import(
        repository=REPOSITORY,
        base_url="http://127.0.0.1:3001",
        session_token=None,
        wait=False,
        timeout_seconds=1,
        poll_seconds=0,
    )

    assert report["setup"]["outcome"] == "reused"
    assert report["setup"]["benchmark_ready"] is True
    assert report["setup"]["next_action"] == "run_benchmark"


def test_rehearsal_creates_missing_workspace(monkeypatch) -> None:
    calls: list[str] = []

    def fake_json_request(**kwargs):
        calls.append(kwargs["path"])
        if kwargs["path"].startswith("/imports/lookup?"):
            return (
                {
                    "workspace_exists": False,
                    "workspace_slug": None,
                    "access_requirement": None,
                    "access_requirement_detail": None,
                },
                None,
            )
        if kwargs["path"] == "/imports/github":
            assert kwargs["method"] == "POST"
            assert kwargs["body"] == {"repo": "fastapi/fastapi", "mode": "full"}
            return (
                {
                    "job_id": "job-123",
                    "workspace_slug": "github-fastapi-fastapi",
                    "repo": "fastapi/fastapi",
                    "mode": "full",
                    "status": "queued",
                },
                None,
            )
        raise AssertionError(f"unexpected path {kwargs['path']}")

    monkeypatch.setattr(rehearsal, "_json_request", fake_json_request)

    report = rehearsal.rehearse_public_import(
        repository=REPOSITORY,
        base_url="http://127.0.0.1:3001",
        session_token=None,
        wait=False,
        timeout_seconds=1,
        poll_seconds=0,
    )

    assert calls == ["/imports/lookup?repo=fastapi%2Ffastapi", "/imports/github"]
    assert report["setup"]["outcome"] == "created"
    assert report["setup"]["benchmark_ready"] is False
    assert report["setup"]["next_action"] == "wait_for_import"
    assert report["import_job"]["job_id"] == "job-123"


def test_rehearsal_waits_for_existing_active_import(monkeypatch) -> None:
    def fake_json_request(**kwargs):
        assert kwargs["path"].startswith("/imports/lookup?")
        return (
            {
                "workspace_exists": True,
                "workspace_slug": "github-fastapi-fastapi",
                "has_successful_import": False,
                "has_running_import": True,
                "active_import": {"job_id": "job-active", "status": "running"},
            },
            None,
        )

    def fake_wait_for_job(**kwargs):
        assert kwargs["job_id"] == "job-active"
        return (
            {
                "job_id": "job-active",
                "workspace_slug": "github-fastapi-fastapi",
                "status": "succeeded",
                "imported_count": 42,
            },
            None,
        )

    monkeypatch.setattr(rehearsal, "_json_request", fake_json_request)
    monkeypatch.setattr(rehearsal, "_wait_for_job", fake_wait_for_job)

    report = rehearsal.rehearse_public_import(
        repository=REPOSITORY,
        base_url="http://127.0.0.1:3001",
        session_token=None,
        wait=True,
        timeout_seconds=1,
        poll_seconds=0,
    )

    assert report["setup"]["outcome"] == "reused"
    assert report["setup"]["benchmark_ready"] is True
    assert report["setup"]["next_action"] == "run_benchmark"
    assert report["import_job"]["job_id"] == "job-active"


def test_rehearsal_classifies_local_stack_failure(monkeypatch) -> None:
    def fake_json_request(**kwargs):
        return None, {"type": "url_error", "detail": "connection refused"}

    monkeypatch.setattr(rehearsal, "_json_request", fake_json_request)

    report = rehearsal.rehearse_public_import(
        repository=REPOSITORY,
        base_url="http://127.0.0.1:3001",
        session_token=None,
        wait=False,
        timeout_seconds=1,
        poll_seconds=0,
    )

    assert report["setup"]["outcome"] == "local_stack_failure"
    assert report["setup"]["benchmark_ready"] is False
    assert report["setup"]["next_action"] == "start_or_fix_local_stack"


def test_rehearsal_classifies_access_requirement_as_operator_guided(monkeypatch) -> None:
    def fake_json_request(**kwargs):
        return (
            {
                "workspace_exists": False,
                "workspace_slug": None,
                "access_requirement": "credential_required",
                "access_requirement_detail": "Repository is not publicly reachable.",
            },
            None,
        )

    monkeypatch.setattr(rehearsal, "_json_request", fake_json_request)

    report = rehearsal.rehearse_public_import(
        repository=REPOSITORY,
        base_url="http://127.0.0.1:3001",
        session_token=None,
        wait=False,
        timeout_seconds=1,
        poll_seconds=0,
    )

    assert report["setup"]["outcome"] == "operator_guided"
    assert report["setup"]["next_action"] == "operator_setup"
    assert "publicly reachable" in report["error"]["detail"]
