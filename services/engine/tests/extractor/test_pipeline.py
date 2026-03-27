from __future__ import annotations

from pathlib import Path
from threading import Lock
from time import sleep

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.models import Artifact, Decision, SourceRef, Workspace
from app.extractor.pipeline import CandidateExtractionPipeline
from app.indexing.embedder import FakeEmbedder
from app.llm.base import DecisionScreeningRequest, ExtractionRequest, ProviderRequestError, ProviderTimeoutError
from app.retrieval.answering import answer_why_question


class StubProvider:
    def screen_decision_likeness(self, request: DecisionScreeningRequest) -> bool:
        return "decided" in request.artifact_content.lower()

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
    def screen_decision_likeness(self, request: DecisionScreeningRequest) -> bool:
        return True

    def extract_candidate(self, request: ExtractionRequest) -> str | None:
        return "not valid json"


class RejectLongInputProvider:
    def __init__(self) -> None:
        self.last_request_content: str | None = None

    def screen_decision_likeness(self, request: DecisionScreeningRequest) -> bool:
        return True

    def extract_candidate(self, request: ExtractionRequest) -> str | None:
        self.last_request_content = request.artifact_content
        if len(request.artifact_content) > 7000:
            raise ProviderRequestError("Extraction provider request failed with status 400: context_length_exceeded")
        return None


class Always400Provider:
    def screen_decision_likeness(self, request: DecisionScreeningRequest) -> bool:
        return True

    def extract_candidate(self, request: ExtractionRequest) -> str | None:
        raise ProviderRequestError("Extraction provider request failed with status 400: context_length_exceeded")


class AlwaysTimeoutProvider:
    def screen_decision_likeness(self, request: DecisionScreeningRequest) -> bool:
        return True

    def extract_candidate(self, request: ExtractionRequest) -> str | None:
        raise ProviderTimeoutError("Timed out while calling extraction provider")


class ScreeningGateProvider:
    def screen_decision_likeness(self, request: DecisionScreeningRequest) -> bool:
        lowered = request.artifact_content.lower()
        return "we decided" in lowered or "decision" in lowered

    def extract_candidate(self, request: ExtractionRequest) -> str | None:
        return """
        {
          "title": "Promote queue-based execution",
          "problem": "Long-running tasks block request handling",
          "context": "Higher background job volume",
          "constraints": null,
          "chosen_option": "Move long-running work to a queue",
          "tradeoffs": "More infra, lower request latency",
          "confidence": 0.85,
          "source_quote": "We decided to move long-running work to a queue because request latency mattered."
        }
        """


class ConcurrencyTrackingProvider:
    def __init__(self) -> None:
        self._active = 0
        self.max_active = 0
        self.lock = Lock()

    def screen_decision_likeness(self, request: DecisionScreeningRequest) -> bool:
        return True

    def extract_candidate(self, request: ExtractionRequest) -> str | None:
        with self.lock:
            self._active += 1
            self.max_active = max(self.max_active, self._active)
        sleep(0.05)
        with self.lock:
            self._active -= 1
        return """
        {
          "title": "Queue long-running work",
          "problem": "Latency is too high",
          "context": null,
          "constraints": null,
          "chosen_option": "Use a queue",
          "tradeoffs": "Operational overhead",
          "confidence": 0.8,
          "source_quote": "We decided to use a queue because latency mattered."
        }
        """


class FamilyTrackingProvider:
    def __init__(self) -> None:
        self.families: list[str | None] = []

    def screen_decision_likeness(self, request: DecisionScreeningRequest) -> bool:
        return True

    def extract_candidate(self, request: ExtractionRequest) -> str | None:
        self.families.append(request.artifact_family)
        return f"""
        {{
          "title": "{request.artifact_title or 'Decision'}",
          "problem": "Need a direction",
          "context": null,
          "constraints": null,
          "chosen_option": "Follow the documented approach",
          "tradeoffs": "Some complexity for clarity",
          "confidence": 0.8,
          "source_quote": "We decided to follow the documented approach because clarity mattered."
        }}
        """


