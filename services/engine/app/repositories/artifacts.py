from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Artifact


class ArtifactRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def upsert(
        self,
        *,
        workspace_id: int,
        artifact_type: str,
        source_id: str,
        repo: str,
        title: str | None,
        content: str,
        author: str | None,
        url: str | None,
        timestamp,
        metadata_json: dict | None = None,
    ) -> Artifact:
        stmt = select(Artifact).where(
            Artifact.workspace_id == workspace_id,
            Artifact.type == artifact_type,
            Artifact.source_id == source_id,
        )
        artifact = self.session.scalar(stmt)
        if artifact is None:
            artifact = Artifact(
                workspace_id=workspace_id,
                type=artifact_type,
                source_id=source_id,
                repo=repo,
                title=title,
                content=content,
                author=author,
                url=url,
                timestamp=timestamp,
                metadata_json=metadata_json,
            )
            self.session.add(artifact)
        else:
            artifact.repo = repo
            artifact.title = title
            artifact.content = content
            artifact.author = author
            artifact.url = url
            artifact.timestamp = timestamp
            artifact.metadata_json = metadata_json

        self.session.flush()
        return artifact

    def list_by_workspace(self, workspace_id: int) -> list[Artifact]:
        stmt = select(Artifact).where(Artifact.workspace_id == workspace_id).order_by(Artifact.id)
        return list(self.session.scalars(stmt))
