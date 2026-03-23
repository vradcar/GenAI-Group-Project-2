"""
Tool Runtime — Person 3 (CLI + Tool Runtime)

Wraps local tool execution with:
- Rich-formatted start/finish status indicators
- Confirm mode: prompts user y/n before each tool call
- Auto mode: executes immediately (still prints the call for visibility)
"""

import asyncio

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

from forgepilot.local_tools import LocalTools
from forgepilot.mcp_client import MCPClient
from forgepilot.types import ToolCall, ToolResult

console = Console()

# Maps tool names to LocalTools methods
_LOCAL_TOOL_NAMES = {"read_file", "write_file", "run_shell"}


class ToolRuntime:
    def __init__(
        self,
        local_tools: LocalTools,
        execution_mode: str = "confirm",
        mcp_client: MCPClient | None = None,
    ) -> None:
        self.local_tools = local_tools
        self.execution_mode = execution_mode  # "confirm" | "auto"
        self.mcp_client = mcp_client

    # Public interface for the agent loop (Person 2 calls this)
  
    def dispatch(self, tool_call: ToolCall) -> ToolResult:
        """Execute a ToolCall, printing visibility markers and gating on mode."""
        args_display = ", ".join(
            f"{k}={repr(v)}" for k, v in tool_call.arguments.items()
        )
        console.print(
            f"\n[bold yellow]>> TOOL CALL[/bold yellow]  "
            f"[bold cyan]{tool_call.name}[/bold cyan]({args_display})"
        )

        if self.execution_mode == "confirm":
            approved = Confirm.ask("   Execute?", default=True)
            if not approved:
                console.print("[dim]   → Skipped by user.[/dim]")
                return ToolResult(name=tool_call.name, success=False, output="Skipped by user.")

        try:
            return asyncio.run(self.dispatch_async(tool_call))
        except RuntimeError:
            return self._run(tool_call)

    async def dispatch_async(self, tool_call: ToolCall) -> ToolResult:
        args_display = ", ".join(
            f"{k}={repr(v)}" for k, v in tool_call.arguments.items()
        )
        console.print(
            f"\n[bold yellow]>> TOOL CALL[/bold yellow]  "
            f"[bold cyan]{tool_call.name}[/bold cyan]({args_display})"
        )

        if self.execution_mode == "confirm":
            approved = Confirm.ask("   Execute?", default=True)
            if not approved:
                console.print("[dim]   → Skipped by user.[/dim]")
                return ToolResult(name=tool_call.name, success=False, output="Skipped by user.")

        if tool_call.name in _LOCAL_TOOL_NAMES:
            return self._run(tool_call)

        if self.mcp_client is not None:
            try:
                result = await self.mcp_client.call_tool(tool_call.name, tool_call.arguments)
                output = result.get("result") if result.get("success") else result.get("error")
                output_str = str(output or "")
                success = bool(result.get("success"))
                self._print_tool_done(tool_call.name, output_str, success=success)
                return ToolResult(name=tool_call.name, success=success, output=output_str)
            except Exception as exc:
                console.print(
                    f"[bold red]!! TOOL ERROR[/bold red]  "
                    f"[bold cyan]{tool_call.name}[/bold cyan]: {exc}"
                )
                return ToolResult(name=tool_call.name, success=False, output=str(exc))

        return ToolResult(
            name=tool_call.name,
            success=False,
            output=f"Unknown tool '{tool_call.name}'. Register local or MCP tools.",
        )

   # Internal execution
   
    def _run(self, tool_call: ToolCall) -> ToolResult:
        try:
            if tool_call.name in _LOCAL_TOOL_NAMES:
                method = getattr(self.local_tools, tool_call.name)
                output = method(**tool_call.arguments)
            else:
                raise ValueError(
                    f"Unknown tool '{tool_call.name}'. "
                    f"Register MCP tools via MCPClient."
                )

            output_str = str(output)
            self._print_tool_done(tool_call.name, output_str, success=True)
            return ToolResult(name=tool_call.name, success=True, output=output_str)

        except Exception as exc:
            console.print(
                f"[bold red]!! TOOL ERROR[/bold red]  "
                f"[bold cyan]{tool_call.name}[/bold cyan]: {exc}"
            )
            return ToolResult(name=tool_call.name, success=False, output=str(exc))

    def _print_tool_done(self, tool_name: str, output: str, success: bool) -> None:
        color = "green" if success else "red"
        label = "OK TOOL DONE" if success else "!! TOOL ERROR"
        console.print(f"[bold {color}]{label}[/bold {color}]  [bold cyan]{tool_name}[/bold cyan]")
        if output:
            console.print(
                Panel(
                    output[:800],
                    title="[dim]output[/dim]",
                    border_style=f"dim {color}",
                    expand=False,
                )
            )
