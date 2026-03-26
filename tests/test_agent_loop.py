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


class RawScriptedProvider:
    def __init__(self, responses: list[str]) -> None:
        self._responses = responses
        self._index = 0

    def complete(self, prompt: str, system_prompt: str | None = None) -> str:
        response = self._responses[min(self._index, len(self._responses) - 1)]
        self._index += 1
        return response

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


def test_agent_parses_fenced_json_response() -> None:
    provider = RawScriptedProvider(
        responses=[
            """I will proceed now.\n```json
{\"thought\":\"Need to write docs\",\"action\":{\"tool\":\"write_file\",\"args\":{\"path\":\"ARCHITECTURE.md\",\"content\":\"# Architecture\"}},\"final\":null}
```""",
            json.dumps(
                {
                    "thought": "Done",
                    "action": None,
                    "final": "Created ARCHITECTURE.md.",
                }
            ),
        ]
    )
    runtime = StubRuntime()

    agent = CodingAgent(
        provider=provider,
        tools=LocalTools("."),
        mcp_client=MCPClient("./configs/mcp.servers.example.json"),
        tool_runtime=runtime,
    )

    result = agent.run_task("Create architecture document", max_steps=4)

    assert len(runtime.calls) == 1
    assert runtime.calls[0].name == "write_file"
    assert "Created ARCHITECTURE.md." in result


def test_markdown_task_requires_review_before_final() -> None:
    provider = ScriptedProvider(
        responses=[
            {
                "thought": "Drafting markdown",
                "action": {
                    "tool": "write_file",
                    "args": {"path": "RAG_REPORT.md", "content": "# Draft"},
                },
                "final": None,
            },
            {
                "thought": "Done",
                "action": None,
                "final": "Completed.",
            },
            {
                "thought": "Reviewing output",
                "action": {
                    "tool": "read_file",
                    "args": {"path": "RAG_REPORT.md"},
                },
                "final": None,
            },
            {
                "thought": "Finalize",
                "action": None,
                "final": "Completed with review.",
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

    result = agent.run_task("Create a markdown report file", max_steps=6)

    assert [call.name for call in runtime.calls] == ["write_file", "read_file"]
    assert "Completed with review." in result


def test_embedded_action_inside_final_is_executed() -> None:
    provider = ScriptedProvider(
        responses=[
            {
                "thought": "Preparing",
                "action": None,
                "final": json.dumps(
                    {
                        "thought": "Need to write deployment file",
                        "action": {
                            "tool": "write_file",
                            "args": {"path": "DEPLOYMENT.md", "content": "updated"},
                        },
                        "final": None,
                    }
                ),
            },
            {
                "thought": "Done",
                "action": None,
                "final": "Applied update.",
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

    result = agent.run_task("Update deployment doc", max_steps=4)

    assert [call.name for call in runtime.calls] == ["write_file"]
    assert "Applied update." in result
