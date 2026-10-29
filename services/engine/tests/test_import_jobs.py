from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

from alembic import command
from alembic.config import Config
import httpx
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.models import Artifact, ImportJob, Workspace
from app.ingest.github_client import GitHubNetworkError
from app.ingest.github_types import GitHubImportResult
from app.jobs.import_jobs import (
    INCREMENTAL_SYNC_OVERLAP,
    _incremental_since_for_success,
    _classify_failure,
    _classify_private_access_validation_failure,
    _normalize_repo,
    queue_github_import,
    run_github_import,
)
from app.llm.base import DecisionScreeningRequest, ExtractionRequest, ProviderTimeoutError
from app.repositories.import_jobs import ImportJobRepository




def test_incremental_since_uses_previous_start_with_utc_overlap_not_finish() -> None:
    started = datetime(2026, 10, 29, 10, 0, 0)
    completed = datetime(2026, 10, 29, 10, 15, 0)
    previous = SimpleNamespace(
        started_at=started,
        finished_at=completed,
        created_at=datetime(2026, 10, 29, 9, 58, 0),
    )
    lower = _incremental_since_for_success(previous)
    assert lower == datetime(2026, 10, 29, 9, 55, 0, tzinfo=timezone.utc)
    # An update made after the issue listing but before extraction finishes
    # must remain in the next import's selected interval.
    changed_during_previous_run = datetime(2026, 10, 29, 10, 3, tzinfo=timezone.utc)
    assert lower < changed_during_previous_run < completed.replace(tzinfo=timezone.utc)


def test_incremental_since_falls_back_to_created_at_for_legacy_job() -> None:
    created = datetime(2026, 10, 29, 9, 30, tzinfo=timezone.utc)
    previous = SimpleNamespace(
        started_at=None, finished_at=datetime(2026, 10, 29, 10, 0, tzinfo=timezone.utc),
        created_at=created,
    )
    assert _incremental_since_for_success(previous) == created - INCREMENTAL_SYNC_OVERLAP


def test_failed_incremental_retry_reuses_previous_success_start_window(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "incremental-start-window.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}")
    started = datetime(2026, 10, 29, 10, 0)
    finished = datetime(2026, 10, 29, 10, 15)
    with Session(engine) as session:
        workspace = Workspace(
            slug="github-org-repo", name="org/repo", repo_url="https://github.com/org/repo"
        )
        session.add(workspace)
        session.flush()
        history = ImportJobRepository(session)
        previous = history.create(
            job_id="previous-success",
            workspace_id=workspace.id,
            repo="org/repo",
            mode="full",
        )
        previous.status = "succeeded"
        previous.started_at = started
        previous.finished_at = finished
        session.commit()

    observed_windows: list[datetime | None] = []

    class FailingIncrementalImporter:
        def __init__(self, session, client) -> None:
            pass

        def import_repo(self, *, workspace_slug: str, repo: str, mode: str = "full",
                        since=None, progress_callback=None):
            assert mode == "since_last_sync"
            observed_windows.append(since)
            raise RuntimeError("Synthetic import failure")

    monkeypatch.setattr("app.jobs.import_jobs.GitHubImporter", FailingIncrementalImporter)
    monkeypatch.setattr("app.jobs.import_jobs._preflight_repository_access", lambda **kwargs: None)
    monkeypatch.setattr(
        "app.jobs.import_jobs.build_runtime_providers",
        lambda settings: SimpleNamespace(embedder=object(), extraction_provider=object()),
    )
    expected = datetime(2026, 10, 29, 9, 55, tzinfo=timezone.utc)
    for _ in range(2):
        queued = queue_github_import(
            workspace_slug="github-org-repo", repo="org/repo", mode="since_last_sync",
        )
        failed = run_github_import(
            job_id=str(queued["job_id"]),
            workspace_slug="github-org-repo",
            repo="org/repo",
            mode="since_last_sync",
        )
        assert failed["status"] == "failed"
        assert failed["summary"]["sync_window"] == {
            "source_since": expected.isoformat(),
            "basis": "last_success_started_at_with_overlap",
            "overlap_seconds": 300,
        }

    assert observed_windows == [expected, expected]
    with Session(engine) as session:
        latest_success = ImportJobRepository(session).latest_success_for_repo(1, "org/repo")
        assert latest_success is not None
        assert latest_success.job_id == "previous-success"

