from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.models import Workspace
from app.db.seed_demo import seed_demo


def test_seed_demo_creates_workspace(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "seed.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")

    workspace = seed_demo()

    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        stored = session.scalar(select(Workspace).where(Workspace.slug == workspace.slug))

    assert stored is not None
    assert stored.slug == "demo-workspace"
    assert stored.repo_url == "https://github.com/example/example"
