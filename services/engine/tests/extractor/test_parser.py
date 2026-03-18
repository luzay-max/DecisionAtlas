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
    assert parsed.title == "Use Redis Cache"
    assert parsed.confidence == 0.81


def test_parser_rejects_malformed_json() -> None:
    with pytest.raises(ValueError, match="Invalid JSON"):
        parse_extraction_response("not-json")


def test_parser_rejects_missing_required_fields() -> None:
    with pytest.raises(ValueError, match="Missing required extraction fields"):
        parse_extraction_response('{"title":"x"}')
