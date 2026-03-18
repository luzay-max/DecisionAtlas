from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class ExtractionRequest:
    artifact_id: int
    artifact_title: str | None
    artifact_content: str
    prompt: str


class ExtractionProvider(Protocol):
    def extract_candidate(self, request: ExtractionRequest) -> str | None:
        ...
