from typing import Protocol

from forgepilot.config import Settings


class LLMProvider(Protocol):
    def complete(self, prompt: str) -> str:
        ...


class TemplateProvider:
    def __init__(self, name: str, model: str) -> None:
        self.name = name
        self.model = model

    def complete(self, prompt: str) -> str:
        return (
            f"[template:{self.name}/{self.model}] Planning next action for: {prompt[:120]}"
        )


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
