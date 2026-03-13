import typer
from rich.console import Console

from forgepilot.agent import CodingAgent
from forgepilot.config import get_settings
from forgepilot.local_tools import LocalTools
from forgepilot.mcp_client import MCPClient
from forgepilot.providers import create_provider

app = typer.Typer(help="ForgePilot CLI coding assistant")
console = Console()


@app.command()
def run(task: str, max_steps: int = 5) -> None:
    settings = get_settings()
    provider = create_provider(settings)
    local_tools = LocalTools(settings.workspace_root)
    mcp_client = MCPClient(settings.mcp_config_path)

    agent = CodingAgent(provider=provider, tools=local_tools, mcp_client=mcp_client)
    result = agent.run_task(task=task, max_steps=max_steps)

    console.print(f"[bold cyan]{settings.forgepilot_name}[/bold cyan]")
    console.print(result)


if __name__ == "__main__":
    app()
