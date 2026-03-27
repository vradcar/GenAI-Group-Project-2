"""
CLI entry point — Person 3 (CLI + Tool Runtime)

Commands:
  forgepilot run "<task>"   — execute a single task and exit
  forgepilot repl           — start an interactive REPL session

REPL commands:
  /mode     — toggle between confirm and auto execution mode
  exit|quit — end the session
"""

import typer
from rich.console import Console
from rich.prompt import Prompt

from forgepilot.agent import CodingAgent
from forgepilot.config import Settings, get_settings
from forgepilot.local_tools import LocalTools
from forgepilot.mcp_client import MCPClient
from forgepilot.providers import create_provider
from forgepilot.tool_runtime import ToolRuntime

app = typer.Typer(help="ForgePilot — AI coding assistant")
console = Console()

# Helpers

def _build_agent(settings: Settings) -> tuple[CodingAgent, ToolRuntime]:
    provider = create_provider(settings)
    local_tools = LocalTools(settings.workspace_root)
    mcp_client = MCPClient(settings.mcp_config_path)
    tool_runtime = ToolRuntime(
        local_tools,
        execution_mode=settings.execution_mode,
        mcp_client=mcp_client,
    )
    agent = CodingAgent(
        provider=provider,
        tools=local_tools,
        mcp_client=mcp_client,
        tool_runtime=tool_runtime,
    )
    return agent, tool_runtime


def _print_header(name: str, mode: str) -> None:
    console.print(
        f"[bold cyan]{name}[/bold cyan]  "
        f"mode: [bold yellow]{mode}[/bold yellow]"
    )


def _run_task(agent: CodingAgent, task: str, max_steps: int) -> None:
    console.print("[bold green]Thinking…[/bold green]")
    result = agent.run_task(task=task, max_steps=max_steps)
    console.print(result)

# Commands

@app.command()
def run(
    task: str = typer.Argument(..., help="Coding task to execute"),
    max_steps: int = typer.Option(5, "--max-steps", "-n", help="Step budget"),
) -> None:
    """Execute a single coding task and exit."""
    settings = get_settings()
    agent, _ = _build_agent(settings)

    _print_header(settings.forgepilot_name, settings.execution_mode)
    console.print()

    console.print("[bold green]Thinking…[/bold green]")
    result = agent.run_task(task=task, max_steps=max_steps)
    console.print(result)


@app.command()
def repl(
    max_steps: int = typer.Option(5, "--max-steps", "-n", help="Step budget per task"),
) -> None:
    """Start an interactive REPL session."""
    settings = get_settings()
    agent, tool_runtime = _build_agent(settings)

    _print_header(settings.forgepilot_name, settings.execution_mode)
    console.print(
        "[dim]Commands:  /mode — toggle confirm/auto   |   exit — quit[/dim]\n"
    )

    while True:
        try:
            task = Prompt.ask("[bold cyan]>[/bold cyan]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye.[/dim]")
            break

        task = task.strip()
        if not task:
            continue

        # built-in REPL commands 
        if task.lower() in ("exit", "quit"):
            console.print("[dim]Goodbye.[/dim]")
            break

        if task.lower() == "/mode":
            new_mode = "auto" if tool_runtime.execution_mode == "confirm" else "confirm"
            tool_runtime.execution_mode = new_mode
            console.print(f"[yellow]Execution mode → {new_mode}[/yellow]\n")
            continue

        _run_task(agent, task, max_steps)
        console.print()


if __name__ == "__main__":
    app()
