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
