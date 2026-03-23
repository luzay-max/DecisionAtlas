from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class GitHubArtifactPayload:
    artifact_type: str
    source_id: str
    repo: str
    title: str | None
    content: str
    author: str | None
    url: str | None
    timestamp: datetime | None
    metadata_json: dict


@dataclass(slots=True)
class GitHubRepositoryFile:
    path: str
    sha: str | None
    size: int | None


@dataclass(slots=True)
class GitHubImportResult:
    imported_count: int
    artifact_counts: dict[str, int]
    selected_document_count: int
    imported_document_count: int
    skipped_document_counts: dict[str, int]
    selected_document_categories: dict[str, int]
