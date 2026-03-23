from __future__ import annotations

import json

from forgepilot.agent import CodingAgent
from forgepilot.local_tools import LocalTools
from forgepilot.mcp_client import MCPClient
from forgepilot.types import ToolCall, ToolResult


class ScriptedProvider:
    def __init__(self, responses: list[dict]) -> None:
        self._responses = responses
        self._index = 0

    def complete(self, prompt: str, system_prompt: str | None = None) -> str:
        response = self._responses[min(self._index, len(self._responses) - 1)]
        self._index += 1
        return json.dumps(response)

    def stream(self, prompt: str, system_prompt: str | None = None):
        yield self.complete(prompt, system_prompt=system_prompt)


class StubRuntime:
    def __init__(self) -> None:
        self.calls: list[ToolCall] = []

    def dispatch(self, tool_call: ToolCall) -> ToolResult:
        self.calls.append(tool_call)
        return ToolResult(name=tool_call.name, success=True, output="ok")


def test_agent_executes_tool_then_finishes() -> None:
    provider = ScriptedProvider(
        responses=[
            {
                "thought": "Need to inspect a file",
                "action": {"tool": "read_file", "args": {"path": "README.md"}},
                "final": None,
            },
            {
                "thought": "Done",
                "action": None,
                "final": "Task completed successfully.",
            },
        ]
    )
    runtime = StubRuntime()

    agent = CodingAgent(
        provider=provider,
        tools=LocalTools("."),
        mcp_client=MCPClient("./configs/mcp.servers.example.json"),
        tool_runtime=runtime,
    )

    result = agent.run_task("Summarize README", max_steps=4)

    assert len(runtime.calls) == 1
    assert runtime.calls[0].name == "read_file"
    assert "Task completed successfully." in result
