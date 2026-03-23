"""
CodingAgent — Person 2 (Agentic Loop + Reasoning) owns the loop implementation.

Interface contract with Person 3 (CLI + Tool Runtime):
  - tool_runtime.dispatch(ToolCall) -> ToolResult  is the sole execution path
  - The loop should call tool_runtime.dispatch() for EVERY tool invocation so
    that confirm/auto gating and status indicators work correctly.
"""

from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, Any

from forgepilot.local_tools import LocalTools
from forgepilot.mcp_client import MCPClient
from forgepilot.providers import LLMProvider
from forgepilot.types import ToolCall

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

    def _system_prompt(self) -> str:
        return (
            "You are an autonomous coding assistant. "
            "Decide one action at a time and return strict JSON only with this schema: "
            "{\"thought\": str, \"action\": {\"tool\": str, \"args\": object} | null, "
            "\"final\": str | null}. "
            "When you need file or shell info, use an action. "
            "When done, set final and action=null. "
            "Available local tools: read_file(path), write_file(path, content), run_shell(command). "
            "Use MCP tools when their names appear in available tools context."
        )

    def _extract_json(self, text: str) -> dict[str, Any]:
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start >= 0 and end > start:
                return json.loads(text[start : end + 1])
            raise

    def _build_user_prompt(self, task: str, step: int, history: list[str]) -> str:
        recent = "\n".join(history[-6:]) if history else "(none yet)"
        return (
            f"TASK:\n{task}\n\n"
            f"STEP: {step}\n"
            "RECENT OBSERVATIONS:\n"
            f"{recent}\n\n"
            "Return JSON only."
        )

    def _fallback_text(self, task: str, max_steps: int) -> str:
        thought = self.provider.complete(task)
        summary_lines = [
            f"Task: {task}",
            f"Thought: {thought}",
            f"Available MCP servers: {len(self.mcp_client.list_servers())}",
            f"Available MCP tools: {len(self.mcp_client.list_tools())}",
            f"Loop budget: {max_steps} steps",
            "Status: Agent response was unstructured; returning provider output.",
        ]
        return "\n".join(summary_lines)

    def run_task(self, task: str, max_steps: int = 5) -> str:
        return asyncio.run(self._run_task_async(task=task, max_steps=max_steps))

    async def _run_task_async(self, task: str, max_steps: int = 5) -> str:
        history: list[str] = []

        async with self.mcp_client:
            available_mcp_tools = [tool["name"] for tool in self.mcp_client.list_tools()]

            if available_mcp_tools:
                history.append(
                    "available_mcp_tools: " + ", ".join(available_mcp_tools[:20])
                )

            for step in range(1, max_steps + 1):
                user_prompt = self._build_user_prompt(task=task, step=step, history=history)
                raw = self.provider.complete(user_prompt, system_prompt=self._system_prompt())

                try:
                    payload = self._extract_json(raw)
                except Exception:
                    return self._fallback_text(task=task, max_steps=max_steps)

                thought = str(payload.get("thought") or "")
                final_text = payload.get("final")
                action = payload.get("action")

                if thought:
                    history.append(f"step {step} thought: {thought}")

                if isinstance(final_text, str) and final_text.strip():
                    history.append(f"step {step} final: {final_text.strip()}")
                    return "\n".join(
                        [
                            f"Task: {task}",
                            f"Final: {final_text.strip()}",
                            "Status: Completed within step budget.",
                        ]
                    )

                if not isinstance(action, dict):
                    continue

                tool_name = action.get("tool")
                args = action.get("args")
                if not isinstance(tool_name, str) or not isinstance(args, dict):
                    history.append(f"step {step} invalid action payload")
                    continue

                if self.tool_runtime is None:
                    history.append(f"step {step} runtime missing for action {tool_name}")
                    continue

                dispatch_async = getattr(self.tool_runtime, "dispatch_async", None)
                if callable(dispatch_async):
                    tool_result = await dispatch_async(ToolCall(name=tool_name.strip(), arguments=args))
                else:
                    tool_result = self.tool_runtime.dispatch(
                        ToolCall(name=tool_name.strip(), arguments=args)
                    )
                result_preview = tool_result.output[:500]
                history.append(
                    f"step {step} tool {tool_result.name} success={tool_result.success} output={result_preview}"
                )

        return "\n".join(
            [
                f"Task: {task}",
                "Status: Step budget exhausted before final answer.",
                "Recent observations:",
                *history[-5:],
            ]
        )
