from __future__ import annotations

import json

from app.llm.base import DecisionScreeningRequest, ExtractionRequest


class FakeProvider:
    def screen_decision_likeness(self, request: DecisionScreeningRequest) -> bool:
        content = request.artifact_content.lower()
        return any(token in content for token in ("decide", "decision", "tradeoff", "chose", "because", "rationale"))

    def extract_candidate(self, request: ExtractionRequest) -> str | None:
        content = request.artifact_content.lower()
        if not any(token in content for token in ("decide", "decision", "tradeoff", "chose", "because")):
            return None

        quote = request.artifact_content[:200].strip()
        payload = {
            "title": request.artifact_title or "Untitled Decision",
            "problem": "Recovered from artifact content",
            "context": None,
            "constraints": None,
            "chosen_option": "Use the option described in the artifact",
            "tradeoffs": "Tradeoffs are implied by the artifact",
            "confidence": 0.72,
            "source_quote": quote,
        }
        return json.dumps(payload)
