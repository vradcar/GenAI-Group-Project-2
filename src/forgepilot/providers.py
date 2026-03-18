"""
LLM Provider abstraction — supports Ollama, OpenAI, Anthropic, Groq.

Protocol defines two methods:
  complete(prompt) -> str          — blocking, returns full response
  stream(prompt)   -> Iterator[str] — yields tokens as they arrive
"""

from typing import Iterator, Protocol

from forgepilot.config import Settings


class LLMProvider(Protocol):
    def complete(self, prompt: str) -> str:
        ...

    def stream(self, prompt: str) -> Iterator[str]:
        ...


class TemplateProvider:
    """Stub provider — replace with real LangChain clients in Provider branch."""

    def __init__(self, name: str, model: str) -> None:
        self.name = name
        self.model = model

    def complete(self, prompt: str) -> str:
        return (
            f"[template:{self.name}/{self.model}] "
            f"Planning next action for: {prompt[:120]}"
        )

    def stream(self, prompt: str) -> Iterator[str]:
        """Simulate streaming by yielding the full response word-by-word."""
        for word in self.complete(prompt).split():
            yield word + " "


def create_provider(settings: Settings) -> LLMProvider:
    provider = settings.default_provider.lower()
    if provider == "ollama":
        return TemplateProvider("ollama", settings.default_model)
    if provider == "openai":
        return TemplateProvider("openai", settings.openai_model)
    if provider == "anthropic":
        return TemplateProvider("anthropic", settings.anthropic_model)
    if provider == "groq":
        return TemplateProvider("groq", settings.groq_model)
    return TemplateProvider("unknown", settings.default_model)
