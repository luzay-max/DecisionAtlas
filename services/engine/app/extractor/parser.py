from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


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
    source_quotes: list[str]


@dataclass(slots=True)
class ExtractionParseResult:
    decision: ParsedDecision | None
    loss_reason: str | None = None
    salvaged: bool = False


FALLBACK_CONFIDENCE = 0.55


def parse_extraction_response(
    raw_response: str | None,
    *,
    artifact_title: str | None = None,
) -> ExtractionParseResult:
    if raw_response is None or not raw_response.strip():
        return ExtractionParseResult(decision=None, loss_reason="null_decision")

    payload_text = _extract_json_payload(raw_response)
    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError:
        return ExtractionParseResult(decision=None, loss_reason="invalid_json")

    if payload is None:
        return ExtractionParseResult(decision=None, loss_reason="null_decision")
    if isinstance(payload, dict) and isinstance(payload.get("decision"), dict):
        payload = payload["decision"]
    if not isinstance(payload, dict):
        return ExtractionParseResult(decision=None, loss_reason="invalid_json")

    return _normalize_payload(payload, artifact_title=artifact_title)


def _extract_json_payload(raw_response: str) -> str:
    cleaned = raw_response.strip()
    fenced = re.match(r"^```(?:json)?\s*(.*?)\s*```$", cleaned, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        return fenced.group(1).strip()
    if cleaned.lower().startswith("json\n"):
        cleaned = cleaned.split("\n", 1)[1].strip()
    if cleaned.startswith("{") or cleaned.startswith("[") or cleaned == "null":
        return cleaned
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        return cleaned[start : end + 1]
    return cleaned


def _normalize_payload(payload: dict[str, Any], *, artifact_title: str | None) -> ExtractionParseResult:
    salvaged = False

    title, title_key = _pick_text(payload, "title", "decision_title", "decisionTitle", "name", "summary_title")
    if not title and artifact_title:
        title = artifact_title.strip()
        salvaged = True

    problem, problem_key = _pick_text(
        payload,
        "problem",
        "problem_statement",
        "problemStatement",
        "question",
        "motivation",
        "decision_problem",
    )
    context, context_key = _pick_text(payload, "context", "background", "decision_context", "notes")
    constraints, constraints_key = _pick_text(payload, "constraints", "constraint", "guardrails")
    chosen_option, chosen_key = _pick_text(
        payload,
        "chosen_option",
        "chosenOption",
        "selected_option",
        "selectedOption",
        "decision",
        "resolution",
        "recommendation",
    )
    tradeoffs, tradeoffs_key = _pick_text(
        payload,
        "tradeoffs",
        "trade_offs",
        "tradeOffs",
        "downsides",
        "risks",
        "cons",
        "considerations",
        "rationale",
        "reasoning",
    )
    source_quote, quote_key = _pick_text(
        payload,
        "source_quote",
        "sourceQuote",
        "quote",
        "evidence_quote",
        "evidenceQuote",
    )
    source_quotes = _pick_text_list(
        payload,
        "source_quotes",
        "sourceQuotes",
        "supporting_quotes",
        "supportingQuotes",
        "evidence_quotes",
        "evidenceQuotes",
    )
    confidence, confidence_key = _pick_float(payload, "confidence", "score", "certainty")
    if confidence is None:
        confidence = FALLBACK_CONFIDENCE
        salvaged = True

    for key in (title_key, problem_key, context_key, constraints_key, chosen_key, tradeoffs_key, quote_key, confidence_key):
        if key is not None and key not in {"title", "problem", "context", "constraints", "chosen_option", "tradeoffs", "source_quote", "confidence"}:
            salvaged = True

    normalized_quotes = _normalize_quotes(source_quote=source_quote, additional_quotes=source_quotes)

    if not title or not problem or not chosen_option or not tradeoffs or not source_quote:
        return ExtractionParseResult(decision=None, loss_reason="missing_required_fields", salvaged=salvaged)

    return ExtractionParseResult(
        decision=ParsedDecision(
            title=title,
            problem=problem,
            context=context,
            constraints=constraints,
            chosen_option=chosen_option,
            tradeoffs=tradeoffs,
            confidence=confidence,
            source_quote=source_quote,
            source_quotes=normalized_quotes,
        ),
        salvaged=salvaged,
    )


def _pick_text(payload: dict[str, Any], *keys: str) -> tuple[str | None, str | None]:
    for key in keys:
        value = payload.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text, key
    return None, None


def _pick_float(payload: dict[str, Any], *keys: str) -> tuple[float | None, str | None]:
    for key in keys:
        value = payload.get(key)
        if value in (None, ""):
            continue
        try:
            return float(value), key
        except (TypeError, ValueError):
            continue
    return None, None


def _pick_text_list(payload: dict[str, Any], *keys: str) -> list[str]:
    values: list[str] = []
    for key in keys:
        raw_value = payload.get(key)
        if raw_value is None:
            continue
        candidates = raw_value if isinstance(raw_value, list) else [raw_value]
        for candidate in candidates:
            text = str(candidate).strip()
            if text:
                values.append(text)
    return values


def _normalize_quotes(*, source_quote: str | None, additional_quotes: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for candidate in [source_quote, *additional_quotes]:
        if not candidate:
            continue
        quote = candidate.strip()
        key = quote.casefold()
        if not quote or key in seen:
            continue
        seen.add(key)
        normalized.append(quote)
    return normalized
