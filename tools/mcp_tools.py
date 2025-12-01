# tools/mcp_tools.py
# -------------------------------------------------------------
# MCP Toolsets (Windows-safe)
# -------------------------------------------------------------

import platform
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StdioConnectionParams,
)
from mcp import StdioServerParameters


print("[TOOLS:MCP] Initializing MCP toolsets...")


# -------------------------------------------------------------
# 1. MCP FILE TOOLSET (Safe)
# -------------------------------------------------------------
def build_file_toolset():
    print("[TOOLS:MCP] Building filesystem toolset...")
    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem"],
            ),
            timeout=45,
        )
    )


mcp_file_toolset = build_file_toolset()


# -------------------------------------------------------------
# 2. MCP HTTP TOOLSET (Disabled by default)
# -------------------------------------------------------------
mcp_http_toolset = None  # Enable only if you create your own MCP microservice


# -------------------------------------------------------------
# 3. MCP SHELL TOOLSET (DISABLED ON WINDOWS)
# -------------------------------------------------------------
if platform.system().lower() == "windows":
    print("[TOOLS:MCP] Shell toolset disabled on Windows.")
    mcp_shell_toolset = None
else:
    mcp_shell_toolset = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-shell"],
                tool_filter=["runCommand"],
            ),
            timeout=30,
        )
    )
    print("[TOOLS:MCP] Shell toolset enabled.")

__all__ = [
    "mcp_file_toolset",
    "mcp_http_toolset",
    "mcp_shell_toolset",
]
