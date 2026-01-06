"""
LLM Client Factory
Factory class for creating appropriate LLM clients.
Supports: OpenAI, Anthropic, Cohere, Ollama
"""

from typing import Optional, List, Generator
import logging
from .base import BaseLLMClient
from .openai_provider import OpenAIClient
from .anthropic_provider import AnthropicClient
from .cohere_provider import CohereClient
from .ollama_provider import OllamaClient

logger = logging.getLogger("rag_app.llm.factory")


class LLMClient:
    """
    Unified LLM client with multi-provider support.
    Factory class for creating appropriate LLM client based on provider.

    Supported providers:
    - OpenAI: GPT-4, GPT-3.5
    - Anthropic: Claude models
    - Cohere: Command R/R+ models
    - Ollama: Local LLM inference
    """

    PROVIDERS = {
        "openai": OpenAIClient,
        "anthropic": AnthropicClient,
        "cohere": CohereClient,
        "ollama": OllamaClient,
    }

    AVAILABLE_MODELS = {
        "openai": [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
        ],
        "anthropic": [
            "claude-sonnet-4-5-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ],
        "cohere": [
            "command-r-plus",
            "command-r",
            "command",
            "command-light",
        ],
        "ollama": [
            "llama3.2",
            "llama3.1",
            "llama3",
            "mistral",
            "mixtral",
            "codellama",
            "phi3",
            "gemma2",
            "qwen2.5",
        ],
    }

    def __init__(
        self,
        provider: str = "anthropic",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize unified LLM client.

        Args:
            provider: LLM provider ('openai', 'anthropic', 'cohere', 'ollama')
            api_key: API key for the provider (not needed for Ollama)
            model: Model name (uses provider default if not specified)
            **kwargs: Additional arguments passed to the provider client
        """
        logger.info(f"Creating LLMClient with provider: {provider}")
        provider = provider.lower()

        if provider not in self.PROVIDERS:
            logger.error(f"Unsupported provider: {provider}")
            raise ValueError(f"Unsupported provider: {provider}. Supported: {list(self.PROVIDERS.keys())}")

        client_class = self.PROVIDERS[provider]

        if model is None:
            model = self.AVAILABLE_MODELS[provider][0]
            logger.info(f"Using default model: {model}")

        self._client = client_class(api_key=api_key, model=model, **kwargs)
        self.provider = provider
        self.model = model
        logger.info(f"LLMClient ready: provider={provider}, model={model}")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        """Generate a response from the LLM."""
        return self._client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> Generator[str, None, None]:
        """Generate a streaming response from the LLM."""
        return self._client.generate_stream(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of available providers."""
        return list(cls.PROVIDERS.keys())

    @classmethod
    def get_available_models(cls, provider: str) -> List[str]:
        """Get list of available models for a provider."""
        return cls.AVAILABLE_MODELS.get(provider.lower(), [])

    @classmethod
    def get_provider_info(cls) -> dict:
        """Get information about all available providers."""
        return {
            "openai": {
                "name": "OpenAI",
                "description": "GPT-4 and GPT-3.5 models",
                "requires_api_key": True,
                "models": cls.AVAILABLE_MODELS["openai"],
            },
            "anthropic": {
                "name": "Anthropic",
                "description": "Claude models",
                "requires_api_key": True,
                "models": cls.AVAILABLE_MODELS["anthropic"],
            },
            "cohere": {
                "name": "Cohere",
                "description": "Command R and Command R+ models",
                "requires_api_key": True,
                "models": cls.AVAILABLE_MODELS["cohere"],
            },
            "ollama": {
                "name": "Ollama",
                "description": "Local LLM inference",
                "requires_api_key": False,
                "models": cls.AVAILABLE_MODELS["ollama"],
            },
        }
