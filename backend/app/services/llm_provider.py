from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import httpx

from app.utils.config import get_settings


class LLMProviderError(Exception):
    pass


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        raise NotImplementedError


class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def generate(self, prompt: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={"model": self.model, "prompt": prompt, "stream": False},
                )
                response.raise_for_status()
        except httpx.ConnectError as exc:
            raise LLMProviderError(
                f"Ollama is not reachable at {self.base_url}. Start Ollama with "
                f"`ollama serve` and make sure the `{self.model}` model is available."
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise LLMProviderError(
                f"Ollama returned HTTP {exc.response.status_code}. Check that model "
                f"`{self.model}` is installed with `ollama pull {self.model}`."
            ) from exc
        except httpx.HTTPError as exc:
            raise LLMProviderError(f"Ollama request failed: {exc}") from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise LLMProviderError("Ollama returned an invalid JSON response") from exc

        return str(data.get("response") or "").strip()


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str | None, model: str) -> None:
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str) -> str:
        if not self.api_key:
            raise LLMProviderError("OPENAI_API_KEY is not configured")

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.2,
                    },
                )
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise LLMProviderError(f"OpenAI request failed: {exc}") from exc

        try:
            data: dict[str, Any] = response.json()
            return str(data["choices"][0]["message"]["content"]).strip()
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise LLMProviderError("OpenAI returned an unexpected response format") from exc


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str | None, model: str) -> None:
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str) -> str:
        if not self.api_key:
            raise LLMProviderError("GEMINI_API_KEY is not configured")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    url,
                    params={"key": self.api_key},
                    json={"contents": [{"parts": [{"text": prompt}]}]},
                )
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise LLMProviderError(f"Gemini request failed: {exc}") from exc

        try:
            data: dict[str, Any] = response.json()
            return str(data["candidates"][0]["content"]["parts"][0]["text"]).strip()
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise LLMProviderError("Gemini returned an unexpected response format") from exc


def get_provider(name: str | None = None) -> LLMProvider:
    settings = get_settings()
    provider_name = (name or settings.llm_provider).lower()

    if provider_name == "ollama":
        return OllamaProvider(settings.ollama_base_url, settings.ollama_model)
    if provider_name == "openai":
        return OpenAIProvider(settings.openai_api_key, settings.openai_model)
    if provider_name == "gemini":
        return GeminiProvider(settings.gemini_api_key, settings.gemini_model)

    raise LLMProviderError(f"Unsupported LLM provider: {provider_name}")
