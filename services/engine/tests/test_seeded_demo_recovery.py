from __future__ import annotations

from pathlib import Path
import sys
from uuid import uuid4

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import Session

from app.db.models import Decision, ReviewAuditEvent, Workspace


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.ci.seed_smoke_demo import seed_smoke_demo
from scripts.demo.check_seeded_demo import check_seeded_demo_readiness
from scripts.demo.reset_seeded_demo import reset_seeded_demo


def _test_db_path(name: str) -> Path:
    db_dir = REPO_ROOT / ".tmp" / "test-dbs"
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / f"{name}-{uuid4().hex}.db"


def _database_url(db_path: Path) -> str:
    return f"sqlite:///{db_path}"


def _migrate(database_url: str) -> None:
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(alembic_cfg, "head")


def test_seeded_demo_readiness_detects_consumed_queue_and_reset_restores_it(monkeypatch) -> None:
    database_url = _database_url(_test_db_path("seeded-demo"))
    monkeypatch.setenv("DATABASE_URL", database_url)
    _migrate(database_url)

    seed_smoke_demo()
    assert check_seeded_demo_readiness().ready is True

    engine = create_engine(database_url)
    try:
        with Session(engine) as session:
            workspace = session.scalar(select(Workspace).where(Workspace.slug == "demo-workspace"))
            assert workspace is not None
            session.execute(
                delete(Decision).where(Decision.workspace_id == workspace.id, Decision.review_state == "candidate")
            )
            session.add(
                ReviewAuditEvent(
                    owner_scope="local-default",
                    workspace_id=workspace.id,
                    actor_id=None,
                    actor_username="local-admin",
                    actor_role="admin",
                    target_type="decision",
                    target_id=1,
                    action="accept",
                    previous_state_json={"review_state": "candidate"},
                    new_state_json={"review_state": "accepted"},
                    rationale="seeded demo reset regression coverage",
                    metadata_json={"source": "test"},
                )
            )
            session.commit()
    finally:
        engine.dispose()

    consumed = check_seeded_demo_readiness()
    assert consumed.ready is False
    assert consumed.candidate_decision_count == 0
    assert consumed.recommended_recovery == "reset"

    reset_seeded_demo()

    restored = check_seeded_demo_readiness()
    assert restored.ready is True
    assert restored.candidate_decision_count > 0
    assert restored.accepted_decision_count > 0
    assert restored.source_ref_count > 0
    assert restored.timeline_decision_count > 0
    assert restored.open_drift_alert_count > 0


def test_seeded_demo_reset_preserves_imported_workspaces(monkeypatch) -> None:
    database_url = _database_url(_test_db_path("imported-preserved"))
    monkeypatch.setenv("DATABASE_URL", database_url)
    _migrate(database_url)

    seed_smoke_demo()
    engine = create_engine(database_url)
    try:
        with Session(engine) as session:
            session.add(
                Workspace(
                    slug="imported-workspace",
                    name="Imported Workspace",
                    repo_url="https://github.com/example/imported",
                    repo_identity="example/imported",
                )
            )
            session.commit()
    finally:
        engine.dispose()

    reset_seeded_demo()

    with Session(engine) as session:
        imported = session.scalar(select(Workspace).where(Workspace.slug == "imported-workspace"))
        demo = session.scalar(select(Workspace).where(Workspace.slug == "demo-workspace"))
    engine.dispose()

    assert imported is not None
    assert imported.repo_url == "https://github.com/example/imported"
    assert demo is not None
    assert check_seeded_demo_readiness().ready is True
