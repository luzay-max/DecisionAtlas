from __future__ import annotations

import httpx

from app.llm.base import ExtractionRequest


class OpenAICompatibleProvider:
    def __init__(self, *, api_key: str, model: str, base_url: str = "https://api.openai.com/v1") -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    def extract_candidate(self, request: ExtractionRequest) -> str | None:
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
        payload = response.json()
        choices = payload.get("choices") or []
        if not choices:
            return None
        return choices[0]["message"]["content"]
