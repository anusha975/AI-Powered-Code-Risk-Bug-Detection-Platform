"""
LLM Provider Abstraction Package.
"""

from typing import Optional

from app.ai.providers.base import LLMProvider
from app.ai.providers.mock_provider import MockLLMProvider
from app.ai.providers.external_provider import ExternalLLMProvider, AIProviderError, AITimeoutError, AIRateLimitError
from app.ai.providers.local_provider import LocalLLMProvider
from app.core.config import settings


def get_llm_provider(provider_type: Optional[str] = None) -> LLMProvider:
    """
    Factory to instantiate the configured LLMProvider.
    Options: 'mock', 'external', 'local'.
    Defaults to settings.LLM_PROVIDER.
    """
    selected = (provider_type or settings.LLM_PROVIDER).lower()

    if selected in ("external", "cloud", "openai"):
        return ExternalLLMProvider()
    elif selected in ("local", "ollama", "vllm"):
        return LocalLLMProvider()
    else:
        return MockLLMProvider()


__all__ = [
    "LLMProvider",
    "MockLLMProvider",
    "ExternalLLMProvider",
    "LocalLLMProvider",
    "AIProviderError",
    "AITimeoutError",
    "AIRateLimitError",
    "get_llm_provider"
]
