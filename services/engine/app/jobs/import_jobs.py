from __future__ import annotations

from uuid import uuid4

from app.config import get_settings
from app.db.session import get_db_session
from app.ingest.github_client import GitHubClient
from app.ingest.github_importer import GitHubImporter


def run_github_import(*, workspace_slug: str, repo: str) -> dict[str, int | str]:
    settings = get_settings()
    session = get_db_session()
    try:
        importer = GitHubImporter(session, GitHubClient(token=getattr(settings, "github_token", None)))
        imported_count = importer.import_repo(workspace_slug=workspace_slug, repo=repo)
        return {
            "job_id": str(uuid4()),
            "imported_count": imported_count,
        }
    finally:
        session.close()
