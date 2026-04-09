from __future__ import annotations

from sqlalchemy.orm import Session

from app.indexing.chunker import chunk_text
from app.indexing.embedder import Embedder
from app.repositories.artifact_chunks import ArtifactChunkRepository


def index_artifact(*, session: Session, artifact_id: int, content: str, embedder: Embedder) -> int:
    chunks = chunk_text(content)
    if not chunks:
        return 0

    embeddings = embedder.embed([chunk.content for chunk in chunks])
    payload = [
        {
            **chunk.to_record(chunk_index=index),
            "embedding": embeddings[index],
        }
        for index, chunk in enumerate(chunks)
    ]
    repo = ArtifactChunkRepository(session)
    repo.replace_for_artifact(artifact_id, payload)
    session.commit()
    return len(payload)