def test_run_github_import_rolls_back_partial_artifacts_on_failure(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "import-job-failure.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")

    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        session.add(Workspace(slug="github-org-repo", name="org/repo", repo_url="https://github.com/org/repo"))
        session.commit()

    class FailingImporter:
        def __init__(self, session, client) -> None:
            self.session = session

        def import_repo(self, *, workspace_slug: str, repo: str, mode: str = "full", since=None, progress_callback=None):
            workspace = self.session.scalar(select(Workspace).where(Workspace.slug == workspace_slug))
            assert workspace is not None
            self.session.add(
                Artifact(
                    workspace_id=workspace.id,
                    type="issue",
                    source_id="partial-1",
                    repo=repo,
                    title="Partial artifact",
                    content="This should be rolled back",
                    author="alice",
                    url="https://github.com/org/repo/issues/1",
                    timestamp=None,
                    metadata_json=None,
                )
            )
            self.session.flush()
            raise ValueError("Unsupported GitHub content encoding for CHANGELOG.md")

    monkeypatch.setattr("app.jobs.import_jobs.GitHubImporter", FailingImporter)
    monkeypatch.setattr("app.jobs.import_jobs._preflight_repository_access", lambda **kwargs: None)
    monkeypatch.setattr(
        "app.jobs.import_jobs.build_runtime_providers",
        lambda settings: SimpleNamespace(embedder=object(), extraction_provider=object()),
    )

    queued_job = queue_github_import(workspace_slug="github-org-repo", repo="org/repo", mode="full")
    result = run_github_import(
        job_id=str(queued_job["job_id"]),
        workspace_slug="github-org-repo",
        repo="org/repo",
        mode="full",
    )

    assert result["status"] == "failed"
    assert result["imported_count"] == 0
    assert result["summary"]["stage"] == "importing_artifacts"
    assert result["summary"]["failure_category"] == "analysis_execution_failed"

    with Session(engine) as session:
        artifacts = session.scalars(select(Artifact)).all()

    assert artifacts == []


def test_run_github_import_succeeds_when_extraction_provider_times_out(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "import-job-timeout.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")

    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        session.add(Workspace(slug="github-org-repo", name="org/repo", repo_url="https://github.com/org/repo"))
        session.commit()

    class TimeoutImporter:
        def __init__(self, session, client) -> None:
            self.session = session

        def import_repo(self, *, workspace_slug: str, repo: str, mode: str = "full", since=None, progress_callback=None):
            workspace = self.session.scalar(select(Workspace).where(Workspace.slug == workspace_slug))
            assert workspace is not None
            self.session.add(
                Artifact(
                    workspace_id=workspace.id,
                    type="doc",
                    source_id="docs/architecture.md",
                    repo=repo,
                    title="Architecture",
                    content="We decided to use Redis as a cache because latency mattered.",
                    author=None,
                    url="https://github.com/org/repo/blob/main/docs/architecture.md",
                    timestamp=None,
                    metadata_json={"path": "docs/architecture.md", "signal_category": "architecture"},
                )
            )
            self.session.commit()
            return GitHubImportResult(
                imported_count=1,
                artifact_counts={"issue": 0, "pr": 0, "commit": 0, "doc": 1},
                selected_document_count=1,
                imported_document_count=1,
                skipped_document_counts={"non_markdown": 0},
                selected_document_categories={"architecture": 1},
            )

    class FakeEmbedder:
        def embed(self, chunks):
            return [[0.1, 0.2, 0.3] for _ in chunks]

    class TimeoutProvider:
        def screen_decision_likeness(self, request: DecisionScreeningRequest) -> bool:
            return True

        def extract_candidate(self, request: ExtractionRequest) -> str | None:
            raise ProviderTimeoutError("Timed out while calling extraction provider")

    monkeypatch.setattr("app.jobs.import_jobs.GitHubImporter", TimeoutImporter)
    monkeypatch.setattr("app.jobs.import_jobs._preflight_repository_access", lambda **kwargs: None)
    monkeypatch.setattr(
        "app.jobs.import_jobs.build_runtime_providers",
        lambda settings: SimpleNamespace(embedder=FakeEmbedder(), extraction_provider=TimeoutProvider()),
    )

    queued_job = queue_github_import(workspace_slug="github-org-repo", repo="org/repo", mode="full")
    result = run_github_import(
        job_id=str(queued_job["job_id"]),
        workspace_slug="github-org-repo",
        repo="org/repo",
        mode="full",
    )

    assert result["status"] == "succeeded"
    assert result["summary"]["stage"] == "completed"
    assert result["summary"]["outcome"] == "insufficient_evidence"
    assert result["summary"]["extraction_summary"]["created_candidates"] == 0
    assert result["summary"]["extraction_summary"]["shortlisted_artifacts"] == 1
    assert result["summary"]["extraction_summary"]["screened_in_artifacts"] == 1
    assert result["summary"]["extraction_summary"]["full_extraction_requests"] == 1
    assert result["summary"]["extraction_summary"]["skipped_provider_timeout"] == 1
    assert result["summary"]["extraction_summary"]["conversion_loss_reasons"]["provider_timeout"] == 1
    assert result["summary"]["extraction_summary"]["total_artifacts"] == 2
    assert result["summary"]["extraction_summary"]["processed_artifacts"] == 2


