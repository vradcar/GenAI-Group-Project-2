from forgepilot.agent import CodingAgent
from forgepilot.local_tools import LocalTools
from forgepilot.mcp_client import MCPClient
from forgepilot.providers import TemplateProvider


def test_agent_template_runs() -> None:
    provider = TemplateProvider("test", "model")
    tools = LocalTools(".")
    mcp_client = MCPClient("./configs/mcp.servers.example.json")
    agent = CodingAgent(provider=provider, tools=tools, mcp_client=mcp_client)
    result = agent.run_task("Create a hello world file")
    assert "Task:" in result
