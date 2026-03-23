from __future__ import annotations

import httpx

from app.llm.base import (
    ExtractionRequest,
    ProviderRateLimitError,
    ProviderRequestError,
    ProviderResponseError,
    ProviderTimeoutError,
)


class OpenAICompatibleProvider:
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str = "https://api.openai.com/v1",
        timeout: float = 60.0,
        client: httpx.Client | None = None,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.client = client or httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )

    def extract_candidate(self, request: ExtractionRequest) -> str | None:
        try:
            response = self.client.post(
                "/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": request.prompt},
                        {
                            "role": "user",
                            "content": request.artifact_content,
                        },
                    ],
                    "temperature": 0,
                },
            )
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise ProviderTimeoutError("Timed out while calling extraction provider") from exc
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 429:
                raise ProviderRateLimitError("Extraction provider rate limit exceeded") from exc
            detail = _response_detail(exc.response)
            raise ProviderRequestError(
                f"Extraction provider request failed with status {exc.response.status_code}: {detail}"
            ) from exc
        except httpx.HTTPError as exc:
            raise ProviderRequestError("Extraction provider request failed") from exc

        payload = response.json()
        choices = payload.get("choices") or []
        if not choices:
            raise ProviderResponseError("Extraction provider returned no choices")
        content = (choices[0].get("message") or {}).get("content")
        if content is None or not isinstance(content, str):
            raise ProviderResponseError("Extraction provider returned an invalid response payload")
        return content


def _response_detail(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        text = response.text.strip()
        return text[:200] if text else "no response body"

    if isinstance(payload, dict):
        for key in ("error", "message", "detail"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()[:200]
            if isinstance(value, dict):
                nested = value.get("message") or value.get("detail")
                if isinstance(nested, str) and nested.strip():
                    return nested.strip()[:200]
    return str(payload)[:200]
