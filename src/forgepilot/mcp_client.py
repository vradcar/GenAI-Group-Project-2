
import json
import logging
import os
import re
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Any

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except Exception:
    ClientSession = None  # type: ignore[assignment]

    class StdioServerParameters:  # type: ignore[no-redef]
        def __init__(self, command: str, args: list[str] | None = None, env: dict[str, str] | None = None):
            self.command = command
            self.args = args or []
            self.env = env

    stdio_client = None


def _mcp_sdk_available() -> bool:
    return (
        ClientSession is not None
        and stdio_client is not None
    )

logger = logging.getLogger(__name__)


def _resolve_env_value(value: str) -> str:
    expanded = os.path.expandvars(value)

    if expanded == value:
        pattern = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")

        def repl(match: re.Match[str]) -> str:
            var_name = match.group(1) or match.group(2)
            return os.getenv(var_name, "")

        expanded = pattern.sub(repl, value)

    return expanded


# ---------------------------------------------------------------------------
# Public result type  (matches the stub's dict return shape so agent.py
# doesn't need to change)
# ---------------------------------------------------------------------------

def _ok(tool_name: str, content: Any) -> dict[str, Any]:
    return {"tool": tool_name, "success": True, "result": content, "error": None}

def _err(tool_name: str, message: str) -> dict[str, Any]:
    return {"tool": tool_name, "success": False, "result": None, "error": message}


# ---------------------------------------------------------------------------
# MCPClient
# ---------------------------------------------------------------------------

