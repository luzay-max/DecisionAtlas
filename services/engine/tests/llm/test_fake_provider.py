from app.llm.base import ExtractionRequest
from app.llm.fake_provider import FakeProvider


def test_fake_provider_returns_deterministic_extraction_for_signal_text() -> None:
    provider = FakeProvider()

    response = provider.extract_candidate(
        ExtractionRequest(
            artifact_id=1,
            artifact_title="Why we chose Redis",
            artifact_content="We decided to use Redis because latency mattered and accepted the tradeoff.",
            prompt="extract",
        )
    )

    assert response is not None
    assert "Why we chose Redis" in response


def test_fake_provider_returns_none_for_low_signal_text() -> None:
    provider = FakeProvider()

    response = provider.extract_candidate(
        ExtractionRequest(
            artifact_id=1,
            artifact_title="Status update",
            artifact_content="Minor formatting cleanup.",
            prompt="extract",
        )
    )

    assert response is None
