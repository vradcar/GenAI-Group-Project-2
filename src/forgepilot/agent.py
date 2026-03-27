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
import re
from pathlib import Path
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
            "Use MCP tools when their names appear in available tools context. "
            "For documentation tasks (README/report/markdown): write complete, concrete content with clear headings, "
            "project-specific details, and runnable commands; avoid placeholders and generic filler."
        )

    def _extract_json(self, text: str) -> dict[str, Any]:
        text = text.strip()

        fenced = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text, re.IGNORECASE)
        if fenced:
            text = fenced.group(1).strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            if start >= 0:
                depth = 0
                end = -1
                for index, char in enumerate(text[start:], start=start):
                    if char == "{":
                        depth += 1
                    elif char == "}":
                        depth -= 1
                        if depth == 0:
                            end = index
                            break
                if end > start:
                    return json.loads(text[start : end + 1])
            raise

    def _coerce_structured_response(
        self, user_prompt: str, raw: str
    ) -> dict[str, Any] | None:
        try:
            return self._extract_json(raw)
        except Exception:
            repair_prompt = (
                "Convert the following assistant output into strict JSON using this exact schema: "
                '{"thought": str, "action": {"tool": str, "args": object} | null, '
                '"final": str | null}. Return JSON only.\n\n'
                f"ORIGINAL OUTPUT:\n{raw}"
            )
            repaired = self.provider.complete(repair_prompt, system_prompt=self._system_prompt())
            try:
                return self._extract_json(repaired)
            except Exception:
                return None

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
        wrote_markdown_files: set[str] = set()
        reviewed_markdown_files: set[str] = set()
        task_lower = task.lower()
        requires_doc_quality_review = any(
            keyword in task_lower
            for keyword in ("markdown", "readme", ".md", "report", "documentation")
        )

        async with self.mcp_client:
            mcp_tools = self.mcp_client.list_tools()
            available_mcp_tools = [tool["name"] for tool in mcp_tools]

            if mcp_tools:
                tool_signatures: list[str] = []
                for tool in mcp_tools[:20]:
                    schema = tool.get("input_schema", {})
                    props = schema.get("properties", {})
                    required = schema.get("required", [])
                    params = []
                    for pname in props:
                        marker = " (required)" if pname in required else ""
                        params.append(f"{pname}{marker}")
                    sig = f"{tool['name']}({', '.join(params)})"
                    tool_signatures.append(sig)
                history.append(
                    "available_mcp_tools:\n" + "\n".join(tool_signatures)
                )

            if requires_doc_quality_review:
                mentioned_files = re.findall(r"([A-Za-z0-9_./\\-]+\.py)", task)
                workspace_root = Path(self.tools.workspace_root)
                for relative_path in mentioned_files[:6]:
                    try:
                        normalized = relative_path.replace("\\", "/")
                        target = (workspace_root / normalized).resolve()
                        if target.exists() and target.is_file():
                            excerpt = target.read_text(encoding="utf-8")[:1200]
                            history.append(
                                f"grounding {normalized}:\n{excerpt}"
                            )
                    except Exception:
                        continue

            for step in range(1, max_steps + 1):
                user_prompt = self._build_user_prompt(task=task, step=step, history=history)
                raw = self.provider.complete(user_prompt, system_prompt=self._system_prompt())

                payload = self._coerce_structured_response(user_prompt=user_prompt, raw=raw)
                if payload is None:
                    return self._fallback_text(task=task, max_steps=max_steps)

                thought = str(payload.get("thought") or "")
                final_text = payload.get("final")
                action = payload.get("action")

                if isinstance(final_text, str) and "\"action\"" in final_text and "{" in final_text:
                    try:
                        embedded = self._extract_json(final_text)
                        embedded_action = embedded.get("action")
                        if isinstance(embedded_action, dict):
                            embedded_thought = embedded.get("thought")
                            if isinstance(embedded_thought, str) and embedded_thought.strip():
                                thought = embedded_thought.strip()
                            action = embedded_action
                            embedded_final = embedded.get("final")
                            if isinstance(embedded_final, str):
                                final_text = embedded_final
                            else:
                                final_text = None
                    except Exception:
                        pass

                if thought:
                    history.append(f"step {step} thought: {thought}")

                if isinstance(final_text, str) and final_text.strip():
                    if requires_doc_quality_review:
                        pending_review = sorted(wrote_markdown_files - reviewed_markdown_files)
                        if pending_review:
                            history.append(
                                "step "
                                f"{step} quality gate: before final, read and refine these files: "
                                + ", ".join(pending_review)
                            )
                            continue

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
                if isinstance(args, str):
                    args = {"path": args}
                if not isinstance(tool_name, str) or not isinstance(args, dict):
                    history.append(f"step {step} invalid action payload")

                    if requires_doc_quality_review:
                        pending_review = sorted(wrote_markdown_files - reviewed_markdown_files)
                        if pending_review and self.tool_runtime is not None:
                            read_tool_name = (
                                "filesystem__read_file"
                                if any(
                                    name.strip().lower() == "filesystem__read_file"
                                    for name in available_mcp_tools
                                )
                                else "read_file"
                            )
                            auto_read_call = ToolCall(
                                name=read_tool_name,
                                arguments={"path": pending_review[0]},
                            )
                            dispatch_async = getattr(self.tool_runtime, "dispatch_async", None)
                            if callable(dispatch_async):
                                auto_result = await dispatch_async(auto_read_call)
                            else:
                                auto_result = self.tool_runtime.dispatch(auto_read_call)
                            reviewed_markdown_files.add(pending_review[0])
                            history.append(
                                f"step {step} auto-review {auto_result.name} success={auto_result.success} "
                                f"output={auto_result.output[:500]}"
                            )
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

                path_arg = args.get("path")
                if isinstance(path_arg, str) and path_arg.lower().endswith(".md"):
                    normalized_tool = tool_name.strip().lower()
                    if normalized_tool.endswith("write_file"):
                        wrote_markdown_files.add(path_arg)
                    if normalized_tool.endswith("read_file"):
                        reviewed_markdown_files.add(path_arg)

                preview_limit = 8000 if tool_name.strip().lower().endswith("read_file") else 2000
                result_preview = tool_result.output[:preview_limit]
                if len(tool_result.output) > preview_limit:
                    result_preview += "\n...[truncated by agent preview]"
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
