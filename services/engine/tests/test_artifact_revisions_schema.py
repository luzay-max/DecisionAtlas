from __future__ import annotations

import hashlib
from pathlib import Path

from alembic import command
from alembic.config import Config
import pytest
from sqlalchemy import create_engine, event, inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import (
    Artifact,
    ArtifactCurrentRevision,
    ArtifactExtractionRun,
    ArtifactRevision,
    Decision,
    SourceRef,
    Workspace,
)


def _config(db_path: Path, monkeypatch) -> Config:
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    return config


def _new_engine(db_path: Path):
    engine = create_engine(f"sqlite:///{db_path}")
    @event.listens_for(engine, "connect")
    def _enable_sqlite_fk(dbapi_connection, connection_record):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")
    return engine


def test_additive_upgrade_preserves_legacy_source_refs_without_invented_revisions(
    tmp_path: Path, monkeypatch
) -> None:
    db_path = tmp_path / "from-0012.db"
    config = _config(db_path, monkeypatch)
    command.upgrade(config, "0012_review_audit_events")

    engine = create_engine(f"sqlite:///{db_path}")
    with engine.begin() as conn:
        workspace_id = conn.execute(text(
            "INSERT INTO workspaces (slug, name) VALUES ('history', 'History')"
        )).lastrowid
        artifact_id = conn.execute(text(
            "INSERT INTO artifacts (workspace_id, type, source_id, content) "
            "VALUES (:workspace_id, 'issue', 'legacy-1', 'Original quote')"
        ), {"workspace_id": workspace_id}).lastrowid
        decision_id = conn.execute(text(
            "INSERT INTO decisions (workspace_id, title, problem, chosen_option, tradeoffs) "
            "VALUES (:workspace_id, 'Cache', 'Slow reads', 'Use cache', 'Complexity')"
        ), {"workspace_id": workspace_id}).lastrowid
        ref_id = conn.execute(text(
            "INSERT INTO source_refs (decision_id, artifact_id, quote) "
            "VALUES (:decision_id, :artifact_id, 'Original quote')"
        ), {"decision_id": decision_id, "artifact_id": artifact_id}).lastrowid
    engine.dispose()

    command.upgrade(config, "head")

    engine = _new_engine(db_path)
    with Session(engine) as session:
        legacy = session.get(SourceRef, ref_id)
        assert legacy is not None
        assert legacy.artifact_id == artifact_id
        assert legacy.artifact_revision_id is None
        assert legacy.quote == "Original quote"
        assert session.get(Artifact, artifact_id).content == "Original quote"
        assert session.scalars(select(ArtifactRevision)).all() == []
        assert session.scalars(select(ArtifactCurrentRevision)).all() == []
        assert session.scalars(select(ArtifactExtractionRun)).all() == []
        assert inspect(session.bind).get_columns("source_refs")[-1]["name"] == "artifact_revision_id"
    engine.dispose()


