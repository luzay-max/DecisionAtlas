from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.models import ArtifactChunk


class ArtifactChunkRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def replace_for_artifact(self, artifact_id: int, chunks: list[dict]) -> list[ArtifactChunk]:
        self.session.execute(delete(ArtifactChunk).where(ArtifactChunk.artifact_id == artifact_id))
        stored: list[ArtifactChunk] = []
        for chunk in chunks:
            row = ArtifactChunk(
                artifact_id=artifact_id,
                chunk_index=chunk["chunk_index"],
                content=chunk["content"],
                embedding=chunk.get("embedding"),
            )
            self.session.add(row)
            stored.append(row)
        self.session.flush()
        return stored

    def list_for_artifact(self, artifact_id: int) -> list[ArtifactChunk]:
        stmt = select(ArtifactChunk).where(ArtifactChunk.artifact_id == artifact_id).order_by(ArtifactChunk.chunk_index)
        return list(self.session.scalars(stmt))
