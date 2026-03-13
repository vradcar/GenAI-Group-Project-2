import json
from pathlib import Path
from typing import Any


class MCPClient:
    def __init__(self, config_path: str) -> None:
        self.config_path = Path(config_path)
        self._config: dict[str, Any] = {"servers": []}

    def load(self) -> None:
        if self.config_path.exists():
            self._config = json.loads(self.config_path.read_text(encoding="utf-8"))

    def list_servers(self) -> list[dict[str, Any]]:
        return list(self._config.get("servers", []))

    def list_tools(self) -> list[dict[str, Any]]:
        tools: list[dict[str, Any]] = []
        for server in self._config.get("servers", []):
            tools.append(
                {
                    "server": server.get("name", "unknown"),
                    "name": f"{server.get('name', 'unknown')}.template_tool",
                    "description": "Template tool loaded from MCP server config",
                }
            )
        return tools

    def call_tool(self, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        return {
            "tool": tool_name,
            "args": args,
            "result": "Template MCP result. Replace with SDK calls.",
        }
