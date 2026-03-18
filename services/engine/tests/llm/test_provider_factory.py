from __future__ import annotations

import httpx
import pytest

from app.config import Settings
from app.indexing.embedder import FakeEmbedder, OpenAICompatibleEmbedder
from app.llm.base import ProviderConfigurationError, ProviderResponseError
from app.llm.fake_provider import FakeProvider
from app.llm.openai_compatible import OpenAICompatibleProvider
from app.llm.provider_factory import build_runtime_providers


def test_provider_factory_defaults_to_fake_mode_without_api_key() -> None:
    runtime = build_runtime_providers(
        Settings(
            llm_provider_mode="auto",
            embedding_provider_mode="auto",
            llm_api_key=None,
            embedding_api_key=None,
        )
    )

    assert runtime.mode == "fake"
    assert runtime.is_live is False
    assert isinstance(runtime.extraction_provider, FakeProvider)
    assert isinstance(runtime.embedder, FakeEmbedder)


def test_provider_factory_uses_openai_compatible_runtime_when_key_exists() -> None:
    runtime = build_runtime_providers(
        Settings(
            llm_provider_mode="openai_compatible",
            embedding_provider_mode="openai_compatible",
            llm_api_key="test-key",
            embedding_api_key="embed-key",
            llm_model="demo-chat",
            embedding_model="demo-embed",
            llm_base_url="https://example.com/v1",
        )
    )

    assert runtime.mode == "openai_compatible"
    assert runtime.is_live is True
    assert isinstance(runtime.extraction_provider, OpenAICompatibleProvider)
    assert isinstance(runtime.embedder, OpenAICompatibleEmbedder)


def test_provider_factory_allows_live_llm_with_fake_embedder() -> None:
    runtime = build_runtime_providers(
        Settings(
            llm_provider_mode="openai_compatible",
            embedding_provider_mode="fake",
            llm_api_key="test-key",
            llm_model="deepseek-chat",
            llm_base_url="https://api.deepseek.com",
        )
    )

    assert runtime.mode == "openai_compatible"
    assert runtime.is_live is True
    assert isinstance(runtime.extraction_provider, OpenAICompatibleProvider)
    assert isinstance(runtime.embedder, FakeEmbedder)


def test_provider_factory_requires_models_for_live_runtime() -> None:
    with pytest.raises(ProviderConfigurationError):
        build_runtime_providers(
            Settings(
                llm_provider_mode="openai_compatible",
                llm_api_key="test-key",
                llm_model="",
            )
        )


def test_openai_compatible_embedder_rejects_empty_embeddings() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "embedding": [],
                    }
                ]
            },
        )

    embedder = OpenAICompatibleEmbedder(
        api_key="test-key",
        model="demo-embed",
        client=httpx.Client(transport=httpx.MockTransport(handler), base_url="https://example.com/v1"),
    )

    with pytest.raises(ProviderResponseError):
        embedder.embed(["hello"])
