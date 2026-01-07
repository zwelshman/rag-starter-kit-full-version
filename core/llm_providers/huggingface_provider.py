"""
Hugging Face Inference API Provider
Implementation for Hugging Face's serverless Inference API.
"""

from typing import Optional, Generator
import os
import logging
from .base import BaseLLMClient

logger = logging.getLogger("rag_app.llm.huggingface")


class HuggingFaceClient(BaseLLMClient):
    """Hugging Face Inference API client."""

    # Available models on Hugging Face Inference API
    AVAILABLE_MODELS = [
        "meta-llama/Meta-Llama-3.1-8B-Instruct",
        "meta-llama/Meta-Llama-3-8B-Instruct",
        "mistralai/Mistral-7B-Instruct-v0.3",
        "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "microsoft/Phi-3-mini-4k-instruct",
        "google/gemma-2-9b-it",
        "Qwen/Qwen2.5-7B-Instruct",
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "meta-llama/Meta-Llama-3.1-8B-Instruct",
    ):
        """
        Initialize Hugging Face Inference API client.

        Args:
            api_key: Hugging Face API token (defaults to HF_API_KEY env var)
            model: Model to use (default: meta-llama/Meta-Llama-3.1-8B-Instruct)
        """
        logger.info("Initializing Hugging Face client...")
        try:
            from huggingface_hub import InferenceClient
        except ImportError:
            logger.error("huggingface_hub package not installed")
            raise ImportError("huggingface_hub is required. Install with: pip install huggingface_hub")

        self.api_key = api_key or os.environ.get("HF_API_KEY") or os.environ.get("HUGGINGFACE_API_KEY")
        if not self.api_key:
            logger.error("No Hugging Face API key provided")
            raise ValueError("Hugging Face API key is required. Set HF_API_KEY environment variable.")

        self.model = model
        self._client = InferenceClient(token=self.api_key)
        logger.info(f"Hugging Face client initialized with model: {self.model}")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        """Generate a response from Hugging Face Inference API."""
        logger.info(f"Generating response (non-streaming)")
        logger.info(f"  Model: {self.model}")
        logger.info(f"  Temperature: {temperature}")
        logger.info(f"  Max tokens: {max_tokens}")
        logger.info(f"  Prompt length: {len(prompt)} chars")

        # Build messages in chat format
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
            logger.debug(f"  System prompt length: {len(system_prompt)} chars")

        messages.append({"role": "user", "content": prompt})

        logger.info("Sending request to Hugging Face Inference API...")

        try:
            response = self._client.chat_completion(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=min(max(temperature, 0.01), 1.0),  # HF requires temp > 0
            )

            result = response.choices[0].message.content
            logger.info(f"Response received: {len(result)} chars")

            if hasattr(response, 'usage') and response.usage:
                logger.info(f"  Usage - Prompt tokens: {response.usage.prompt_tokens}")
                logger.info(f"  Usage - Completion tokens: {response.usage.completion_tokens}")

            return result

        except Exception as e:
            logger.error(f"Error calling Hugging Face API: {e}")
            raise

    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> Generator[str, None, None]:
        """Generate a streaming response from Hugging Face Inference API."""
        logger.info(f"Generating response (streaming)")
        logger.info(f"  Model: {self.model}")
        logger.info(f"  Temperature: {temperature}")
        logger.info(f"  Max tokens: {max_tokens}")
        logger.info(f"  Prompt length: {len(prompt)} chars")

        # Build messages in chat format
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
            logger.debug(f"  System prompt length: {len(system_prompt)} chars")

        messages.append({"role": "user", "content": prompt})

        logger.info("Starting streaming request to Hugging Face Inference API...")

        try:
            token_count = 0
            stream = self._client.chat_completion(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=min(max(temperature, 0.01), 1.0),
                stream=True,
            )

            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    token_count += 1
                    yield chunk.choices[0].delta.content

            logger.info(f"Streaming complete: ~{token_count} chunks streamed")

        except Exception as e:
            logger.error(f"Error streaming from Hugging Face API: {e}")
            raise

    @classmethod
    def get_available_models(cls) -> list:
        """Get list of available models."""
        return cls.AVAILABLE_MODELS
