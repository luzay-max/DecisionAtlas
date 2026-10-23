"""The stdio SDK entrypoint registers only four read-only tools.

This test uses a tiny SDK double so the existing Engine uv environment does
not silently acquire an MCP dependency; a real-host integration test is still
required for release.
"""
from __future__ import annotations

import sys
from types import ModuleType

import httpx

from app.mcp.bridge import BridgeSettings, DecisionBridge
from app.mcp.server import create_server


def test_mcp_tools_register_with_readonly_annotations(monkeypatch) -> None:
    registered = {}

    class MCPServer:
        def __init__(self, name: str):
            self.name = name

        def tool(self, *, annotations, structured_output: bool = False):
            assert annotations.read_only_hint is True
            assert annotations.open_world_hint is False
            assert structured_output is True

            def register(fn):
                registered[fn.__name__] = fn
                return fn

            return register

    class Annotations:
        def __init__(self, *, read_only_hint: bool, open_world_hint: bool):
            self.read_only_hint = read_only_hint
            self.open_world_hint = open_world_hint

    mcp = ModuleType("mcp")
    server_module = ModuleType("mcp.server")
    types_module = ModuleType("mcp.types")
    server_module.MCPServer = MCPServer
    types_module.ToolAnnotations = Annotations
    monkeypatch.setitem(sys.modules, "mcp", mcp)
    monkeypatch.setitem(sys.modules, "mcp.server", server_module)
    monkeypatch.setitem(sys.modules, "mcp.types", types_module)

    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(str(request.url))
        return httpx.Response(200, json=[{
            "id": 7,
            "title": "Use PostgreSQL",
            "problem": "Concurrency",
            "review_state": "accepted",
            "chosen_option": "PostgreSQL",
            "review_evidence": {"source_ref_count": 1, "source_ref_preview": []},
        }])

    settings = BridgeSettings("http://127.0.0.1:8000", "project-demo", "test-token")
    client = httpx.Client(
        base_url=settings.api_url,
        transport=httpx.MockTransport(handler),
    )
    result = create_server(DecisionBridge(settings, client=client))
    assert result.name == "DecisionAtlas Project Decisions"
    assert set(registered) == {
        "project_status", "list_project_decisions",
        "search_project_decisions", "get_decision_evidence",
    }
    assert registered["project_status"]()["accepted_count"] == 1
    assert registered["list_project_decisions"](1)["items"][0]["review_state"] == "accepted"
    assert registered["search_project_decisions"]("PostgreSQL")["items"][0]["decision_id"] == 7
    assert len(calls) == 3