class SalvageProvider:
    def screen_decision_likeness(self, request: DecisionScreeningRequest) -> bool:
        return True

    def extract_candidate(self, request: ExtractionRequest) -> str | None:
        return """
        ```json
        {
          "problem_statement": "Latency is too high",
          "selectedOption": "Move long-running work to a queue",
          "risks": "More operational overhead",
          "quote": "We decided to move long-running work to a queue because latency mattered."
        }
        ```
        """


class ConversionLossProvider:
    def screen_decision_likeness(self, request: DecisionScreeningRequest) -> bool:
        return True

    def extract_candidate(self, request: ExtractionRequest) -> str | None:
        title = (request.artifact_title or "").lower()
        if "invalid" in title:
            return "not valid json"
        if "missing" in title:
            return """
            {
              "title": "Queue rollout",
              "problem": "Latency is too high",
              "confidence": 0.7,
              "source_quote": "We decided to move long-running work to a queue because latency mattered."
            }
            """
        return """
        {
          "title": "Queue rollout",
          "problem": "Latency is too high",
          "chosen_option": "Move long-running work to a queue",
          "tradeoffs": "More operational overhead",
          "confidence": 0.7,
          "source_quote": "This quote does not exist in the artifact."
        }
        """


class MultiQuoteProvider:
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
          "source_quote": "Use a GitHub App identity when ensuring release candidate branches.",
          "source_quotes": [
            "Use a GitHub App identity when ensuring release candidate branches.",
            "This will allow creation and deletion of these branches in CI.",
            "Currently the workflow will fail due to branch protection."
          ]
        }
        """


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
        pipeline = CandidateExtractionPipeline(session, StubProvider())
        created = pipeline.run(workspace_slug="demo-workspace")
        decisions = session.scalars(select(Decision)).all()

    assert created == 1
    assert decisions[0].title == "Adopt Redis Cache"
    assert pipeline.last_run_stats.shortlisted_artifacts == 1


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
    assert len(provider.last_request_content) <= 7000
    assert "Artifact title:" in provider.last_request_content


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
    assert progress_updates[-1]["screened_artifacts"] == 2
    assert progress_updates[-1]["processed_artifacts"] == 4
    assert progress_updates[-1]["completed_full_extractions"] == 2
    assert progress_updates[-1]["current_artifact_title"] is None
    assert progress_updates[-1]["created_candidates"] >= 1


def test_pipeline_uses_screening_to_skip_low_value_artifacts(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "extractor-screening.db"
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
                    source_id="docs/architecture.md",
                    repo="org/repo",
                    title="Architecture Decision",
                    content="We decided to move long-running work to a queue because request latency mattered.",
                    author=None,
                    url="https://github.com/org/repo/blob/main/docs/architecture.md",
                    timestamp=None,
                    metadata_json={"path": "docs/architecture.md"},
                ),
                Artifact(
                    workspace_id=workspace.id,
                    type="pr",
                    source_id="2",
                    repo="org/repo",
                    title="Refactor naming",
                    content="This cleans up a few names and adds comments.",
                    author="bob",
                    url="https://github.com/org/repo/pull/2",
                    timestamp=None,
                    metadata_json=None,
                ),
            ]
        )
        session.commit()

    with Session(engine) as session:
        pipeline = CandidateExtractionPipeline(session, ScreeningGateProvider())
        created = pipeline.run(workspace_slug="demo-workspace")

    assert created == 1
    assert pipeline.last_run_stats.shortlisted_artifacts == 1
    assert pipeline.last_run_stats.screened_artifacts == 1
    assert pipeline.last_run_stats.screened_in_artifacts == 1
    assert pipeline.last_run_stats.screened_out_artifacts == 0
    assert pipeline.last_run_stats.full_extraction_requests == 1
    assert pipeline.last_run_stats.completed_full_extractions == 1


def test_pipeline_runs_full_extraction_with_bounded_concurrency(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "extractor-concurrency.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}")
    provider = ConcurrencyTrackingProvider()

    with Session(engine) as session:
        workspace = Workspace(slug="demo-workspace", name="Demo", repo_url="https://github.com/org/repo")
        session.add(workspace)
        session.flush()
        session.add_all(
            [
                Artifact(
                    workspace_id=workspace.id,
                    type="doc",
                    source_id=f"docs/architecture-{index}.md",
                    repo="org/repo",
                    title=f"Architecture {index}",
                    content="We decided to use a queue because latency mattered.",
                    author=None,
                    url=f"https://github.com/org/repo/blob/main/docs/architecture-{index}.md",
                    timestamp=None,
                    metadata_json={"path": f"docs/architecture-{index}.md"},
                )
                for index in range(5)
            ]
        )
        session.commit()

    with Session(engine) as session:
        pipeline = CandidateExtractionPipeline(session, provider)
        created = pipeline.run(workspace_slug="demo-workspace")

    assert created == 5
    assert provider.max_active >= 2
    assert provider.max_active <= 3
    assert pipeline.last_run_stats.full_extraction_requests == 5
    assert pipeline.last_run_stats.completed_full_extractions == 5


def test_pipeline_records_artifact_family_routing(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "extractor-families.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}")
    provider = FamilyTrackingProvider()

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
                    title="Architecture Decision",
                    content="We decided to follow the documented approach because clarity mattered.",
                    author=None,
                    url="https://github.com/org/repo/blob/main/docs/architecture.md",
                    timestamp=None,
                    metadata_json={"path": "docs/architecture.md"},
                ),
                Artifact(
                    workspace_id=workspace.id,
                    type="pr",
                    source_id="2",
                    repo="org/repo",
                    title="Queue rollout",
                    content="We decided to follow the documented approach because clarity mattered.",
                    author="alice",
                    url="https://github.com/org/repo/pull/2",
                    timestamp=None,
                    metadata_json=None,
                ),
                Artifact(
                    workspace_id=workspace.id,
                    type="issue",
                    source_id="3",
                    repo="org/repo",
                    title="Queue proposal",
                    content="We decided to follow the documented approach because clarity mattered.",
                    author="bob",
                    url="https://github.com/org/repo/issues/3",
                    timestamp=None,
                    metadata_json=None,
                ),
            ]
        )
        session.commit()

    with Session(engine) as session:
        pipeline = CandidateExtractionPipeline(session, provider)
        created = pipeline.run(workspace_slug="demo-workspace")

    assert created == 3
    assert provider.families.count("rationale_doc") == 1
    assert provider.families.count("pull_request") == 1
    assert provider.families.count("lightweight_evidence") == 1
    assert pipeline.last_run_stats.selected_extraction_families == {
        "rationale_doc": 1,
        "pull_request": 1,
        "lightweight_evidence": 1,
    }


def test_pipeline_salvages_recoverable_structured_output(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "extractor-salvage.db"
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
                type="pr",
                source_id="2",
                repo="org/repo",
                title="Queue rollout",
                content="We decided to move long-running work to a queue because latency mattered.",
                author="alice",
                url="https://github.com/org/repo/pull/2",
                timestamp=None,
                metadata_json=None,
            )
        )
        session.commit()

    with Session(engine) as session:
        pipeline = CandidateExtractionPipeline(session, SalvageProvider())
        created = pipeline.run(workspace_slug="demo-workspace")
        decisions = session.scalars(select(Decision)).all()

    assert created == 1
    assert len(decisions) == 1
    assert decisions[0].title == "Queue rollout"
    assert decisions[0].confidence == 0.55
    assert pipeline.last_run_stats.salvaged_candidates == 1


def test_pipeline_records_conversion_loss_reasons(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "extractor-conversion-loss.db"
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
                    source_id="docs/invalid.md",
                    repo="org/repo",
                    title="Invalid output",
                    content="We decided to move long-running work to a queue because latency mattered.",
                    author=None,
                    url="https://github.com/org/repo/blob/main/docs/invalid.md",
                    timestamp=None,
                    metadata_json={"path": "docs/invalid.md"},
                ),
                Artifact(
                    workspace_id=workspace.id,
                    type="doc",
                    source_id="docs/missing.md",
                    repo="org/repo",
                    title="Missing fields",
                    content="We decided to move long-running work to a queue because latency mattered.",
                    author=None,
                    url="https://github.com/org/repo/blob/main/docs/missing.md",
                    timestamp=None,
                    metadata_json={"path": "docs/missing.md"},
                ),
                Artifact(
                    workspace_id=workspace.id,
                    type="doc",
                    source_id="docs/ungrounded.md",
                    repo="org/repo",
                    title="Ungrounded quote",
                    content="We decided to use a different release workflow because compliance mattered.",
                    author=None,
                    url="https://github.com/org/repo/blob/main/docs/ungrounded.md",
                    timestamp=None,
                    metadata_json={"path": "docs/ungrounded.md"},
                ),
            ]
        )
        session.commit()

    with Session(engine) as session:
        pipeline = CandidateExtractionPipeline(session, ConversionLossProvider())
        created = pipeline.run(workspace_slug="demo-workspace")

    assert created == 0
    assert pipeline.last_run_stats.skipped_invalid_json == 1
    assert pipeline.last_run_stats.conversion_loss_reasons == {
        "invalid_json": 1,
        "missing_required_fields": 1,
        "ungrounded_quote": 1,
    }


def test_pipeline_persists_multiple_grounded_source_refs_when_available(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "extractor-multi-quote.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}")

    with Session(engine) as session:
        workspace = Workspace(slug="imported-workspace", name="Imported", repo_url="https://github.com/org/repo")
        session.add(workspace)
        session.flush()
        session.add(
            Artifact(
                workspace_id=workspace.id,
                type="pr",
                source_id="release-1",
                repo="org/repo",
                title="GitHub App token for release candidates",
                content=(
                    "Use a GitHub App identity when ensuring release candidate branches. "
                    "This will allow creation and deletion of these branches in CI. "
                    "Currently the workflow will fail due to branch protection."
                ),
                author="alice",
                url="https://github.com/org/repo/pull/10",
                timestamp=None,
                metadata_json=None,
            )
        )
        session.commit()

    with Session(engine) as session:
        pipeline = CandidateExtractionPipeline(session, MultiQuoteProvider())
        created = pipeline.run(workspace_slug="imported-workspace")
        decisions = session.scalars(select(Decision)).all()
        source_refs = session.scalars(select(SourceRef)).all()

    assert created == 1
    assert len(decisions) == 1
    assert len(source_refs) >= 2
    assert pipeline.last_run_stats.thin_source_ref_decisions == 0


def test_improved_source_ref_coverage_can_upgrade_imported_why_answer_to_ok(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "extractor-why-upgrade.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(f"sqlite:///{db_path}")

    with Session(engine) as session:
        workspace = Workspace(slug="imported-workspace", name="Imported", repo_url="https://github.com/org/repo")
        session.add(workspace)
        session.flush()
        session.add(
            Artifact(
                workspace_id=workspace.id,
                type="pr",
                source_id="release-1",
                repo="org/repo",
                title="GitHub App token for release candidates",
                content=(
                    "Use a GitHub App identity when ensuring release candidate branches. "
                    "This will allow creation and deletion of these branches in CI. "
                    "Currently the workflow will fail due to branch protection."
                ),
                author="alice",
                url="https://github.com/org/repo/pull/10",
                timestamp=None,
                metadata_json=None,
            )
        )
        session.commit()

    with Session(engine) as session:
        pipeline = CandidateExtractionPipeline(session, MultiQuoteProvider())
        pipeline.run(workspace_slug="imported-workspace")
        decision = session.scalars(select(Decision)).one()
        decision.review_state = "accepted"
        session.commit()

    with Session(engine) as session:
        response = answer_why_question(
            session=session,
            workspace_slug="imported-workspace",
            question="why use github app token for release candidate branch operations",
            embedder=FakeEmbedder(),
        )

    assert response["status"] == "ok"
    assert len(response["citations"]) >= 2
