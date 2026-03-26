"""
Simplified Claude LLM Provider
Single interface for Anthropic Claude models
"""

import os
from anthropic import Anthropic
from typing import Optional


class ClaudeProvider:
    """Simple Claude LLM provider"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        """Initialize Claude provider
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Model name to use
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment or arguments")
        
        self.model = model
        self.client = Anthropic(api_key=self.api_key)
    
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1024) -> str:
        """Generate response using Claude
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated text response
        """
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
    
    def generate_with_context(
        self, 
        query: str, 
        context: str,
        system_prompt: str = "You are a helpful assistant.",
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> str:
        """Generate response using Claude with context (for RAG)
        
        Args:
            query: User question
            context: Retrieved context/documents
            system_prompt: System message to guide behavior
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated text response
        """
        prompt = f"""{system_prompt}

Context:
{context}

Question: {query}

Answer:"""
        
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
    
    def get_model_name(self) -> str:
        """Get current model name"""
        return self.model
    
    def set_model(self, model: str) -> None:
        """Change model"""
        self.model = model
