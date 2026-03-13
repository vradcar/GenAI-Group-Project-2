from forgepilot.local_tools import LocalTools
from forgepilot.mcp_client import MCPClient
from forgepilot.providers import LLMProvider


class CodingAgent:
    def __init__(self, provider: LLMProvider, tools: LocalTools, mcp_client: MCPClient) -> None:
        self.provider = provider
        self.tools = tools
        self.mcp_client = mcp_client

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
