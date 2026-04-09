import pytest

from app.extractor.parser import parse_extraction_response


def test_parser_maps_valid_json_to_decision() -> None:
    parsed = parse_extraction_response(
        """
        {
          "title": "Use Redis Cache",
          "problem": "Latency is too high",
          "context": "Traffic increased",
          "constraints": "Need cheap infrastructure",
          "chosen_option": "Use Redis for cache",
          "tradeoffs": "More moving parts",
          "confidence": 0.81,
          "source_quote": "We decided to use Redis for cache."
        }
        """
    )

    assert parsed is not None
    assert parsed.loss_reason is None
    assert parsed.decision is not None
    assert parsed.decision.title == "Use Redis Cache"
    assert parsed.decision.confidence == 0.81


def test_parser_rejects_malformed_json() -> None:
    parsed = parse_extraction_response("not-json")

    assert parsed.decision is None
    assert parsed.loss_reason == "invalid_json"


def test_parser_rejects_missing_required_fields() -> None:
    parsed = parse_extraction_response('{"title":"x"}')

    assert parsed.decision is None
    assert parsed.loss_reason == "missing_required_fields"
