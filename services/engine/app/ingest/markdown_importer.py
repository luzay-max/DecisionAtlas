from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from app.ingest.file_discovery import discover_adr_files, discover_markdown_files
from app.repositories.artifacts import ArtifactRepository
from app.repositories.workspaces import WorkspaceRepository


def _strip_frontmatter(content: str) -> str:
    if not content.startswith("---"):
        return content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return content
    return parts[2].lstrip()


def _repo_doc_url(repo_url: str | None, file_path: Path, root: Path) -> str | None:
    if not repo_url:
        return None
    relative = file_path.relative_to(root).as_posix()
    return f"{repo_url.rstrip('/')}/blob/main/{relative}"


class MarkdownImporter:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.workspaces = WorkspaceRepository(session)
        self.artifacts = ArtifactRepository(session)

    def import_directory(self, *, workspace_slug: str, root: Path, repo: str) -> int:
        workspace = self.workspaces.get_by_slug(workspace_slug)
        if workspace is None:
            raise ValueError(f"Workspace not found: {workspace_slug}")

        files = {path for path in discover_markdown_files(root)}
        files.update(discover_adr_files(root))

        total = 0
        for file_path in sorted(files):
            content = _strip_frontmatter(file_path.read_text(encoding="utf-8"))
            source_id = str(file_path.relative_to(root)).replace("\\", "/")
            self.artifacts.upsert(
                workspace_id=workspace.id,
                artifact_type="doc",
                source_id=source_id,
                repo=repo,
                title=file_path.stem,
                content=content,
                author=None,
                url=_repo_doc_url(workspace.repo_url, file_path, root),
                timestamp=None,
                metadata_json={"path": source_id},
            )
            total += 1

        self.session.commit()
        return total
