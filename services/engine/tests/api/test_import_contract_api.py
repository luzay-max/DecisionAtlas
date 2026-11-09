from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.api.imports import GitHubPrivateAccessBindingRequest, GitSourceBindingRequest
from app.api.imports_contract import ImportJobResponse, ImportTargetResponse


def test_import_job_contract_covers_existing_lifecycle_states_and_summary() -> None:
    for status in ("queued", "running", "paused", "succeeded", "failed"):
        response = ImportJobResponse(
            job_id="job-123",
            workspace_slug="workspace",
            repo="org/repo",
            mode="since_last_sync",
            status=status,
            sync_origin="webhook",
            trigger_event="pull_request",
            imported_count=7,
            summary={
                "stage": "completed",
                "outcome": "insufficient_evidence",
                "artifact_counts": {"issue": 1, "pr": 2},
            },
            error_message=None,
            started_at="2026-11-07T01:02:03+00:00",
            finished_at=None,
        )
        assert response.status == status
        assert response.summary is not None
        assert response.summary["artifact_counts"]["pr"] == 2

    with pytest.raises(ValidationError):
        ImportJobResponse(
            job_id="job-123",
            workspace_slug="workspace",
            repo="org/repo",
            mode="full",
            status="cancelled",
            imported_count=0,
        )


def test_import_target_response_rejects_unmodeled_credentials() -> None:
    payload = {
        "owner_scope": "local-default",
        "provider": "github",
        "access_mode": "token",
        "repo": "org/private-repo",
        "repo_url": "https://github.com/org/private-repo",
        "workspace_exists": True,
        "workspace_slug": "github-org-private-repo",
        "has_successful_import": False,
        "can_incremental_sync": False,
        "has_running_import": False,
        "latest_import": None,
        "active_import": None,
        "access_source_type": "github_token",
        "access_source_label": "Private GitHub source team private repo",
        "access_source_status": "authorized",
        "repo_private": True,
    }
    response = ImportTargetResponse.model_validate(payload)
    assert response.access_source_status == "authorized"
    assert not hasattr(response, "token")

    with pytest.raises(ValidationError):
        ImportTargetResponse.model_validate({**payload, "token": "ghp-do-not-echo"})


def test_private_access_request_credentials_are_not_in_model_repr() -> None:
    secret = "ghp-do-not-log-this"
    private_request = GitHubPrivateAccessBindingRequest(repo="org/private", token=secret)
    generic_request = GitSourceBindingRequest(
        provider="github",
        access_mode="token",
        repo="org/private",
        token=secret,
    )
    assert secret not in repr(private_request)
    assert secret not in repr(generic_request)