def test_run_github_import_records_thin_source_ref_coverage_in_summary(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "import-job-thin-coverage.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")

    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        session.add(Workspace(slug="github-org-repo", name="org/repo", repo_url="https://github.com/org/repo"))
        session.commit()

    class SingleArtifactImporter:
        def __init__(self, session, client) -> None:
            self.session = session

        def import_repo(self, *, workspace_slug: str, repo: str, mode: str = "full", since=None, progress_callback=None):
            workspace = self.session.scalar(select(Workspace).where(Workspace.slug == workspace_slug))
            assert workspace is not None
            self.session.add(
                Artifact(
                    workspace_id=workspace.id,
                    type="pr",
                    source_id="release-1",
                    repo=repo,
                    title="GitHub App token for release candidates",
                    content="Use a GitHub App identity when ensuring release candidate branches.",
                    author="alice",
                    url="https://github.com/org/repo/pull/10",
                    timestamp=None,
                    metadata_json=None,
                )
            )
            self.session.commit()
            return GitHubImportResult(
                imported_count=1,
                artifact_counts={"issue": 0, "pr": 1, "commit": 0, "doc": 0},
                selected_document_count=0,
                imported_document_count=0,
                skipped_document_counts={},
                selected_document_categories={},
            )

    class FakeEmbedder:
        def embed(self, chunks):
            return [[0.1, 0.2, 0.3] for _ in chunks]

    class ThinCoverageProvider:
        def screen_decision_likeness(self, request: DecisionScreeningRequest) -> bool:
            return True

        def extract_candidate(self, request: ExtractionRequest) -> str | None:
            return """
            {
              "title": "Use GitHub App token for release candidate branch operations",
              "problem": "Release candidate branch operations fail with the default token",
              "chosen_option": "Use a GitHub App token for release candidate branch operations",
              "tradeoffs": "Requires separate app identity",
              "confidence": 0.9,
              "source_quote": "Use a GitHub App identity when ensuring release candidate branches."
            }
            """

    monkeypatch.setattr("app.jobs.import_jobs.GitHubImporter", SingleArtifactImporter)
    monkeypatch.setattr("app.jobs.import_jobs._preflight_repository_access", lambda **kwargs: None)
    monkeypatch.setattr(
        "app.jobs.import_jobs.build_runtime_providers",
        lambda settings: SimpleNamespace(embedder=FakeEmbedder(), extraction_provider=ThinCoverageProvider()),
    )
    monkeypatch.setattr("app.jobs.import_jobs._build_extraction_progress_reporter", lambda **kwargs: (lambda stats: None))

    queued_job = queue_github_import(workspace_slug="github-org-repo", repo="org/repo", mode="full")
    result = run_github_import(
        job_id=str(queued_job["job_id"]),
        workspace_slug="github-org-repo",
        repo="org/repo",
        mode="full",
    )

    assert result["status"] == "succeeded"
    assert result["summary"]["extraction_summary"]["thin_source_ref_decisions"] == 1
    assert result["summary"]["extraction_summary"]["conversion_loss_reasons"]["thin_source_ref_coverage"] == 1


