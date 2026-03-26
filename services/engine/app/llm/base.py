from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class ExtractionRequest:
    artifact_id: int
    artifact_title: str | None
    artifact_content: str
    prompt: str
    artifact_family: str | None = None


@dataclass(slots=True)
class DecisionScreeningRequest:
    artifact_id: int
    artifact_title: str | None
    artifact_content: str
    prompt: str


class ExtractionProvider(Protocol):
    def screen_decision_likeness(self, request: DecisionScreeningRequest) -> bool:
        ...

    def extract_candidate(self, request: ExtractionRequest) -> str | None:
        ...


class ProviderError(RuntimeError):
    pass


class ProviderConfigurationError(ProviderError):
    pass


class ProviderTimeoutError(ProviderError):
    pass


class ProviderRateLimitError(ProviderError):
    pass


class ProviderRequestError(ProviderError):
    pass


class ProviderResponseError(ProviderError):
    pass
