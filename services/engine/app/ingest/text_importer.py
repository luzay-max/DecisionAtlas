from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from app.ingest.pandoc_adapter import PandocAdapter
from app.repositories.artifacts import ArtifactRepository
from app.repositories.workspaces import WorkspaceRepository


class TextImporter:
    def __init__(self, session: Session, pandoc_adapter: PandocAdapter | None = None) -> None:
        self.session = session
        self.workspaces = WorkspaceRepository(session)
        self.artifacts = ArtifactRepository(session)
        self.pandoc = pandoc_adapter or PandocAdapter()

    def import_file(self, *, workspace_slug: str, file_path: Path, repo: str = "local") -> int:
        workspace = self.workspaces.get_by_slug(workspace_slug)
        if workspace is None:
            raise ValueError(f"Workspace not found: {workspace_slug}")

        suffix = file_path.suffix.lower()
        if suffix == ".docx":
            content = self.pandoc.convert_to_markdown(file_path)
            if content is None:
                return 0
            artifact_type = "meeting_note"
        else:
            content = file_path.read_text(encoding="utf-8")
            artifact_type = "meeting_note" if suffix == ".txt" else "doc"

        self.artifacts.upsert(
            workspace_id=workspace.id,
            artifact_type=artifact_type,
            source_id=file_path.name,
            repo=repo,
            title=file_path.stem,
            content=content,
            author=None,
            url=None,
            timestamp=None,
            metadata_json={"path": str(file_path)},
        )
        self.session.commit()
        return 1
