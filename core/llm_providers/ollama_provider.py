"""
Ollama LLM Provider
Integration with local Ollama models for RAG applications.
"""

import os
import logging
import requests
from typing import Optional, Generator, List

from .base import BaseLLMClient

logger = logging.getLogger("rag_app.llm.ollama")


class OllamaClient(BaseLLMClient):
    """
    Ollama LLM client implementation.
    Supports running local LLM models via Ollama.
    """

    DEFAULT_MODEL = "llama3.2"
    DEFAULT_HOST = "http://localhost:11434"

    def __init__(
        self,
        api_key: Optional[str] = None,  # Not used, kept for interface compatibility
        model: str = DEFAULT_MODEL,
        host: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize Ollama client.

        Args:
            api_key: Not used for Ollama (local inference)
            model: Model name (default: llama3.2)
            host: Ollama server host (default: http://localhost:11434)
            **kwargs: Additional arguments
        """
        self.host = host or os.getenv("OLLAMA_HOST", self.DEFAULT_HOST)
        self.model = model
        self.api_base = f"{self.host}/api"

        # Verify connection
        if not self._check_connection():
            logger.warning(f"Cannot connect to Ollama at {self.host}. Make sure Ollama is running.")

        logger.info(f"Ollama client initialized: host={self.host}, model={model}")

    def _check_connection(self) -> bool:
        """Check if Ollama server is reachable."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def get_available_models(self) -> List[str]:
        """Get list of models available on the Ollama server."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get Ollama models: {e}")
        return []

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        """
        Generate a response using Ollama.

        Args:
            prompt: User prompt
            system_prompt: System instructions
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text response
        """
        logger.info(f"Generating with Ollama: model={self.model}, temp={temperature}")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = requests.post(
                f"{self.api_base}/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    },
                },
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()
            result = data.get("message", {}).get("content", "")
            logger.info(f"Ollama response generated: {len(result)} characters")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama request failed: {e}")
            raise RuntimeError(f"Ollama request failed: {e}")

    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> Generator[str, None, None]:
        """
        Generate a streaming response using Ollama.

        Args:
            prompt: User prompt
            system_prompt: System instructions
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Yields:
            Token strings as they are generated
        """
        logger.info(f"Streaming with Ollama: model={self.model}, temp={temperature}")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = requests.post(
                f"{self.api_base}/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": True,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    },
                },
                stream=True,
                timeout=120,
            )
            response.raise_for_status()

            import json
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        content = data.get("message", {}).get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue

        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama streaming request failed: {e}")
            raise RuntimeError(f"Ollama streaming request failed: {e}")

    def get_model_info(self) -> dict:
        """Get information about the current model."""
        available = self.get_available_models()
        return {
            "provider": "ollama",
            "model": self.model,
            "host": self.host,
            "available_models": available,
            "is_local": True,
        }

    def pull_model(self, model_name: str) -> bool:
        """
        Pull a model from Ollama library.

        Args:
            model_name: Name of the model to pull

        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.post(
                f"{self.api_base}/pull",
                json={"name": model_name},
                timeout=600,  # Models can take time to download
            )
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            return False

    @staticmethod
    def estimate_cost(input_tokens: int, output_tokens: int, model: str = "llama3.2") -> float:
        """
        Estimate cost for Ollama usage.
        Ollama is free (local inference), so cost is $0.00
        """
        return 0.00


# Common Ollama models reference
OLLAMA_MODELS = {
    "llama3.2": "Meta's Llama 3.2 (3B/1B parameters)",
    "llama3.1": "Meta's Llama 3.1 (8B/70B/405B parameters)",
    "llama3": "Meta's Llama 3 (8B/70B parameters)",
    "mistral": "Mistral 7B",
    "mixtral": "Mixtral 8x7B",
    "codellama": "Code Llama for coding tasks",
    "phi3": "Microsoft's Phi-3 (3.8B)",
    "gemma2": "Google's Gemma 2",
    "qwen2.5": "Alibaba's Qwen 2.5",
    "deepseek-coder-v2": "DeepSeek Coder V2",
}
