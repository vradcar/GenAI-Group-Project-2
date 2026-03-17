"""
CodingAgent — Person 2 (Agentic Loop + Reasoning) owns the loop implementation.

Interface contract with Person 3 (CLI + Tool Runtime):
  - tool_runtime.dispatch(ToolCall) -> ToolResult  is the sole execution path
  - The loop should call tool_runtime.dispatch() for EVERY tool invocation so
    that confirm/auto gating and status indicators work correctly.
"""

from forgepilot.local_tools import LocalTools
from forgepilot.mcp_client import MCPClient
from forgepilot.providers import LLMProvider

# ToolRuntime is optional at import time to avoid circular deps;
# type-hint as string and import lazily.
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from forgepilot.tool_runtime import ToolRuntime


class CodingAgent:
    def __init__(
        self,
        provider: LLMProvider,
        tools: LocalTools,
        mcp_client: MCPClient,
        tool_runtime: "ToolRuntime | None" = None,
    ) -> None:
        self.provider = provider
        self.tools = tools
        self.mcp_client = mcp_client
        self.tool_runtime = tool_runtime  # Person 3 provides this; Person 2 uses it

    def run_task(self, task: str, max_steps: int = 5) -> str:
        self.mcp_client.load()
        thought = self.provider.complete(task)
        summary_lines = [
            f"Task: {task}",
            f"Thought: {thought}",
            f"Available MCP servers: {len(self.mcp_client.list_servers())}",
            f"Available MCP tools: {len(self.mcp_client.list_tools())}",
            f"Loop budget: {max_steps} steps",
            "Status: Template scaffold ready; implement full tool-calling loop next.",
        ]
        return "\n".join(summary_lines)
