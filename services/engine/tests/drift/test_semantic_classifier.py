from __future__ import annotations

from datetime import datetime

from app.db.models import Artifact
from app.drift.semantic_classifier import classify_semantic_drift
from app.drift.semantic_recall import SemanticCandidate


def test_classifier_emits_possible_supersession_for_replacement_language() -> None:
    artifact = Artifact(
        id=1,
        workspace_id=1,
        type="pull_request",
        source_id="2",
        repo="org/repo",
        title="Replace Redis cache with Dragonfly",
        content="We should replace the Redis cache with Dragonfly to reduce cost.",
        author="carol",
        url=None,
        timestamp=datetime(2026, 3, 19, 9, 0, 0),
        metadata_json=None,
    )
    candidates = [
        SemanticCandidate(
            decision_id=7,
            title="Use Redis Cache",
            problem="Latency too high",
            chosen_option="Use Redis as cache only",
            tradeoffs="Extra dependency",
            score=3.2,
            created_at=datetime(2026, 3, 18, 9, 0, 0),
        )
    ]

    result = classify_semantic_drift(artifact=artifact, candidates=candidates)

    assert result is not None
    assert result.alert_type == "possible_supersession"
    assert result.confidence_label == "medium"
    assert "being replaced" in result.summary


def test_classifier_emits_needs_review_for_exploration_language() -> None:
    artifact = Artifact(
        id=2,
        workspace_id=1,
        type="issue",
        source_id="3",
        repo="org/repo",
        title="Evaluate Redis alternatives",
        content="This RFC will evaluate alternatives to the Redis cache for lower cost.",
        author="dana",
        url=None,
        timestamp=datetime(2026, 3, 19, 9, 0, 0),
        metadata_json=None,
    )
    candidates = [
        SemanticCandidate(
            decision_id=8,
            title="Use Redis Cache",
            problem="Latency too high",
            chosen_option="Use Redis as cache only",
            tradeoffs="Extra dependency",
            score=2.4,
            created_at=datetime(2026, 3, 18, 9, 0, 0),
        )
    ]

    result = classify_semantic_drift(artifact=artifact, candidates=candidates)

    assert result is not None
    assert result.alert_type == "needs_review"
    assert result.confidence_label == "low"
    assert "changes or reinforces" in result.summary


def test_classifier_downgrades_broad_changelog_like_artifact_to_needs_review() -> None:
    artifact = Artifact(
        id=4,
        workspace_id=1,
        type="doc",
        source_id="CHANGELOG.md",
        repo="org/repo",
        title="CHANGELOG",
        content="This release notes entry says we should replace the Redis cache with Dragonfly for lower cost.",
        author="maintainer",
        url=None,
        timestamp=datetime(2026, 3, 20, 9, 0, 0),
        metadata_json={"path": "CHANGELOG.md", "signal_category": "release_notes"},
    )
    candidates = [
        SemanticCandidate(
            decision_id=10,
            title="Use Redis Cache",
            problem="Latency too high",
            chosen_option="Use Redis as cache only",
            tradeoffs="Extra dependency",
            score=3.0,
            created_at=datetime(2026, 3, 18, 9, 0, 0),
        )
    ]

    result = classify_semantic_drift(artifact=artifact, candidates=candidates)

    assert result is not None
    assert result.alert_type == "needs_review"


def test_classifier_requires_more_than_generic_supersession_marker() -> None:
    artifact = Artifact(
        id=5,
        workspace_id=1,
        type="issue",
        source_id="5",
        repo="org/repo",
        title="Redis cache follow-up",
        content="This note mentions replace work around the Redis cache but does not explain what replaces the prior choice.",
        author="erin",
        url=None,
        timestamp=datetime(2026, 3, 20, 9, 0, 0),
        metadata_json=None,
    )
    candidates = [
        SemanticCandidate(
            decision_id=11,
            title="Use Redis Cache",
            problem="Latency too high",
            chosen_option="Use Redis as cache only",
            tradeoffs="Extra dependency",
            score=3.0,
            created_at=datetime(2026, 3, 18, 9, 0, 0),
        )
    ]

    result = classify_semantic_drift(artifact=artifact, candidates=candidates)

    assert result is None


def test_classifier_downgrades_implementation_substitution_to_needs_review() -> None:
    artifact = Artifact(
        id=6,
        workspace_id=1,
        type="pull_request",
        source_id="6",
        repo="browser-use/browser-use",
        title="Feature Request: Use cloakbrowser replace playwright",
        content=(
            "Feature Request: Use cloakbrowser replace playwright while keeping HTTP-based downloads for remote browsers "
            "and agent status tracking intact."
        ),
        author="erin",
        url=None,
        timestamp=datetime(2026, 3, 20, 9, 0, 0),
        metadata_json=None,
    )
    candidates = [
        SemanticCandidate(
            decision_id=12,
            title="Enable HTTP-based downloads for remote browsers with agent status tracking",
            problem="Remote browser downloads need richer progress and status handling.",
            chosen_option="Use HTTP-based downloads with explicit remote-browser status tracking.",
            tradeoffs="Adds transport complexity and more operational states to review.",
            score=3.0,
            created_at=datetime(2026, 3, 18, 9, 0, 0),
        )
    ]

    result = classify_semantic_drift(artifact=artifact, candidates=candidates)

    assert result is not None
    assert result.alert_type == "needs_review"
    assert "implementation-level substitution" in result.summary


