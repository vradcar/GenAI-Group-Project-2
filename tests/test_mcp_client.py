
import asyncio
from pathlib import Path
import pytest
import pytest
pytestmark = pytest.mark.asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from forgepilot.mcp_client import MCPClient, _flatten, _ok, _err


# ---------------------------------------------------------------------------
# Helpers to build fake MCP tool/response objects
# ---------------------------------------------------------------------------

def fake_tool(name: str, description: str = "A tool", schema: dict = None):
    t = MagicMock()
    t.name = name
    t.description = description
    t.inputSchema = schema or {"type": "object", "properties": {}}
    return t


def fake_list_tools_response(*tool_names: str):
    resp = MagicMock()
    resp.tools = [fake_tool(n) for n in tool_names]
    return resp


def fake_call_tool_response(text: str, is_error: bool = False):
    block = MagicMock()
    block.text = text
    resp = MagicMock()
    resp.content = [block]
    resp.isError = is_error
    return resp


# ---------------------------------------------------------------------------
# Fixture: patch stdio_client + ClientSession for every test
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.initialize = AsyncMock()
    session.list_tools = AsyncMock(
        return_value=fake_list_tools_response("read_file", "write_file")
    )
    session.call_tool = AsyncMock(
        return_value=fake_call_tool_response("file contents here")
    )
    return session


@pytest.fixture
def patched_client(mock_session: AsyncMock, tmp_path: Path):
    """MCPClient wired to a fake session — no real subprocesses."""
    config = tmp_path / "mcp_servers.json"
    config.write_text(
        '{"servers": [{"name": "filesystem", "command": "npx", '
        '"args": ["-y", "@modelcontextprotocol/server-filesystem", "."], "env": {}}]}'
    )

    # Patch both the transport and session constructors
    with patch("forgepilot.mcp_client.stdio_client") as mock_transport, \
     patch("forgepilot.mcp_client.ClientSession") as mock_session_cls:
        # stdio_client(params) -> async context manager yielding (read, write)
        mock_transport.return_value.__aenter__ = AsyncMock(
            return_value=(MagicMock(), MagicMock())
        )
        mock_transport.return_value.__aexit__ = AsyncMock(return_value=False)

        # ClientSession(read, write) -> async context manager yielding session
        mock_session_cls.return_value.__aenter__ = AsyncMock(
            return_value=mock_session
        )
        mock_session_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        yield MCPClient(str(config)), mock_session


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_connects_and_loads_tools(patched_client: tuple):
    client, _ = patched_client
    async with client:
        assert "filesystem" in client.list_servers()
        tools = client.list_tools()
        assert len(tools) == 2
        names = [t["name"] for t in tools]
        assert "filesystem__read_file" in names
        assert "filesystem__write_file" in names


@pytest.mark.asyncio
async def test_list_tools_schema_shape(patched_client: tuple):
    client, _ = patched_client
    async with client:
        for tool in client.list_tools():
            assert "name" in tool
            assert "description" in tool
            assert "input_schema" in tool
            assert "server" in tool


@pytest.mark.asyncio
async def test_call_tool_success(patched_client: tuple):
    client, mock_session = patched_client
    async with client:
        result = await client.call_tool(
            "filesystem__read_file", {"path": "README.md"}
        )
    assert result["success"] is True
    assert result["result"] == "file contents here"
    assert result["error"] is None
    mock_session.call_tool.assert_called_once_with("read_file", {"path": "README.md"})


@pytest.mark.asyncio
async def test_call_tool_unknown_name(patched_client: tuple):
    client, _ = patched_client
    async with client:
        result = await client.call_tool("filesystem__nonexistent", {})
    assert result["success"] is False
    assert "Unknown tool" in result["error"]


@pytest.mark.asyncio
async def test_call_tool_server_error(patched_client: tuple):
    client, mock_session = patched_client
    mock_session.call_tool = AsyncMock(
        return_value=fake_call_tool_response("permission denied", is_error=True)
    )
    async with client:
        result = await client.call_tool("filesystem__read_file", {"path": "/etc/shadow"})
    assert result["success"] is False
    assert "permission denied" in result["error"]


@pytest.mark.asyncio
async def test_call_tool_exception(patched_client: tuple):
    client, mock_session = patched_client
    mock_session.call_tool = AsyncMock(side_effect=RuntimeError("connection lost"))
    async with client:
        result = await client.call_tool("filesystem__read_file", {"path": "x"})
    assert result["success"] is False
    assert "connection lost" in result["error"]


@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_failed_server_does_not_crash_client(tmp_path: Path):
    """A server that fails to connect should be skipped, not fatal."""
    config = tmp_path / "mcp_servers.json"
    config.write_text(
        '{"servers": ['
        '  {"name": "bad",  "command": "nonexistent_binary", "args": [], "env": {}},'
        '  {"name": "good", "command": "npx", "args": [], "env": {}}'
        ']}'
    )

    good_session = AsyncMock()
    good_session.initialize = AsyncMock()
    good_session.list_tools = AsyncMock(
        return_value=fake_list_tools_response("some_tool")
    )

    # Good transport context manager
    good_transport = MagicMock()
    good_transport.__aenter__ = AsyncMock(return_value=(MagicMock(), MagicMock()))
    good_transport.__aexit__ = AsyncMock(return_value=False)

    # Bad transport raises immediately
    bad_transport = MagicMock()
    bad_transport.__aenter__ = AsyncMock(side_effect=OSError("binary not found"))
    bad_transport.__aexit__ = AsyncMock(return_value=False)

    call_count = 0

    def transport_side_effect(params):
        nonlocal call_count
        call_count += 1
        return bad_transport if call_count == 1 else good_transport

    with patch("forgepilot.mcp_client.stdio_client", side_effect=transport_side_effect), \
         patch("forgepilot.mcp_client.ClientSession") as mock_session_cls:

        mock_session_cls.return_value.__aenter__ = AsyncMock(return_value=good_session)
        mock_session_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        client = MCPClient(str(config))
        async with client:
            assert "good" in client.list_servers()
            assert "bad" not in client.list_servers()
# ---------------------------------------------------------------------------
# Unit tests for pure helpers (no async needed)
# ---------------------------------------------------------------------------

def test_flatten_single_text_block():
    block = MagicMock()
    block.text = "hello"
    assert _flatten([block]) == "hello"


def test_flatten_multiple_blocks():
    b1, b2 = MagicMock(), MagicMock()
    b1.text = "line one"
    b2.text = "line two"
    assert _flatten([b1, b2]) == "line one\nline two"


def test_flatten_empty():
    assert _flatten([]) == ""


def test_ok_shape():
    r = _ok("my_tool", "content")
    assert r == {"tool": "my_tool", "success": True, "result": "content", "error": None}


def test_err_shape():
    r = _err("my_tool", "something broke")
    assert r == {"tool": "my_tool", "success": False, "result": None, "error": "something broke"}


def test_to_anthropic_tools_shape(patched_client: tuple):
    client, _ = patched_client

    async def _run():
        async with client:
            return client.to_anthropic_tools()

    tools = asyncio.run(_run())
    for t in tools:
        assert set(t.keys()) == {"name", "description", "input_schema"}


def test_to_openai_tools_shape(patched_client: tuple):
    client, _ = patched_client

    async def _run():
        async with client:
            return client.to_openai_tools()

    tools = asyncio.run(_run())
    for t in tools:
        assert t["type"] == "function"
        assert "name" in t["function"]
        assert "parameters" in t["function"]