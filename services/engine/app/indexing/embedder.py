from __future__ import annotations

import httpx

from app.llm.base import (
    ProviderRateLimitError,
    ProviderRequestError,
    ProviderResponseError,
    ProviderTimeoutError,
)


class Embedder:
    def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class FakeEmbedder(Embedder):
    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[float(len(text)), float(index)] for index, text in enumerate(texts)]


class OpenAICompatibleEmbedder(Embedder):
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str = "https://api.openai.com/v1",
        timeout: float = 60.0,
        client: httpx.Client | None = None,
    ) -> None:
        self.client = client or httpx.Client(
            base_url=base_url.rstrip("/"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )
        self.model = model

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        try:
            response = self.client.post(
                "/embeddings",
                json={
                    "model": self.model,
                    "input": texts,
                },
            )
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise ProviderTimeoutError("Timed out while calling embedding provider") from exc
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 429:
                raise ProviderRateLimitError("Embedding provider rate limit exceeded") from exc
            raise ProviderRequestError(
                f"Embedding provider request failed with status {exc.response.status_code}"
            ) from exc
        except httpx.HTTPError as exc:
            raise ProviderRequestError("Embedding provider request failed") from exc

        payload = response.json()
        data = payload.get("data")
        if not isinstance(data, list) or len(data) != len(texts):
            raise ProviderResponseError("Embedding provider returned an invalid response payload")

        embeddings: list[list[float]] = []
        for item in data:
            embedding = item.get("embedding") if isinstance(item, dict) else None
            if not isinstance(embedding, list) or not embedding:
                raise ProviderResponseError("Embedding provider returned an empty embedding")
            embeddings.append([float(value) for value in embedding])
        return embeddings
