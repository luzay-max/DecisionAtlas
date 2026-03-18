from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_initial_tables_exist(tmp_path: Path) -> None:
    db_path = tmp_path / "schema.db"
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")

    command.upgrade(alembic_cfg, "head")

    engine = create_engine(f"sqlite:///{db_path}")
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    assert {
        "workspaces",
        "artifacts",
        "artifact_chunks",
        "decisions",
        "source_refs",
        "relations",
        "drift_alerts",
    }.issubset(table_names)
