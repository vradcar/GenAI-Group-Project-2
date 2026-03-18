"""
Tool Runtime — Person 3 (CLI + Tool Runtime)

Wraps local tool execution with:
- Rich-formatted start/finish status indicators
- Confirm mode: prompts user y/n before each tool call
- Auto mode: executes immediately (still prints the call for visibility)
"""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

from forgepilot.local_tools import LocalTools
from forgepilot.types import ToolCall, ToolResult

console = Console()

# Maps tool names to LocalTools methods
_LOCAL_TOOL_NAMES = {"read_file", "write_file", "run_shell"}


class ToolRuntime:
    def __init__(self, local_tools: LocalTools, execution_mode: str = "confirm") -> None:
        self.local_tools = local_tools
        self.execution_mode = execution_mode  # "confirm" | "auto"

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

        return self._run(tool_call)

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

            console.print(
                f"[bold green]OK TOOL DONE[/bold green]  "
                f"[bold cyan]{tool_call.name}[/bold cyan]"
            )
            output_str = str(output)
            if output_str:
                console.print(
                    Panel(
                        output_str[:800],
                        title="[dim]output[/dim]",
                        border_style="dim green",
                        expand=False,
                    )
                )
            return ToolResult(name=tool_call.name, success=True, output=output_str)

        except Exception as exc:
            console.print(
                f"[bold red]!! TOOL ERROR[/bold red]  "
                f"[bold cyan]{tool_call.name}[/bold cyan]: {exc}"
            )
            return ToolResult(name=tool_call.name, success=False, output=str(exc))