class MCPClient:
    """
    Async MCP client.  Launches each server as a stdio subprocess,
    performs the MCP handshake, and discovers tools dynamically.

    Supports the existing mcp_servers.json format exactly:
        { "servers": [ { "name", "command", "args", "env" }, ... ] }

    Tool names are namespaced:  "<server_name>__<original_tool_name>"
    so there are no collisions between servers.
    """

    def __init__(self, config_path: str = "configs/mcp_servers.json") -> None:
        self.config_path = Path(config_path)
        self._raw_config: dict[str, Any] = {"servers": []}

        # server_name -> live ClientSession
        self._sessions: dict[str, ClientSession] = {}

        # namespaced_tool_name -> { meta + server_name + original_name }
        self._tool_registry: dict[str, dict[str, Any]] = {}

        # keeps all stdio transports alive while the client is open
        self._exit_stack = AsyncExitStack()

    # ------------------------------------------------------------------
    # Context manager  --  use `async with MCPClient(...) as client:`
    # ------------------------------------------------------------------

    async def __aenter__(self) -> "MCPClient":
        self._load_config()
        if not _mcp_sdk_available():
            logger.warning("MCP SDK not installed; continuing with no connected MCP servers")
            return self
        await self._connect_all()
        return self

    async def __aexit__(self, *_) -> None:
        await self._exit_stack.aclose()
        self._sessions.clear()
        self._tool_registry.clear()

    # ------------------------------------------------------------------
    # Config loading  (same JSON schema the team already uses)
    # ------------------------------------------------------------------

    def _load_config(self) -> None:
        if not self.config_path.exists():
            logger.warning("MCP config not found: %s", self.config_path)
            return
        self._raw_config = json.loads(
            self.config_path.read_text(encoding="utf-8")
        )
        logger.info("Loaded MCP config from %s", self.config_path)

    # ------------------------------------------------------------------
    # Connection + tool discovery
    # ------------------------------------------------------------------

    async def _connect_all(self) -> None:
        for server_def in self._raw_config.get("servers", []):
            try:
                await self._connect_one(server_def)
            except Exception as exc:
                # One bad server must not crash the whole client
                logger.error(
                    "Could not connect to server '%s': %s",
                    server_def.get("name", "?"), exc,
                )

    async def _connect_one(self, server_def: dict[str, Any]) -> None:
        if not _mcp_sdk_available() or stdio_client is None:
            raise RuntimeError("MCP SDK unavailable")

        name    = server_def["name"]
        command = server_def["command"]
        args    = server_def.get("args", [])

        # Resolve ${VAR} placeholders in env values from the real environment
        raw_env = server_def.get("env") or {}
        env = {k: _resolve_env_value(v) for k, v in raw_env.items()} or None

        params = StdioServerParameters(command=command, args=args, env=env)

        read, write = await self._exit_stack.enter_async_context(
            stdio_client(params)
        )
        session = await self._exit_stack.enter_async_context(
            ClientSession(read, write)
        )
        await session.initialize()

        self._sessions[name] = session
        logger.info("Connected: %s", name)

        await self._discover_tools(name, session)

    async def _discover_tools(
        self, server_name: str, session: ClientSession
    ) -> None:
        """Ask the server for its tool list and register each one."""
        response = await session.list_tools()
        count = 0
        for tool in response.tools:
            namespaced = f"{server_name}__{tool.name}"
            self._tool_registry[namespaced] = {
                # fields the agent / LLM needs
                "name":         namespaced,
                "description":  tool.description or "",
                "input_schema": tool.inputSchema or {},
                # fields we need internally
                "_server":      server_name,
                "_original":    tool.name,
            }
            count += 1

        logger.info("Loaded %d tools from '%s'", count, server_name)

    # ------------------------------------------------------------------
    # Public interface  (called by agent.py)
    # ------------------------------------------------------------------

    def list_tools(self) -> list[dict[str, Any]]:
        """
        Return all tools across all connected servers.

        Each dict has:
            name          - namespaced tool name  (pass to call_tool)
            description   - human / LLM-readable description
            input_schema  - JSON Schema for the tool's arguments
            server        - which server owns this tool
        """
        return [
            {
                "name":         t["name"],
                "description":  t["description"],
                "input_schema": t["input_schema"],
                "server":       t["_server"],
            }
            for t in self._tool_registry.values()
        ]

    def list_servers(self) -> list[str]:
        """Names of all successfully connected servers."""
        return list(self._sessions.keys())

    async def call_tool(
        self, tool_name: str, args: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Execute a tool by its namespaced name.

        Always returns a dict — never raises.  The agent checks ["success"].

        Parameters
        ----------
        tool_name : str
            Namespaced name, e.g. "filesystem__read_file"
        args : dict
            Arguments matching the tool's input_schema

        Returns
        -------
        dict  with keys: tool, success, result, error
        """
        entry = self._tool_registry.get(tool_name)
        if entry is None:
            return _err(
                tool_name,
                f"Unknown tool '{tool_name}'. "
                f"Available: {list(self._tool_registry)}"
            )

        session = self._sessions.get(entry["_server"])
        if session is None:
            return _err(tool_name, f"Server '{entry['_server']}' not connected.")

        try:
            response = await session.call_tool(entry["_original"], args)
            content  = _flatten(response.content)

            if response.isError:
                return _err(tool_name, str(content))
            return _ok(tool_name, content)

        except Exception as exc:
            logger.exception("Tool call failed: %s", tool_name)
            return _err(tool_name, str(exc))

    # ------------------------------------------------------------------
    # LLM schema helpers  (Person 2 / providers.py can call these)
    # ------------------------------------------------------------------

    def to_anthropic_tools(self) -> list[dict[str, Any]]:
        """Format tool list for Anthropic API tool_use calls."""
        return [
            {
                "name":         t["name"],
                "description":  t["description"],
                "input_schema": t["input_schema"],
            }
            for t in self.list_tools()
        ]

    def to_openai_tools(self) -> list[dict[str, Any]]:
        """Format tool list for OpenAI / Ollama function-calling."""
        return [
            {
                "type": "function",
                "function": {
                    "name":        t["name"],
                    "description": t["description"],
                    "parameters":  t["input_schema"],
                },
            }
            for t in self.list_tools()
        ]


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _flatten(content_blocks: list) -> Any:
    """Collapse MCP content block list into a plain string."""
    if not content_blocks:
        return ""
    parts = []
    for block in content_blocks:
        if hasattr(block, "text"):
            parts.append(block.text)
        elif hasattr(block, "data"):
            parts.append(block.data)
        else:
            parts.append(str(block))
    return "\n".join(parts) if len(parts) > 1 else parts[0]