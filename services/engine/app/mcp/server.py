"""DecisionAtlas read-only MCP v2 stdio server.

Launch with uv run --with mcp==2.2.0 python -m app.mcp.server
from services/engine after configuring workspace and session in environment.
"""
from __future__ import annotations

from typing import Any

from app.mcp.bridge import BridgeSettings, DecisionBridge


def create_server(bridge: DecisionBridge | None = None):
    # Lazy import: Engine tests do not add MCP as a core production dependency.
    # This module requires the official MCP Python SDK v2 when launched.
    from mcp.server import MCPServer
    from mcp.types import ToolAnnotations

    source = bridge or DecisionBridge(BridgeSettings.from_env())
    server = MCPServer("DecisionAtlas Project Decisions")
    readonly = ToolAnnotations(read_only_hint=True, open_world_hint=False)

    @server.tool(annotations=readonly, structured_output=True)
    def project_status() -> dict[str, Any]:
        """Check accepted-decision availability in the pre-authorized workspace."""
        return source.project_status()

    @server.tool(annotations=readonly, structured_output=True)
    def list_project_decisions(limit: int = 20) -> dict[str, Any]:
        """Read reviewed, accepted project decisions only (max 50)."""
        return source.list_project_decisions(limit=limit)

    @server.tool(annotations=readonly, structured_output=True)
    def search_project_decisions(query: str, limit: int = 10) -> dict[str, Any]:
        """Find accepted decisions by basic local lexical matching; not semantic search."""
        return source.search_project_decisions(query=query, limit=limit)

    @server.tool(annotations=readonly, structured_output=True)
    def get_decision_evidence(decision_id: int) -> dict[str, Any]:
        """Get cited evidence for an accepted decision in the configured workspace."""
        return source.get_decision_evidence(decision_id=decision_id)

    return server


if __name__ == "__main__":
    create_server().run()  # SDK v2 stdio transport is the default.
