from __future__ import annotations

import unittest
from unittest.mock import patch

from app.services.llm_provider import GeminiProvider, LLMProviderError, OllamaProvider, OpenAIProvider, get_provider


class LLMProviderTestCase(unittest.TestCase):
    def test_default_provider_is_ollama(self) -> None:
        provider = get_provider()

        self.assertIsInstance(provider, OllamaProvider)

    def test_provider_can_be_switched_via_environment(self) -> None:
        with patch.dict("os.environ", {"LLM_PROVIDER": "openai"}, clear=False):
            provider = get_provider()

        self.assertIsInstance(provider, OpenAIProvider)

    def test_gemini_provider_is_selected_when_configured(self) -> None:
        with patch.dict("os.environ", {"LLM_PROVIDER": "gemini"}, clear=False):
            provider = get_provider()

        self.assertIsInstance(provider, GeminiProvider)

    def test_unknown_provider_raises_error(self) -> None:
        with patch.dict("os.environ", {"LLM_PROVIDER": "unknown"}, clear=False):
            with self.assertRaises(LLMProviderError):
                get_provider()


if __name__ == "__main__":
    unittest.main()
