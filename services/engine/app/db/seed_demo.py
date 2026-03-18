from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models import Workspace


def seed_demo() -> Workspace:
    settings = get_settings()
    engine = create_engine(settings.database_url)
    payload_path = Path(__file__).resolve().parents[4] / "examples" / "demo-workspace" / "workspace.json"
    payload = json.loads(payload_path.read_text(encoding="utf-8"))

    with Session(engine) as session:
        existing = session.scalar(select(Workspace).where(Workspace.slug == payload["slug"]))
        if existing:
            return existing

        workspace = Workspace(
            slug=payload["slug"],
            name=payload["name"],
            repo_url=payload.get("repo_url"),
        )
        session.add(workspace)
        session.commit()
        session.refresh(workspace)
        return workspace


if __name__ == "__main__":
    workspace = seed_demo()
    print(f"Seeded workspace: {workspace.slug}")
