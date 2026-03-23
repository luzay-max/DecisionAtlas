from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.models import Artifact, Decision, SourceRef, Workspace
from app.extractor.pipeline import CandidateExtractionPipeline
from app.llm.base import ExtractionRequest, ProviderRequestError, ProviderTimeoutError


class StubProvider:
    def extract_candidate(self, request: ExtractionRequest) -> str | None:
        if "decided" not in request.artifact_content.lower():
            return None
        return """
        {
          "title": "Adopt Redis Cache",
          "problem": "Latency is too high",
          "context": "Read load increased",
          "constraints": "Keep operational cost low",
          "chosen_option": "Use Redis as cache only",
          "tradeoffs": "Extra dependency, lower latency",
          "confidence": 0.9,
          "source_quote": "We decided to use Redis as a cache because latency mattered."
        }
        """


class InvalidJsonProvider:
    def extract_candidate(self, request: ExtractionRequest) -> str | None:
        return "not valid json"


class RejectLongInputProvider:
    def __init__(self) -> None:
        self.last_request_content: str | None = None

    def extract_candidate(self, request: ExtractionRequest) -> str | None:
        self.last_request_content = request.artifact_content
        if len(request.artifact_content) > 14000:
            raise ProviderRequestError("Extraction provider request failed with status 400: context_length_exceeded")
        return None


class Always400Provider:
    def extract_candidate(self, request: ExtractionRequest) -> str | None:
        raise ProviderRequestError("Extraction provider request failed with status 400: context_length_exceeded")


class AlwaysTimeoutProvider:
    def extract_candidate(self, request: ExtractionRequest) -> str | None:
        raise ProviderTimeoutError("Timed out while calling extraction provider")


def test_pipeline_skips_low_signal_and_creates_candidate_decision(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "extractor.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}")

    with Session(engine) as session:
        workspace = Workspace(slug="demo-workspace", name="Demo", repo_url="https://github.com/org/repo")
        session.add(workspace)
        session.flush()
        session.add_all(
            [
                Artifact(
                    workspace_id=workspace.id,
                    type="issue",
                    source_id="1",
                    repo="org/repo",
                    title="Cache decision",
                    content="We decided to use Redis as a cache because latency mattered.",
                    author="alice",
                    url="https://github.com/org/repo/issues/1",
                    timestamp=None,
                    metadata_json=None,
                ),
                Artifact(
                    workspace_id=workspace.id,
                    type="issue",
                    source_id="2",
                    repo="org/repo",
                    title="Chore",
                    content="Formatting cleanup only.",
                    author="bob",
                    url="https://github.com/org/repo/issues/2",
                    timestamp=None,
                    metadata_json=None,
                ),
            ]
        )
        session.commit()

    with Session(engine) as session:
        created = CandidateExtractionPipeline(session, StubProvider()).run(workspace_slug="demo-workspace")

    with Session(engine) as session:
        decisions = session.scalars(select(Decision)).all()
        source_refs = session.scalars(select(SourceRef)).all()

    assert created == 1
    assert len(decisions) == 1
    assert decisions[0].review_state == "candidate"
    assert len(source_refs) == 1
    assert source_refs[0].quote == "We decided to use Redis as a cache because latency mattered."


def test_pipeline_prioritizes_high_signal_docs(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "extractor-doc-priority.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}")

    with Session(engine) as session:
        workspace = Workspace(slug="demo-workspace", name="Demo", repo_url="https://github.com/org/repo")
        session.add(workspace)
        session.flush()
        session.add_all(
            [
                Artifact(
                    workspace_id=workspace.id,
                    type="doc",
                    source_id="docs/migration-guide.md",
                    repo="org/repo",
                    title="Migration Guide",
                    content="We decided to use Redis as a cache because latency mattered.",
                    author=None,
                    url="https://github.com/org/repo/blob/main/docs/migration-guide.md",
                    timestamp=None,
                    metadata_json={"path": "docs/migration-guide.md"},
                ),
                Artifact(
                    workspace_id=workspace.id,
                    type="issue",
                    source_id="2",
                    repo="org/repo",
                    title="Formatting cleanup",
                    content="Formatting cleanup only.",
                    author="bob",
                    url="https://github.com/org/repo/issues/2",
                    timestamp=None,
                    metadata_json=None,
                ),
            ]
        )
        session.commit()

    with Session(engine) as session:
        created = CandidateExtractionPipeline(session, StubProvider()).run(workspace_slug="demo-workspace")
        decisions = session.scalars(select(Decision)).all()

    assert created == 1
    assert decisions[0].title == "Adopt Redis Cache"


def test_pipeline_is_idempotent_for_already_linked_artifacts(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "extractor-repeat.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}")

    with Session(engine) as session:
        workspace = Workspace(slug="demo-workspace", name="Demo", repo_url="https://github.com/org/repo")
        session.add(workspace)
        session.flush()
        session.add(
            Artifact(
                workspace_id=workspace.id,
                type="issue",
                source_id="1",
                repo="org/repo",
                title="Cache decision",
                content="We decided to use Redis as a cache because latency mattered.",
                author="alice",
                url="https://github.com/org/repo/issues/1",
                timestamp=None,
                metadata_json=None,
            )
        )
        session.commit()

    with Session(engine) as session:
        CandidateExtractionPipeline(session, StubProvider()).run(workspace_slug="demo-workspace")

    with Session(engine) as session:
        created = CandidateExtractionPipeline(session, StubProvider()).run(workspace_slug="demo-workspace")
        decisions = session.scalars(select(Decision)).all()

    assert created == 0
    assert len(decisions) == 1


