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
        self.api_key = (api_key or "").strip()
        self.model = (model or "gemini-1.5-flash").strip().removeprefix("models/")

    async def generate(self, prompt: str) -> str:
        if not self.api_key:
            raise LLMProviderError(
                "GEMINI_API_KEY is not configured. Please add your Google AI Studio API key "
                "to backend/.env (e.g. GEMINI_API_KEY=AIzaSy...)"
            )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    url,
                    headers={
                        "x-goog-api-key": self.api_key,
                        "Content-Type": "application/json",
                    },
                    json={"contents": [{"parts": [{"text": prompt}]}]},
                )
        except httpx.HTTPError as exc:
            raise LLMProviderError(f"Gemini connection failed: {exc}") from exc

        if response.status_code != 200:
            error_message = f"HTTP {response.status_code}"
            try:
                error_json = response.json()
                if isinstance(error_json, dict) and "error" in error_json:
                    error_message = error_json["error"].get("message") or error_message
            except Exception:
                error_message = response.text or error_message
            raise LLMProviderError(f"Google AI Studio error: {error_message}")

        try:
            data: dict[str, Any] = response.json()
        except ValueError as exc:
            raise LLMProviderError("Gemini returned an invalid JSON response") from exc

        candidates = data.get("candidates")
        if not candidates:
            feedback = data.get("promptFeedback", {})
            block_reason = feedback.get("blockReason")
            if block_reason:
                return f"Prompt blocked by Google Gemini safety filters: {block_reason}"
            raise LLMProviderError("Google AI Studio returned no candidate responses.")

        first_candidate = candidates[0]
        finish_reason = first_candidate.get("finishReason")
        if finish_reason == "SAFETY":
            return "Response blocked by Google Gemini safety filters."

        try:
            return str(first_candidate["content"]["parts"][0]["text"]).strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMProviderError(f"Gemini returned an unexpected response structure: {data}") from exc


def get_provider(name: str | None = None) -> LLMProvider:
    import os
    from dotenv import dotenv_values

    settings = get_settings()
    provider_name = (name or settings.llm_provider).lower()

    # Load fresh values from .env if present to reflect on-the-fly config updates
    fresh_env = dotenv_values(".env")

    if provider_name == "ollama":
        base_url = fresh_env.get("OLLAMA_BASE_URL") or os.getenv("OLLAMA_BASE_URL") or settings.ollama_base_url
        model = fresh_env.get("OLLAMA_MODEL") or os.getenv("OLLAMA_MODEL") or settings.ollama_model
        return OllamaProvider(base_url, model)
    if provider_name == "openai":
        api_key = fresh_env.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") or settings.openai_api_key
        model = fresh_env.get("OPENAI_MODEL") or os.getenv("OPENAI_MODEL") or settings.openai_model
        return OpenAIProvider(api_key, model)
    if provider_name == "gemini":
        api_key = fresh_env.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") or settings.gemini_api_key
        model = fresh_env.get("GEMINI_MODEL") or os.getenv("GEMINI_MODEL") or settings.gemini_model
        return GeminiProvider(api_key, model)

    raise LLMProviderError(f"Unsupported LLM provider: {provider_name}")
