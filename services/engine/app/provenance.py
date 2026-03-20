from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models import Artifact, Workspace
from app.repositories.artifacts import ArtifactRepository


WorkspaceMode = str


@dataclass(frozen=True)
class WorkspaceProvenance:
    workspace_mode: WorkspaceMode
    source_summary: str


def get_workspace_provenance(
    *,
    session: Session,
    workspace: Workspace,
    artifacts: list[Artifact] | None = None,
) -> WorkspaceProvenance:
    artifact_items = artifacts if artifacts is not None else ArtifactRepository(session).list_by_workspace(workspace.id)
    has_seeded = any(_is_seeded_artifact(artifact) for artifact in artifact_items)
    has_imported = any(not _is_seeded_artifact(artifact) for artifact in artifact_items)
    settings = get_settings()

    if has_seeded and has_imported:
        return WorkspaceProvenance(
            workspace_mode="mixed",
            source_summary="This workspace contains seeded demo data and imported repository data.",
        )

    if has_seeded or workspace.slug == settings.demo_workspace_slug:
        return WorkspaceProvenance(
            workspace_mode="demo",
            source_summary="This workspace is using seeded demo data for a guided product walkthrough.",
        )

    return WorkspaceProvenance(
        workspace_mode="imported",
        source_summary="This workspace is using imported repository data.",
    )


def _is_seeded_artifact(artifact: Artifact) -> bool:
    return artifact.source_id.startswith("seed-")