def test_classifier_downgrades_bugfix_heavy_replacement_language_to_needs_review() -> None:
    artifact = Artifact(
        id=7,
        workspace_id=1,
        type="pull_request",
        source_id="7",
        repo="browser-use/browser-use",
        title="fix: cookie persistence bugs + comprehensive tests",
        content=(
            "This fix replaces the previous HTTP-based remote browser downloads flow with a more reliable "
            "cookie transfer path while keeping agent status tracking intact."
        ),
        author="erin",
        url=None,
        timestamp=datetime(2026, 3, 20, 9, 0, 0),
        metadata_json=None,
    )
    candidates = [
        SemanticCandidate(
            decision_id=13,
            title="Enable HTTP-based downloads for remote browsers with agent status tracking",
            problem="Remote browser downloads need richer progress and status handling.",
            chosen_option="Use HTTP-based downloads with explicit remote-browser status tracking.",
            tradeoffs="Adds transport complexity and more operational states to review.",
            score=3.0,
            created_at=datetime(2026, 3, 18, 9, 0, 0),
        )
    ]

    result = classify_semantic_drift(artifact=artifact, candidates=candidates)

    assert result is not None
    assert result.alert_type == "needs_review"


def test_classifier_downgrades_bugfix_with_deprecated_api_language_to_needs_review() -> None:
    artifact = Artifact(
        id=9,
        workspace_id=1,
        type="pull_request",
        source_id="9",
        repo="browser-use/browser-use",
        title="fix: cookie persistence bugs + comprehensive tests",
        content=(
            "Fixes cookie/storage state persistence and clear_cookies() routing. "
            "The fix replaces deprecated API usage, adds startup retries, and adds a comprehensive test suite."
        ),
        author="erin",
        url=None,
        timestamp=datetime(2026, 3, 20, 9, 0, 0),
        metadata_json=None,
    )
    candidates = [
        SemanticCandidate(
            decision_id=15,
            title="Enable HTTP-based downloads for remote browsers with agent status tracking",
            problem="Remote browser downloads need richer progress and status handling.",
            chosen_option="Use HTTP-based downloads with explicit remote-browser status tracking.",
            tradeoffs="Adds transport complexity and more operational states to review.",
            score=3.0,
            created_at=datetime(2026, 3, 18, 9, 0, 0),
        )
    ]

    result = classify_semantic_drift(artifact=artifact, candidates=candidates)

    assert result is not None
    assert result.alert_type == "needs_review"


def test_classifier_downgrades_lifecycle_fix_replacement_language_to_needs_review() -> None:
    artifact = Artifact(
        id=8,
        workspace_id=1,
        type="pull_request",
        source_id="8",
        repo="browser-use/browser-use",
        title="fix: preserve CDP WebSocket connections on Agent.close() with keep_alive=True",
        content=(
            "This fix replaces the previous keep_alive close behavior with a safer shutdown path "
            "while preserving websocket connections and the broader keep_alive decision."
        ),
        author="erin",
        url=None,
        timestamp=datetime(2026, 3, 20, 9, 0, 0),
        metadata_json=None,
    )
    candidates = [
        SemanticCandidate(
            decision_id=14,
            title="Gracefully stop browser session on agent close with keep_alive=True to prevent asyncio deadlock",
            problem="Agent shutdown can deadlock when keep_alive=True.",
            chosen_option="Update Agent.close() to call await self.browser_session.stop() when keep_alive is True.",
            tradeoffs="Adds an extra shutdown step but prevents deadlock.",
            score=3.0,
            created_at=datetime(2026, 3, 18, 9, 0, 0),
        )
    ]

    result = classify_semantic_drift(artifact=artifact, candidates=candidates)

    assert result is not None
    assert result.alert_type == "needs_review"


def test_classifier_returns_none_when_signal_is_weak() -> None:
    artifact = Artifact(
        id=3,
        workspace_id=1,
        type="issue",
        source_id="4",
        repo="org/repo",
        title="Update cache TTL",
        content="Tune the cache TTL from five minutes to ten minutes.",
        author="erin",
        url=None,
        timestamp=datetime(2026, 3, 19, 9, 0, 0),
        metadata_json=None,
    )
    candidates = [
        SemanticCandidate(
            decision_id=9,
            title="Use Redis Cache",
            problem="Latency too high",
            chosen_option="Use Redis as cache only",
            tradeoffs="Extra dependency",
            score=1.0,
            created_at=datetime(2026, 3, 18, 9, 0, 0),
        )
    ]

    assert classify_semantic_drift(artifact=artifact, candidates=candidates) is None
