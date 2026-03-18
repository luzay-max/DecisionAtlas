from __future__ import annotations

import json
from dataclasses import dataclass


@dataclass(slots=True)
class ParsedDecision:
    title: str
    problem: str
    context: str | None
    constraints: str | None
    chosen_option: str
    tradeoffs: str
    confidence: float
    source_quote: str


def parse_extraction_response(raw_response: str | None) -> ParsedDecision | None:
    if raw_response is None:
        return None
    try:
        payload = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid JSON extraction response") from exc

    if payload is None:
        return None

    required = ["title", "problem", "chosen_option", "tradeoffs", "confidence", "source_quote"]
    missing = [key for key in required if key not in payload or payload[key] in (None, "")]
    if missing:
        raise ValueError(f"Missing required extraction fields: {', '.join(missing)}")

    return ParsedDecision(
        title=str(payload["title"]),
        problem=str(payload["problem"]),
        context=None if payload.get("context") is None else str(payload["context"]),
        constraints=None if payload.get("constraints") is None else str(payload["constraints"]),
        chosen_option=str(payload["chosen_option"]),
        tradeoffs=str(payload["tradeoffs"]),
        confidence=float(payload["confidence"]),
        source_quote=str(payload["source_quote"]),
    )
