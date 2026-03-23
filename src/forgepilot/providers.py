"""LLM provider abstraction for Ollama, OpenAI, Anthropic, and Groq."""

from __future__ import annotations

from typing import Iterator, Protocol

from forgepilot.config import Settings


class LLMProvider(Protocol):
    def complete(self, prompt: str, system_prompt: str | None = None) -> str:
        ...

    def stream(self, prompt: str, system_prompt: str | None = None) -> Iterator[str]:
        ...


class TemplateProvider:
    def __init__(self, name: str, model: str) -> None:
        self.name = name
        self.model = model

    def complete(self, prompt: str, system_prompt: str | None = None) -> str:
        prefix = f"[{self.name}/{self.model}]"
        if system_prompt:
            return f"{prefix} {system_prompt[:60]} :: {prompt[:180]}"
        return f"{prefix} {prompt[:180]}"

    def stream(self, prompt: str, system_prompt: str | None = None) -> Iterator[str]:
        for word in self.complete(prompt, system_prompt=system_prompt).split():
            yield word + " "


class LangChainChatProvider:
    def __init__(self, llm: object, name: str, model: str) -> None:
        self._llm = llm
        self.name = name
        self.model = model

    def _build_messages(self, prompt: str, system_prompt: str | None) -> list[tuple[str, str]]:
        messages: list[tuple[str, str]] = []
        if system_prompt:
            messages.append(("system", system_prompt))
        messages.append(("human", prompt))
        return messages

    def complete(self, prompt: str, system_prompt: str | None = None) -> str:
        messages = self._build_messages(prompt, system_prompt)
        response = self._llm.invoke(messages)
        content = getattr(response, "content", "")
        return str(content) if content is not None else ""

    def stream(self, prompt: str, system_prompt: str | None = None) -> Iterator[str]:
        messages = self._build_messages(prompt, system_prompt)
        for chunk in self._llm.stream(messages):
            text = getattr(chunk, "content", "")
            if text:
                yield str(text)


def _create_ollama(settings: Settings) -> LLMProvider:
    try:
        from langchain_ollama import ChatOllama

        llm = ChatOllama(
            model=settings.default_model,
            base_url=settings.ollama_base_url,
            temperature=settings.temperature,
        )
        return LangChainChatProvider(llm=llm, name="ollama", model=settings.default_model)
    except Exception:
        return TemplateProvider("ollama-fallback", settings.default_model)


def _create_openai(settings: Settings) -> LLMProvider:
    if not settings.openai_api_key:
        return TemplateProvider("openai-missing-key", settings.openai_model)
    try:
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
        )
        return LangChainChatProvider(llm=llm, name="openai", model=settings.openai_model)
    except Exception:
        return TemplateProvider("openai-fallback", settings.openai_model)


def _create_anthropic(settings: Settings) -> LLMProvider:
    if not settings.anthropic_api_key:
        return TemplateProvider("anthropic-missing-key", settings.anthropic_model)
    try:
        from langchain_anthropic import ChatAnthropic

        llm = ChatAnthropic(
            model=settings.anthropic_model,
            api_key=settings.anthropic_api_key,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
        )
        return LangChainChatProvider(
            llm=llm, name="anthropic", model=settings.anthropic_model
        )
    except Exception:
        return TemplateProvider("anthropic-fallback", settings.anthropic_model)


def _create_groq(settings: Settings) -> LLMProvider:
    if not settings.groq_api_key:
        return TemplateProvider("groq-missing-key", settings.groq_model)
    try:
        from langchain_groq import ChatGroq

        llm = ChatGroq(
            model=settings.groq_model,
            api_key=settings.groq_api_key,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
        )
        return LangChainChatProvider(llm=llm, name="groq", model=settings.groq_model)
    except Exception:
        return TemplateProvider("groq-fallback", settings.groq_model)


def create_provider(settings: Settings) -> LLMProvider:
    provider = settings.default_provider.lower().strip()
    if provider == "ollama":
        return _create_ollama(settings)
    if provider == "openai":
        return _create_openai(settings)
    if provider == "anthropic":
        return _create_anthropic(settings)
    if provider == "groq":
        return _create_groq(settings)
    return TemplateProvider("unknown-provider", settings.default_model)