def test_pipeline_skips_invalid_json_responses(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "extractor-invalid.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}")

    with Session(engine) as session:
        workspace = Workspace(slug="demo-workspace", name="Demo", repo_url="https://github.com/org/repo")
        session.add(workspace)
        session.flush()
        session.add(
            Artifact(
                workspace_id=workspace.id,
                type="issue",
                source_id="1",
                repo="org/repo",
                title="Cache decision",
                content="We decided to use Redis as a cache because latency mattered.",
                author="alice",
                url="https://github.com/org/repo/issues/1",
                timestamp=None,
                metadata_json=None,
            )
        )
        session.commit()

    with Session(engine) as session:
        created = CandidateExtractionPipeline(session, InvalidJsonProvider()).run(workspace_slug="demo-workspace")
        decisions = session.scalars(select(Decision)).all()

    assert created == 0
    assert decisions == []


def test_pipeline_truncates_large_artifacts_before_extraction(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "extractor-large.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}")
    large_content = ("We decided to use Redis as a cache because latency mattered.\n\n" * 500).strip()
    provider = RejectLongInputProvider()

    with Session(engine) as session:
        workspace = Workspace(slug="demo-workspace", name="Demo", repo_url="https://github.com/org/repo")
        session.add(workspace)
        session.flush()
        session.add(
            Artifact(
                workspace_id=workspace.id,
                type="doc",
                source_id="docs/architecture.md",
                repo="org/repo",
                title="Architecture",
                content=large_content,
                author=None,
                url="https://github.com/org/repo/blob/main/docs/architecture.md",
                timestamp=None,
                metadata_json={"path": "docs/architecture.md"},
            )
        )
        session.commit()

    with Session(engine) as session:
        created = CandidateExtractionPipeline(session, provider).run(workspace_slug="demo-workspace")

    assert created == 0
    assert provider.last_request_content is not None
    assert len(provider.last_request_content) <= 14000
    assert "content truncated" in provider.last_request_content


def test_pipeline_skips_single_artifact_when_provider_returns_400(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "extractor-provider-400.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}")

    with Session(engine) as session:
        workspace = Workspace(slug="demo-workspace", name="Demo", repo_url="https://github.com/org/repo")
        session.add(workspace)
        session.flush()
        session.add(
            Artifact(
                workspace_id=workspace.id,
                type="doc",
                source_id="docs/architecture.md",
                repo="org/repo",
                title="Architecture",
                content="We decided to use Redis as a cache because latency mattered.",
                author=None,
                url="https://github.com/org/repo/blob/main/docs/architecture.md",
                timestamp=None,
                metadata_json={"path": "docs/architecture.md"},
            )
        )
        session.commit()

    with Session(engine) as session:
        created = CandidateExtractionPipeline(session, Always400Provider()).run(workspace_slug="demo-workspace")
        decisions = session.scalars(select(Decision)).all()

    assert created == 0
    assert decisions == []


def test_pipeline_skips_single_artifact_when_provider_times_out(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "extractor-provider-timeout.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}")

    with Session(engine) as session:
        workspace = Workspace(slug="demo-workspace", name="Demo", repo_url="https://github.com/org/repo")
        session.add(workspace)
        session.flush()
        session.add(
            Artifact(
                workspace_id=workspace.id,
                type="doc",
                source_id="docs/architecture.md",
                repo="org/repo",
                title="Architecture",
                content="We decided to use Redis as a cache because latency mattered.",
                author=None,
                url="https://github.com/org/repo/blob/main/docs/architecture.md",
                timestamp=None,
                metadata_json={"path": "docs/architecture.md"},
            )
        )
        session.commit()

    with Session(engine) as session:
        pipeline = CandidateExtractionPipeline(session, AlwaysTimeoutProvider())
        created = pipeline.run(workspace_slug="demo-workspace")
        decisions = session.scalars(select(Decision)).all()

    assert created == 0
    assert decisions == []
    assert pipeline.last_run_stats.skipped_provider_timeout == 1


def test_pipeline_reports_live_progress_stats(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "extractor-progress.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}")
    progress_updates: list[dict[str, int | str | None]] = []

    with Session(engine) as session:
        workspace = Workspace(slug="demo-workspace", name="Demo", repo_url="https://github.com/org/repo")
        session.add(workspace)
        session.flush()
        session.add_all(
            [
                Artifact(
                    workspace_id=workspace.id,
                    type="doc",
                    source_id="docs/architecture.md",
                    repo="org/repo",
                    title="Architecture",
                    content="We decided to use Redis as a cache because latency mattered.",
                    author=None,
                    url="https://github.com/org/repo/blob/main/docs/architecture.md",
                    timestamp=None,
                    metadata_json={"path": "docs/architecture.md"},
                ),
                Artifact(
                    workspace_id=workspace.id,
                    type="doc",
                    source_id="docs/rollout.md",
                    repo="org/repo",
                    title="Rollout plan",
                    content="We decided to roll out the change gradually because safety mattered.",
                    author=None,
                    url="https://github.com/org/repo/blob/main/docs/rollout.md",
                    timestamp=None,
                    metadata_json={"path": "docs/rollout.md"},
                ),
            ]
        )
        session.commit()

    with Session(engine) as session:
        pipeline = CandidateExtractionPipeline(session, StubProvider())
        pipeline.run(
            workspace_slug="demo-workspace",
            progress_callback=lambda stats: progress_updates.append(stats.to_summary()),
        )

    assert progress_updates[0]["total_artifacts"] == 2
    assert progress_updates[0]["processed_artifacts"] == 0
    assert progress_updates[-1]["processed_artifacts"] == 2
    assert progress_updates[-1]["current_artifact_title"] is None
    assert progress_updates[-1]["created_candidates"] >= 1
