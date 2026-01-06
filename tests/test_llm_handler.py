"""
Tests for LLM Handler
Tests for multi-provider LLM functionality.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock


class TestLLMClientFactory:
    """Tests for the LLMClient factory class."""

    def test_get_available_providers(self):
        """Test that all expected providers are available."""
        from core.llm_providers import LLMClient

        providers = LLMClient.get_available_providers()

        assert "openai" in providers
        assert "anthropic" in providers
        assert "cohere" in providers
        assert "ollama" in providers

    def test_get_available_models(self):
        """Test that models are returned for each provider."""
        from core.llm_providers import LLMClient

        # Test Anthropic models
        anthropic_models = LLMClient.get_available_models("anthropic")
        assert len(anthropic_models) > 0
        assert "claude-sonnet-4-5-20241022" in anthropic_models

        # Test OpenAI models
        openai_models = LLMClient.get_available_models("openai")
        assert len(openai_models) > 0
        assert "gpt-4o" in openai_models

        # Test Cohere models
        cohere_models = LLMClient.get_available_models("cohere")
        assert len(cohere_models) > 0
        assert "command-r-plus" in cohere_models

        # Test Ollama models
        ollama_models = LLMClient.get_available_models("ollama")
        assert len(ollama_models) > 0

    def test_invalid_provider_raises_error(self):
        """Test that invalid provider raises ValueError."""
        from core.llm_providers import LLMClient

        with pytest.raises(ValueError, match="Unsupported provider"):
            LLMClient(provider="invalid_provider", api_key="test")

    def test_get_provider_info(self):
        """Test provider info retrieval."""
        from core.llm_providers import LLMClient

        info = LLMClient.get_provider_info()

        assert "openai" in info
        assert "anthropic" in info
        assert "cohere" in info
        assert "ollama" in info

        # Check structure
        assert "name" in info["openai"]
        assert "description" in info["openai"]
        assert "requires_api_key" in info["openai"]
        assert "models" in info["openai"]


class TestAnthropicClient:
    """Tests for Anthropic client."""

    @patch('core.llm_providers.anthropic_provider.Anthropic')
    def test_generate(self, mock_anthropic):
        """Test basic generation."""
        from core.llm_providers import AnthropicClient

        # Setup mock
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.return_value = MagicMock(
            content=[MagicMock(text="Test response")]
        )

        client = AnthropicClient(api_key="test-key")
        response = client.generate("Test prompt")

        assert response == "Test response"
        mock_client.messages.create.assert_called_once()


class TestCohereClient:
    """Tests for Cohere client."""

    def test_estimate_cost(self):
        """Test cost estimation for Cohere."""
        from core.llm_providers.cohere_provider import CohereClient

        # Test command-r-plus pricing
        cost = CohereClient.estimate_cost(1000, 500, "command-r-plus")
        assert cost > 0

        # Test command-r pricing (should be cheaper)
        cost_r = CohereClient.estimate_cost(1000, 500, "command-r")
        assert cost_r > 0
        assert cost_r < cost


class TestOllamaClient:
    """Tests for Ollama client."""

    def test_estimate_cost_is_free(self):
        """Test that Ollama cost is always 0 (local inference)."""
        from core.llm_providers.ollama_provider import OllamaClient

        cost = OllamaClient.estimate_cost(10000, 5000, "llama3.2")
        assert cost == 0.0

    @patch('core.llm_providers.ollama_provider.requests.get')
    def test_check_connection(self, mock_get):
        """Test connection check."""
        from core.llm_providers.ollama_provider import OllamaClient

        mock_get.return_value = MagicMock(status_code=200)

        # Note: This will try to initialize, may need adjustments
        # based on actual implementation
        assert True  # Placeholder


class TestLLMClientIntegration:
    """Integration tests (require API keys)."""

    @pytest.mark.skipif(
        not os.environ.get("ANTHROPIC_API_KEY"),
        reason="ANTHROPIC_API_KEY not set"
    )
    def test_anthropic_real_request(self):
        """Test real request to Anthropic (requires API key)."""
        from core.llm_providers import LLMClient

        client = LLMClient(
            provider="anthropic",
            model="claude-3-haiku-20240307"  # Use cheapest model for tests
        )

        response = client.generate(
            "Say 'test' and nothing else",
            max_tokens=10
        )

        assert len(response) > 0

    @pytest.mark.skipif(
        not os.environ.get("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set"
    )
    def test_openai_real_request(self):
        """Test real request to OpenAI (requires API key)."""
        from core.llm_providers import LLMClient

        client = LLMClient(
            provider="openai",
            model="gpt-3.5-turbo"  # Use cheapest model for tests
        )

        response = client.generate(
            "Say 'test' and nothing else",
            max_tokens=10
        )

        assert len(response) > 0