def test_run_github_import_records_recovery_conversion_counters_in_summary(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "import-job-recovery.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")

    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        session.add(Workspace(slug="github-org-repo", name="org/repo", repo_url="https://github.com/org/repo"))
        session.commit()

    class RecoveryImporter:
        def __init__(self, session, client) -> None:
            self.session = session

        def import_repo(self, *, workspace_slug: str, repo: str, mode: str = "full", since=None, progress_callback=None):
            workspace = self.session.scalar(select(Workspace).where(Workspace.slug == workspace_slug))
            assert workspace is not None
            self.session.add(
                Artifact(
                    workspace_id=workspace.id,
                    type="doc",
                    source_id="docs/rollout.md",
                    repo=repo,
                    title="Rollout plan",
                    content=(
                        "We decided to move long-running work to a queue because request latency mattered. "
                        "The rollout will happen gradually so we can watch queue health. "
                        "This keeps the API responsive while adoption grows."
                    ),
                    author=None,
                    url="https://github.com/org/repo/blob/main/docs/rollout.md",
                    timestamp=None,
                    metadata_json={"path": "docs/rollout.md", "signal_category": "rollout"},
                )
            )
            self.session.commit()
            return GitHubImportResult(
                imported_count=1,
                artifact_counts={"issue": 0, "pr": 0, "commit": 0, "doc": 1},
                selected_document_count=1,
                imported_document_count=1,
                skipped_document_counts={},
                selected_document_categories={"rollout": 1},
            )

    class FakeEmbedder:
        def embed(self, chunks):
            return [[0.1, 0.2, 0.3] for _ in chunks]

    class RecoveryProvider:
        def screen_decision_likeness(self, request: DecisionScreeningRequest) -> bool:
            return True

        def extract_candidate(self, request: ExtractionRequest) -> str | None:
            if "Potential decision evidence:" not in request.artifact_content:
                return "not valid json"
            return """
            {
              "title": "Recover queue rollout",
              "problem": "Long-running tasks block request handling",
              "context": "Background processing volume increased",
              "constraints": "Keep the API responsive during rollout",
              "chosen_option": "Move long-running work to a queue",
              "tradeoffs": "More infrastructure, lower request latency",
              "confidence": 0.84,
              "source_quote": "We decided to move long-running work to a queue because request latency mattered.",
              "source_quotes": [
                "We decided to move long-running work to a queue because request latency mattered.",
                "The rollout will happen gradually so we can watch queue health."
              ]
            }
            """

    monkeypatch.setattr("app.jobs.import_jobs.GitHubImporter", RecoveryImporter)
    monkeypatch.setattr("app.jobs.import_jobs._preflight_repository_access", lambda **kwargs: None)
    monkeypatch.setattr(
        "app.jobs.import_jobs.build_runtime_providers",
        lambda settings: SimpleNamespace(embedder=FakeEmbedder(), extraction_provider=RecoveryProvider()),
    )
    monkeypatch.setattr("app.jobs.import_jobs._build_extraction_progress_reporter", lambda **kwargs: (lambda stats: None))

    queued_job = queue_github_import(workspace_slug="github-org-repo", repo="org/repo", mode="full")
    result = run_github_import(
        job_id=str(queued_job["job_id"]),
        workspace_slug="github-org-repo",
        repo="org/repo",
        mode="full",
    )

    assert result["status"] == "succeeded"
    assert result["summary"]["outcome"] == "ok"
    assert result["summary"]["extraction_summary"]["created_candidates"] == 1
    assert result["summary"]["extraction_summary"]["recovery_extraction_attempts"] == 1
    assert result["summary"]["extraction_summary"]["recovered_candidates"] == 1
    assert result["summary"]["extraction_summary"]["skipped_invalid_json"] == 0
    assert result["summary"]["extraction_summary"]["conversion_loss_reasons"] == {}


def test_classify_failure_distinguishes_network_provider_and_repository_access() -> None:
    request = httpx.Request("GET", "https://api.github.com/repos/org/repo")
    response = httpx.Response(404, request=request, json={"message": "Not Found"})
    http_error = httpx.HTTPStatusError("not found", request=request, response=response)

    assert _classify_failure(GitHubNetworkError("network", cause=httpx.ConnectError("boom", request=request))) == "network_failure"
    assert _classify_failure(http_error) == "repository_access_failure"
    assert _classify_failure(ProviderTimeoutError("provider timeout")) == "provider_failure"


def test_private_access_validation_failure_categories_are_stable() -> None:
    request = httpx.Request("GET", "https://api.github.com/repos/org/private-repo")
    unauthorized = httpx.HTTPStatusError("bad credentials", request=request, response=httpx.Response(401, request=request))
    not_found = httpx.HTTPStatusError("not found", request=request, response=httpx.Response(404, request=request))
    network = GitHubNetworkError("network", cause=httpx.ConnectError("boom", request=request))

    assert _classify_private_access_validation_failure(unauthorized, repo_ref="org/private-repo")[0:2] == (
        "authorization_failed",
        "unauthorized",
    )
    assert _classify_private_access_validation_failure(not_found, repo_ref="org/private-repo")[0:2] == (
        "repository_not_found",
        "repository_not_found",
    )
    assert _classify_private_access_validation_failure(network, repo_ref="org/private-repo")[0:2] == (
        "network_failure",
        "provider_failure",
    )


def test_normalize_repo_rejects_invalid_input_without_retryable_client_path() -> None:
    try:
        _normalize_repo("not-a-repo")
    except ValueError as exc:
        assert "owner/repo" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_queue_github_import_rejects_private_repo_without_authorized_source(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "import-job-private-required.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")

    request = httpx.Request("GET", "https://api.github.com/repos/org/private-repo")
    response = httpx.Response(404, request=request, json={"message": "Not Found"})

    def fake_get_repository_metadata(self, repo: str):
        raise httpx.HTTPStatusError("not found", request=request, response=response)

    monkeypatch.setattr("app.jobs.import_jobs.GitHubClient.get_repository_metadata", fake_get_repository_metadata)

    try:
        queue_github_import(workspace_slug=None, repo="org/private-repo", mode="full")
    except ValueError as exc:
        assert "not publicly reachable" in str(exc)
    else:
        raise AssertionError("expected ValueError")
