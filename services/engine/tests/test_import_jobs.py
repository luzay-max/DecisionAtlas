from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from alembic import command
from alembic.config import Config
import httpx
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.models import Artifact, Workspace
from app.ingest.github_client import GitHubNetworkError
from app.ingest.github_types import GitHubImportResult
from app.jobs.import_jobs import (
    _classify_failure,
    _classify_private_access_validation_failure,
    _github_client_for_workspace,
    _normalize_repo,
    _preflight_repository_access,
    _token_for_workspace,
    RepositoryAccessError,
    queue_github_import,
    run_github_import,
)
from app.llm.base import DecisionScreeningRequest, ExtractionRequest, ProviderTimeoutError


def test_public_workspace_can_use_valid_global_github_token() -> None:
    workspace = SimpleNamespace(access_source_type="public")
    settings = SimpleNamespace(github_token="valid-global-token")

    assert _token_for_workspace(session=None, workspace=workspace, settings=settings) == "valid-global-token"


def test_public_workspace_falls_back_to_anonymous_for_unauthorized_global_token(monkeypatch) -> None:
    created_tokens = []

    class FakeGitHubClient:
        def __init__(self, token=None, max_pages=5) -> None:
            self.token = token
            created_tokens.append(token)

        def get_repository_metadata(self, repo):
            request = httpx.Request("GET", f"https://api.github.com/repos/{repo}")
            response = httpx.Response(401, request=request)
            raise httpx.HTTPStatusError("unauthorized", request=request, response=response)

    monkeypatch.setattr("app.jobs.import_jobs.GitHubClient", FakeGitHubClient)
    workspace = SimpleNamespace(access_source_type="public")
    settings = SimpleNamespace(github_token="stale-global-token", github_import_max_pages=5)

    client = _github_client_for_workspace(
        session=None,
        workspace=workspace,
        settings=settings,
        repo="pytest-dev/pluggy",
    )

    assert client.token is None
    assert created_tokens == ["stale-global-token", None]

def test_installation_workspace_can_still_use_configured_github_token() -> None:
    workspace = SimpleNamespace(access_source_type="github_app_installation")
    settings = SimpleNamespace(github_token="installation-token")

    assert _token_for_workspace(session=None, workspace=workspace, settings=settings) == "installation-token"


def test_owner_scoped_token_workspace_uses_bound_secret(monkeypatch) -> None:
    class FakeTokenRepository:
        def __init__(self, session) -> None:
            pass

        def get_by_owner_scope_and_source_ref(self, *, owner_scope, source_ref):
            assert owner_scope == "owner-1"
            assert source_ref == "token-source-1"
            return SimpleNamespace(token_secret="owner-scoped-token")

    monkeypatch.setattr("app.jobs.import_jobs.GitHubTokenAccessSourceRepository", FakeTokenRepository)
    workspace = SimpleNamespace(
        access_source_type="github_token",
        access_source_ref="token-source-1",
        owner_scope="owner-1",
        repo_identity="org/private",
        repo_url="https://github.com/org/private",
        slug="github-org-private",
    )

    assert _token_for_workspace(session=object(), workspace=workspace, settings=SimpleNamespace()) == "owner-scoped-token"


def test_run_github_import_rolls_back_partial_artifacts_on_failure(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "import-job-failure.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("GITHUB_TOKEN", "")

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
    monkeypatch.setenv("GITHUB_TOKEN", "")

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
    monkeypatch.setenv("GITHUB_TOKEN", "")

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
    monkeypatch.setenv("GITHUB_TOKEN", "")

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
    server_error = httpx.HTTPStatusError("bad gateway", request=request, response=httpx.Response(502, request=request))
    assert _classify_failure(server_error) == "network_failure"
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


def test_public_preflight_falls_back_when_metadata_is_rate_limited(monkeypatch) -> None:
    request = httpx.Request("GET", "https://api.github.com/repos/pallets/flask")
    response = httpx.Response(403, request=request, json={"message": "API rate limit exceeded"})

    def rate_limited_metadata(self, repo: str):
        raise httpx.HTTPStatusError("rate limited", request=request, response=response)

    monkeypatch.setattr("app.jobs.import_jobs.GitHubClient.get_repository_metadata", rate_limited_metadata)
    monkeypatch.setattr(
        "app.jobs.import_jobs.GitHubClient.is_public_repository_reachable",
        lambda self, repo: True,
    )

    _preflight_repository_access(
        session=None,
        repo_ref="pallets/flask",
        owner_scope="local-default",
        access_source_type="public",
        access_source_ref=None,
    )


def test_public_preflight_keeps_indeterminate_forbidden_as_network_failure(monkeypatch) -> None:
    request = httpx.Request("GET", "https://api.github.com/repos/pallets/flask")
    response = httpx.Response(403, request=request, json={"message": "API rate limit exceeded"})

    def rate_limited_metadata(self, repo: str):
        raise httpx.HTTPStatusError("rate limited", request=request, response=response)

    monkeypatch.setattr("app.jobs.import_jobs.GitHubClient.get_repository_metadata", rate_limited_metadata)
    monkeypatch.setattr(
        "app.jobs.import_jobs.GitHubClient.is_public_repository_reachable",
        lambda self, repo: False,
    )

    try:
        _preflight_repository_access(
            session=None,
            repo_ref="pallets/flask",
            owner_scope="local-default",
            access_source_type="public",
            access_source_ref=None,
        )
    except RepositoryAccessError as exc:
        assert exc.failure_category == "network_failure"
        assert "provider or network failure" in str(exc)
    else:
        raise AssertionError("expected RepositoryAccessError")

def test_queue_github_import_rejects_private_repo_without_authorized_source(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "import-job-private-required.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("GITHUB_TOKEN", "")

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")

    request = httpx.Request("GET", "https://api.github.com/repos/org/private-repo")
    response = httpx.Response(404, request=request, json={"message": "Not Found"})

    def fake_get_repository_metadata(self, repo: str):
        raise httpx.HTTPStatusError("not found", request=request, response=response)

    monkeypatch.setattr("app.jobs.import_jobs.GitHubClient.get_repository_metadata", fake_get_repository_metadata)
    monkeypatch.setattr("app.jobs.import_jobs.GitHubClient.is_public_repository_reachable", lambda self, repo: False)

    try:
        queue_github_import(workspace_slug=None, repo="org/private-repo", mode="full")
    except ValueError as exc:
        assert "not publicly reachable" in str(exc)
    else:
        raise AssertionError("expected ValueError")
