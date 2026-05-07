from __future__ import annotations

from pathlib import Path
import sys

from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import Session

ENGINE_DIR = Path(__file__).resolve().parents[2] / "services" / "engine"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from app.config import get_settings
from app.db.models import Artifact, ArtifactChunk, Decision, DriftAlert, ImportJob, Relation, SourceRef, Workspace

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.ci.seed_smoke_demo import seed_smoke_demo


DEMO_WORKSPACE_SLUG = "demo-workspace"


def reset_seeded_demo() -> None:
    settings = get_settings()
    engine = create_engine(settings.database_url)
    should_seed = True

    try:
        with Session(engine) as session:
            workspace = session.scalar(select(Workspace).where(Workspace.slug == DEMO_WORKSPACE_SLUG))
            if workspace is None:
                session.commit()
                should_seed = True
            else:
                workspace_id = workspace.id
                artifact_ids = list(session.scalars(select(Artifact.id).where(Artifact.workspace_id == workspace_id)))
                decision_ids = list(session.scalars(select(Decision.id).where(Decision.workspace_id == workspace_id)))

                session.execute(delete(ImportJob).where(ImportJob.workspace_id == workspace_id))
                session.execute(delete(DriftAlert).where(DriftAlert.workspace_id == workspace_id))

                if decision_ids:
                    session.execute(delete(SourceRef).where(SourceRef.decision_id.in_(decision_ids)))
                    session.execute(
                        delete(Relation).where(
                            ((Relation.from_type == "decision") & Relation.from_id.in_(decision_ids))
                            | ((Relation.to_type == "decision") & Relation.to_id.in_(decision_ids))
                        )
                    )

                if artifact_ids:
                    session.execute(delete(SourceRef).where(SourceRef.artifact_id.in_(artifact_ids)))
                    session.execute(delete(ArtifactChunk).where(ArtifactChunk.artifact_id.in_(artifact_ids)))
                    session.execute(
                        delete(Relation).where(
                            ((Relation.from_type == "artifact") & Relation.from_id.in_(artifact_ids))
                            | ((Relation.to_type == "artifact") & Relation.to_id.in_(artifact_ids))
                        )
                    )

                session.execute(delete(Decision).where(Decision.workspace_id == workspace_id))
                session.execute(delete(Artifact).where(Artifact.workspace_id == workspace_id))
                session.execute(delete(Workspace).where(Workspace.id == workspace_id))
                session.commit()
    finally:
        engine.dispose()

    if should_seed:
        seed_smoke_demo()


if __name__ == "__main__":
    reset_seeded_demo()
    print("Reset and reseeded demo-workspace.")