def test_revision_schema_enforces_identity_and_pointer_same_artifact(
    tmp_path: Path, monkeypatch
) -> None:
    db_path = tmp_path / "revision-constraints.db"
    config = _config(db_path, monkeypatch)
    command.upgrade(config, "head")
    engine = _new_engine(db_path)

    with Session(engine) as session:
        workspace = Workspace(slug="revision-workspace", name="Revisions")
        session.add(workspace)
        session.flush()
        artifacts = [
            Artifact(
                workspace_id=workspace.id, type="doc", source_id=path,
                content="initial", repo="org/repo", title=path,
            )
            for path in ("docs/a.md", "docs/b.md")
        ]
        session.add_all(artifacts)
        session.flush()
        first_id, second_id = artifacts[0].id, artifacts[1].id
        decision = Decision(
            workspace_id=workspace.id, title="Initial source choice", problem="Review",
            chosen_option="Use the original", tradeoffs="Other options",
        )
        session.add(decision)
        session.flush()
        decision_id = decision.id
        original = ArtifactRevision(
            artifact_id=first_id,
            revision_number=1,
            capture_fingerprint="a" * 64,
            content_sha256=hashlib.sha256(b"initial").hexdigest(),
            content="initial",
            title="docs/a.md",
            capture_method="legacy_snapshot",
            verification_state="legacy_unverified",
        )
        session.add(original)
        session.commit()
        revision_id = original.id

    with Session(engine) as session:
        session.add(ArtifactCurrentRevision(artifact_id=second_id, revision_id=revision_id))
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()

    with Session(engine) as session:
        session.add(ArtifactCurrentRevision(artifact_id=first_id, revision_id=revision_id))
        session.add(ArtifactExtractionRun(
            artifact_revision_id=revision_id,
            extractor_fingerprint="f" * 64,
            status="succeeded",
            candidate_count=0,
        ))
        session.commit()

    # SourceRefs may only bind a revision belonging to their Artifact.
    # Legacy unbound refs (nullable revision_id) must remain legal.
    with Session(engine) as session:
        session.add_all([
            SourceRef(
                decision_id=decision_id, artifact_id=first_id,
                artifact_revision_id=revision_id, quote="Matching source revision",
            ),
            SourceRef(
                decision_id=decision_id, artifact_id=second_id,
                artifact_revision_id=None, quote="Legacy evidence not bound",
            ),
        ])
        session.commit()

    with Session(engine) as session:
        session.add(SourceRef(
            decision_id=decision_id, artifact_id=second_id,
            artifact_revision_id=revision_id, quote="Mismatched source revision",
        ))
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()

    with Session(engine) as session:
        assert len(session.scalars(select(SourceRef).where(SourceRef.decision_id == decision_id)).all()) == 2

    with Session(engine) as session:
        session.add(ArtifactRevision(
            artifact_id=first_id, revision_number=2,
            capture_fingerprint="a" * 64,
            content_sha256="b" * 64,
            content="modified", capture_method="github_api",
            verification_state="local_hash_only",
        ))
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()

    with Session(engine) as session:
        session.add(ArtifactRevision(
            artifact_id=first_id, revision_number=1,
            capture_fingerprint="c" * 64,
            content_sha256="c" * 64,
            content="modified", capture_method="github_api",
            verification_state="local_hash_only",
        ))
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()

    with Session(engine) as session:
        session.add(ArtifactExtractionRun(
            artifact_revision_id=revision_id,
            extractor_fingerprint="f" * 64,
            status="succeeded",
        ))
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()

    with Session(engine) as session:
        assert session.get(ArtifactCurrentRevision, first_id).revision_id == revision_id
        assert session.get(ArtifactCurrentRevision, second_id) is None
        assert session.scalar(select(ArtifactRevision).where(ArtifactRevision.artifact_id == first_id)).id == revision_id
        assert session.scalar(select(ArtifactExtractionRun).where(
            ArtifactExtractionRun.artifact_revision_id == revision_id
        )).candidate_count == 0
    engine.dispose()


def test_schema_only_downgrade_allowed_before_any_capture(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "no-revisions-downgrade.db"
    config = _config(db_path, monkeypatch)
    command.upgrade(config, "head")
    command.downgrade(config, "0012_review_audit_events")

    engine = create_engine(f"sqlite:///{db_path}")
    with engine.connect() as connection:
        tables = inspect(connection).get_table_names()
        assert "artifact_revisions" not in tables
        assert "artifact_current_revisions" not in tables
        assert "artifact_extraction_runs" not in tables
        assert "artifact_revision_id" not in {x["name"] for x in inspect(connection).get_columns("source_refs")}
    engine.dispose()


def test_destructive_downgrade_refused_when_revision_rows_exist(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "captured-downgrade.db"
    config = _config(db_path, monkeypatch)
    command.upgrade(config, "head")
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        workspace = Workspace(slug="preserved", name="Preserved")
        session.add(workspace)
        session.flush()
        artifact = Artifact(workspace_id=workspace.id, type="doc", source_id="README.md", content="Original")
        session.add(artifact)
        session.flush()
        session.add(ArtifactRevision(
            artifact_id=artifact.id, revision_number=1, capture_fingerprint="a" * 64,
            content_sha256="b" * 64, content="Original", capture_method="legacy_snapshot",
            verification_state="legacy_unverified",
        ))
        session.commit()
    engine.dispose()

    with pytest.raises(RuntimeError, match="Refusing destructive downgrade"):
        command.downgrade(config, "0012_review_audit_events")

    engine = create_engine(f"sqlite:///{db_path}")
    with engine.connect() as conn:
        assert conn.scalar(text("SELECT COUNT(*) FROM artifact_revisions")) == 1
    engine.dispose()
