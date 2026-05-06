from __future__ import annotations

import os

from dotenv import load_dotenv
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

load_dotenv()

KPI_MCP_URL = os.getenv("KPI_MCP_URL", "http://127.0.0.1:8091/mcp")


def kpi_toolset(tool_filter: list[str] | None = None) -> McpToolset:
    return McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=KPI_MCP_URL,
            timeout=60.0,
        ),
        tool_filter=tool_filter,
    )

