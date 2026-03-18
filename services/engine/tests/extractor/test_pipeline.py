from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.models import Artifact, Decision, SourceRef, Workspace
from app.extractor.pipeline import CandidateExtractionPipeline
from app.llm.base import ExtractionRequest


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
