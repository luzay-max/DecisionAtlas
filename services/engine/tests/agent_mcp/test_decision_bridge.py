"""Read-only MCP Engine bridge tests: no network, no MCP SDK dependency."""
from __future__ import annotations

import httpx
import pytest

from app.mcp.bridge import (
    BridgeConfigurationError, BridgeSettings, DecisionBridge, DecisionServiceError,
)


def settings(**env: str) -> BridgeSettings:
    return BridgeSettings.from_env({
        "DECISIONATLAS_MCP_API_URL": "http://127.0.0.1:8000",
        "DECISIONATLAS_MCP_WORKSPACE": "reviewed-project",
        "DECISIONATLAS_MCP_SESSION_TOKEN": "test-session-token",
        **env,
    })


@pytest.mark.parametrize(("key", "value"), [
    ("DECISIONATLAS_MCP_API_URL", "https://evil.example"),
    ("DECISIONATLAS_MCP_API_URL", "http://127.0.0.1"),
    ("DECISIONATLAS_MCP_API_URL", "http://127.0.0.1:8000@evil.example:8000"),
    ("DECISIONATLAS_MCP_API_URL", "http://localhost:8000/private"),
    ("DECISIONATLAS_MCP_API_URL", "http://127.0.0.1:invalid"),
    ("DECISIONATLAS_MCP_API_URL", "http://127.0.0.1:8000?secret=1"),
    ("DECISIONATLAS_MCP_WORKSPACE", "../other-project"),
    ("DECISIONATLAS_MCP_WORKSPACE", ""),
    ("DECISIONATLAS_MCP_SESSION_TOKEN", ""),
    ("DECISIONATLAS_MCP_SESSION_TOKEN", "bad\nheader"),
])
def test_bridge_rejects_untrusted_configuration(key: str, value: str) -> None:
    with pytest.raises(BridgeConfigurationError):
        settings(**{key: value})


def _bridge(records: list[dict], *, evidence: dict | None = None):
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        assert request.headers["x-decisionatlas-session-token"] == "test-session-token"
        if request.url.path == "/decisions":
            assert request.url.params["workspace_slug"] == "reviewed-project"
            assert request.url.params["review_state"] == "accepted"
            return httpx.Response(200, json=records)
        if request.url.path == "/decisions/7":
            return httpx.Response(200, json=evidence or records[0])
        return httpx.Response(404)

    client = httpx.Client(
        base_url="http://127.0.0.1:8000",
        transport=httpx.MockTransport(handler),
    )
    return DecisionBridge(settings(), client=client), calls


def _accepted() -> dict:
    return {
        "id": 7,
        "title": "Use PostgreSQL",
        "review_state": "accepted",
        "problem": "Persistence and concurrency",
        "constraints": "Avoid SQLite for production workloads",
        "chosen_option": "PostgreSQL",
        "review_evidence": {
            "source_ref_count": 1,
            "source_ref_preview": [{"url": "https://example.org/ADR1", "quote": "Use Postgres"}],
        },
    }


def test_status_list_search_and_citations_only_expose_accepted_decisions() -> None:
    approved = _accepted()
    unreviewed = {"id": 10, "title": "Drop authentication", "review_state": "candidate"}
    bridge, calls = _bridge([approved, unreviewed])
    state = bridge.project_status()
    assert state["accepted_count"] == 1
    listed = bridge.list_project_decisions(limit=5)
    assert [x["decision_id"] for x in listed["items"]] == [7]
    assert listed["items"][0]["evidence_status"] == "accepted_with_source_refs"
    hits = bridge.search_project_decisions("PostgreSQL concurrency")
    assert hits["status"] == "matched_accepted"
    assert hits["items"][0]["decision_id"] == 7
    assert bridge.search_project_decisions("completely unrelated")["status"] == "insufficient_evidence"
    # Never fetch arbitrary ids before verifying membership in the accepted workspace list.
    assert bridge.get_decision_evidence(10)["status"] == "not_accepted_or_not_visible"
    assert not any(str(call.url).endswith("/decisions/10") for call in calls)
    evidence = {
        **approved,
        "source_refs": [{
            "artifact_id": 42, "quote": "Selected for migrations",
            "url": "https://example.org/ADR1", "span_start": 3, "span_end": 7,
        }],
    }
    with_evidence, _ = _bridge([approved], evidence=evidence)
    detail = with_evidence.get_decision_evidence(7)
    assert detail["source_refs"][0]["url"] == "https://example.org/ADR1"
    assert detail["advisory_only"]
    assert "session-token" not in str(detail)


def test_acceptance_without_citations_is_marked_unverified() -> None:
    item = {**_accepted(), "review_evidence": {"source_ref_count": 0, "source_ref_preview": []}}
    bridge, _ = _bridge([item], evidence={**item, "source_refs": []})
    assert bridge.list_project_decisions()["items"][0]["evidence_status"] == "accepted_sources_missing"
    assert bridge.get_decision_evidence(7)["status"] == "accepted_sources_missing"


@pytest.mark.parametrize(("status", "expected"), [
    (401, "session"), (403, "not available"), (404, "not available"), (302, "redirected"),
    (500, "HTTP 500"),
])
def test_bridge_backend_error_is_sanitized(status: int, expected: str) -> None:
    client = httpx.Client(
        base_url="http://127.0.0.1:8000",
        transport=httpx.MockTransport(lambda r: httpx.Response(
            status, headers={"location": "http://evil.example"} if status == 302 else {},
            text="secret upstream error body TOKEN=private",
        )),
    )
    bridge = DecisionBridge(settings(), client=client)
    with pytest.raises(DecisionServiceError, match=expected) as caught:
        bridge.list_project_decisions()
    assert "private" not in str(caught.value)
    assert "evil.example" not in str(caught.value)


def test_bridge_rejects_bad_json_and_payload_size() -> None:
    for content in (b"invalid json", b"x" * 2_000_001):
        client = httpx.Client(
            base_url="http://127.0.0.1:8000",
            transport=httpx.MockTransport(lambda r: httpx.Response(200, content=content)),
        )
        with pytest.raises(DecisionServiceError):
            DecisionBridge(settings(), client=client).list_project_decisions()


def test_bridge_limits_tool_inputs() -> None:
    bridge, _ = _bridge([_accepted()])
    with pytest.raises(ValueError):
        bridge.list_project_decisions(100)
    with pytest.raises(ValueError):
        bridge.search_project_decisions("x" * 501)
    with pytest.raises(ValueError):
        bridge.get_decision_evidence(-1)
