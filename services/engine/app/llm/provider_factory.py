from __future__ import annotations

from dataclasses import dataclass

from app.config import Settings, get_settings
from app.indexing.embedder import Embedder, FakeEmbedder, OpenAICompatibleEmbedder
from app.llm.base import ExtractionProvider, ProviderConfigurationError
from app.llm.fake_provider import FakeProvider
from app.llm.openai_compatible import OpenAICompatibleProvider


@dataclass(frozen=True, slots=True)
class RuntimeProviders:
    extraction_provider: ExtractionProvider
    embedder: Embedder
    mode: str
    is_live: bool


def build_runtime_providers(settings: Settings | None = None) -> RuntimeProviders:
    resolved = settings or get_settings()
    mode = resolved.llm_provider_mode.lower()
    if mode not in {"auto", "fake", "openai_compatible"}:
        raise ProviderConfigurationError(f"Unsupported llm_provider_mode: {resolved.llm_provider_mode}")

    if mode == "fake" or (mode == "auto" and not resolved.llm_api_key):
        return RuntimeProviders(
            extraction_provider=FakeProvider(),
            embedder=FakeEmbedder(),
            mode="fake",
            is_live=False,
        )

    if not resolved.llm_api_key:
        raise ProviderConfigurationError("LLM_API_KEY is required when using a live provider")
    if not resolved.llm_model:
        raise ProviderConfigurationError("LLM_MODEL is required when using a live provider")
    if not resolved.embedding_model:
        raise ProviderConfigurationError("EMBEDDING_MODEL is required when using a live provider")

    embedding_api_key = resolved.embedding_api_key or resolved.llm_api_key
    if not embedding_api_key:
        raise ProviderConfigurationError("EMBEDDING_API_KEY or LLM_API_KEY is required for embeddings")

    return RuntimeProviders(
        extraction_provider=OpenAICompatibleProvider(
            api_key=resolved.llm_api_key,
            model=resolved.llm_model,
            base_url=resolved.llm_base_url,
            timeout=resolved.llm_timeout_seconds,
        ),
        embedder=OpenAICompatibleEmbedder(
            api_key=embedding_api_key,
            model=resolved.embedding_model,
            base_url=resolved.llm_base_url,
            timeout=resolved.llm_timeout_seconds,
        ),
        mode="openai_compatible",
        is_live=True,
    )
