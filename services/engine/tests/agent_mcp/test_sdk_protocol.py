"""MCP Python SDK v2 contract smoke, run by the opt-in pinned CI step."""
from __future__ import annotations

import httpx
import pytest

pytest.importorskip("mcp")
from mcp import Client

from app.mcp.bridge import BridgeSettings, DecisionBridge
from app.mcp.server import create_server


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_sdk_v2_tool_discovery_and_calls_without_network():
    received = []

    def mock_engine(request: httpx.Request) -> httpx.Response:
        received.append(request)
        assert request.headers["x-decisionatlas-session-token"] == "short-lived-test-token"
        assert request.url.path == "/decisions"
        assert request.url.params["workspace_slug"] == "project-docs"
        assert request.url.params["review_state"] == "accepted"
        return httpx.Response(200, json=[
            {
                "id": 1, "review_state": "accepted", "title": "Keep migration history",
                "chosen_option": "Versioned migrations",
                "review_evidence": {
                    "source_ref_count": 1,
                    "source_ref_preview": [{"quote": "Documented in ADR", "url": "https://example.org/adr"}],
                },
            },
            {"id": 2, "review_state": "candidate", "title": "Disable authentication"},
        ])

    settings = BridgeSettings("http://127.0.0.1:8000", "project-docs", "short-lived-test-token")
    http = httpx.Client(base_url=settings.api_url, transport=httpx.MockTransport(mock_engine))
    server = create_server(DecisionBridge(settings, client=http))

    async with Client(server, raise_exceptions=True) as client:
        listed = await client.list_tools()
        assert {tool.name for tool in listed.tools} == {
            "project_status", "list_project_decisions",
            "search_project_decisions", "get_decision_evidence",
        }
        result = await client.call_tool("project_status", {})
        assert not result.is_error
        assert result.structured_content["accepted_count"] == 1

        decisions = await client.call_tool("list_project_decisions", {"limit": 10})
        assert not decisions.is_error
        assert [d["decision_id"] for d in decisions.structured_content["items"]] == [1]

        search = await client.call_tool("search_project_decisions", {"query": "migration"})
        assert not search.is_error
        assert search.structured_content["items"][0]["decision_id"] == 1

        denied = await client.call_tool("get_decision_evidence", {"decision_id": 2})
        assert not denied.is_error
        assert denied.structured_content["status"] == "not_accepted_or_not_visible"

    assert len(received) == 4
