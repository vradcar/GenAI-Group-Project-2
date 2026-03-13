from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    name: str
    arguments: dict[str, Any]


@dataclass
class ToolResult:
    name: str
    success: bool
    output: str


@dataclass
class AgentStep:
    thought: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    final_response: str | None = None
