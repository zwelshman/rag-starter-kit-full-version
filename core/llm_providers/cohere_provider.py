"""
Cohere LLM Provider
Integration with Cohere's Command models for RAG applications.
"""

import os
import logging
from typing import Optional, Generator

from .base import BaseLLMClient

logger = logging.getLogger("rag_app.llm.cohere")


class CohereClient(BaseLLMClient):
    """
    Cohere LLM client implementation.
    Supports Command R and Command R+ models.
    """

    DEFAULT_MODEL = "command-r-plus"
    AVAILABLE_MODELS = [
        "command-r-plus",
        "command-r",
        "command",
        "command-light",
        "command-nightly",
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        **kwargs,
    ):
        """
        Initialize Cohere client.

        Args:
            api_key: Cohere API key (or set COHERE_API_KEY env var)
            model: Model name (default: command-r-plus)
            **kwargs: Additional arguments
        """
        try:
            import cohere
        except ImportError:
            raise ImportError("Cohere package not installed. Run: pip install cohere")

        self.api_key = api_key or os.getenv("COHERE_API_KEY")
        if not self.api_key:
            raise ValueError("Cohere API key not provided. Set COHERE_API_KEY or pass api_key parameter.")

        self.model = model
        self.client = cohere.Client(api_key=self.api_key)
        logger.info(f"Cohere client initialized with model: {model}")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        """
        Generate a response using Cohere.

        Args:
            prompt: User prompt
            system_prompt: System instructions
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text response
        """
        logger.info(f"Generating with Cohere: model={self.model}, temp={temperature}, max_tokens={max_tokens}")

        preamble = system_prompt if system_prompt else "You are a helpful AI assistant."

        response = self.client.chat(
            model=self.model,
            message=prompt,
            preamble=preamble,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        result = response.text
        logger.info(f"Cohere response generated: {len(result)} characters")
        return result

    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> Generator[str, None, None]:
        """
        Generate a streaming response using Cohere.

        Args:
            prompt: User prompt
            system_prompt: System instructions
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Yields:
            Token strings as they are generated
        """
        logger.info(f"Streaming with Cohere: model={self.model}, temp={temperature}")

        preamble = system_prompt if system_prompt else "You are a helpful AI assistant."

        for event in self.client.chat_stream(
            model=self.model,
            message=prompt,
            preamble=preamble,
            temperature=temperature,
            max_tokens=max_tokens,
        ):
            if event.event_type == "text-generation":
                yield event.text

    def get_model_info(self) -> dict:
        """Get information about the current model."""
        return {
            "provider": "cohere",
            "model": self.model,
            "available_models": self.AVAILABLE_MODELS,
        }

    @staticmethod
    def estimate_cost(input_tokens: int, output_tokens: int, model: str = "command-r-plus") -> float:
        """
        Estimate cost for Cohere API usage.

        Pricing (as of 2024):
        - Command R+: $3.00/1M input, $15.00/1M output
        - Command R: $0.50/1M input, $1.50/1M output
        - Command: $1.00/1M input, $2.00/1M output
        """
        pricing = {
            "command-r-plus": {"input": 3.00, "output": 15.00},
            "command-r": {"input": 0.50, "output": 1.50},
            "command": {"input": 1.00, "output": 2.00},
            "command-light": {"input": 0.30, "output": 0.60},
            "command-nightly": {"input": 1.00, "output": 2.00},
        }

        model_pricing = pricing.get(model, pricing["command-r-plus"])
        input_cost = (input_tokens / 1_000_000) * model_pricing["input"]
        output_cost = (output_tokens / 1_000_000) * model_pricing["output"]

        return input_cost + output_cost
