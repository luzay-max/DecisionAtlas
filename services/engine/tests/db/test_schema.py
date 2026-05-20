from pathlib import Path
import os

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_initial_tables_exist(tmp_path: Path) -> None:
    db_path = tmp_path / "schema.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")

    command.upgrade(alembic_cfg, "head")

    engine = create_engine(f"sqlite:///{db_path}")
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    assert {
        "workspaces",
        "actors",
        "owner_scopes",
        "owner_scope_memberships",
        "auth_sessions",
        "workspace_memberships",
        "artifacts",
        "artifact_chunks",
        "decisions",
        "source_refs",
        "relations",
        "drift_alerts",
        "import_jobs",
        "github_app_installations",
        "github_token_access_sources",
    }.issubset(table_names)

    actor_columns = {column["name"] for column in inspector.get_columns("actors")}
    workspace_membership_columns = {column["name"] for column in inspector.get_columns("workspace_memberships")}

    assert {"status", "disabled_at"}.issubset(actor_columns)
    assert {"workspace_id", "actor_id", "role"}.issubset(workspace_membership_columns)
