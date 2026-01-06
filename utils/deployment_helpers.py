"""
Deployment Helpers
Utilities for deploying the RAG application to various platforms.
"""

import os
import logging
from typing import Dict, Any, Optional, List
import json

logger = logging.getLogger("rag_app.utils.deployment")


class DeploymentConfig:
    """
    Manages deployment configuration for various platforms.
    """

    PLATFORMS = [
        "streamlit_cloud",
        "huggingface_spaces",
        "railway",
        "docker",
        "aws_lambda",
        "gcp_cloud_run",
    ]

    def __init__(self):
        """Initialize deployment configuration."""
        self.config = {}

    def generate_streamlit_cloud_config(self) -> Dict[str, Any]:
        """Generate configuration for Streamlit Cloud deployment."""
        return {
            "platform": "streamlit_cloud",
            "requirements": [
                "streamlit>=1.28.0",
                "anthropic>=0.7.0",
                "chromadb>=0.4.18",
                "sentence-transformers>=2.2.2",
            ],
            "secrets_template": {
                "ANTHROPIC_API_KEY": "sk-ant-your-key-here",
                "OPENAI_API_KEY": "sk-your-key-here",
                "COHERE_API_KEY": "your-cohere-key-here",
                "PINECONE_API_KEY": "your-pinecone-key-here",
            },
            "config_toml": """
[theme]
primaryColor = "#10B981"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
enableCORS = false
port = 8501
""",
        }

    def generate_docker_config(self) -> Dict[str, Any]:
        """Generate Docker deployment configuration."""
        dockerfile = """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the application
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
"""

        docker_compose = """version: '3.8'

services:
  rag-app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - COHERE_API_KEY=${COHERE_API_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  # Optional: ChromaDB server
  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8000:8000"
    volumes:
      - chroma-data:/chroma/chroma
    restart: unless-stopped

volumes:
  chroma-data:
"""

        return {
            "platform": "docker",
            "dockerfile": dockerfile,
            "docker_compose": docker_compose,
        }

    def generate_railway_config(self) -> Dict[str, Any]:
        """Generate Railway deployment configuration."""
        return {
            "platform": "railway",
            "railway_json": {
                "$schema": "https://railway.app/railway.schema.json",
                "build": {
                    "builder": "NIXPACKS"
                },
                "deploy": {
                    "startCommand": "streamlit run app.py --server.port=$PORT --server.address=0.0.0.0",
                    "healthcheckPath": "/_stcore/health",
                    "restartPolicyType": "ON_FAILURE"
                }
            },
        }

    def generate_huggingface_config(self) -> Dict[str, Any]:
        """Generate Hugging Face Spaces configuration."""
        return {
            "platform": "huggingface_spaces",
            "readme": """---
title: RAG Starter Kit Pro
emoji: 🚀
colorFrom: green
colorTo: blue
sdk: streamlit
sdk_version: 1.28.0
app_file: app.py
pinned: false
---

# RAG Starter Kit Pro

A production-ready RAG application with multiple LLM providers and vector stores.
""",
        }

    def validate_environment(self) -> Dict[str, bool]:
        """Validate environment variables for deployment."""
        required_vars = [
            "ANTHROPIC_API_KEY",
        ]
        optional_vars = [
            "OPENAI_API_KEY",
            "COHERE_API_KEY",
            "PINECONE_API_KEY",
            "WEAVIATE_URL",
            "OLLAMA_HOST",
        ]

        results = {"required": {}, "optional": {}}

        for var in required_vars:
            results["required"][var] = bool(os.getenv(var))

        for var in optional_vars:
            results["optional"][var] = bool(os.getenv(var))

        return results

    def generate_env_template(self) -> str:
        """Generate .env template file."""
        return """# RAG Starter Kit Pro - Environment Variables
# Copy this file to .env and fill in your API keys

# Required: Primary LLM Provider
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key

# Optional: Additional LLM Providers
OPENAI_API_KEY=sk-your-openai-api-key
COHERE_API_KEY=your-cohere-api-key

# Optional: Vector Store Configuration
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=us-east-1

WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=your-weaviate-api-key

# Optional: Local LLM (Ollama)
OLLAMA_HOST=http://localhost:11434

# Optional: Application Settings
LOG_LEVEL=INFO
DEBUG=false

# Optional: Authentication
AUTH_ENABLED=false
SECRET_KEY=your-secret-key-for-sessions
"""


def check_deployment_readiness() -> Dict[str, Any]:
    """
    Check if the application is ready for deployment.

    Returns:
        Dictionary with readiness status and issues
    """
    issues = []
    warnings = []

    # Check required files
    required_files = ["app.py", "requirements.txt"]
    for file in required_files:
        if not os.path.exists(file):
            issues.append(f"Missing required file: {file}")

    # Check API keys
    if not os.getenv("ANTHROPIC_API_KEY"):
        warnings.append("ANTHROPIC_API_KEY not set - required for Claude models")

    # Check optional configurations
    optional_configs = {
        "OPENAI_API_KEY": "OpenAI models",
        "COHERE_API_KEY": "Cohere models",
        "PINECONE_API_KEY": "Pinecone vector store",
    }

    for key, feature in optional_configs.items():
        if not os.getenv(key):
            warnings.append(f"{key} not set - {feature} will be unavailable")

    return {
        "ready": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
    }


def get_deployment_guide(platform: str) -> str:
    """
    Get deployment guide for a specific platform.

    Args:
        platform: Target deployment platform

    Returns:
        Deployment guide as markdown string
    """
    guides = {
        "streamlit_cloud": """
# Streamlit Cloud Deployment

1. Push your code to GitHub
2. Go to share.streamlit.io
3. Click "New app"
4. Select your repository and branch
5. Set main file path to `app.py`
6. Add secrets in the "Advanced settings":
   - ANTHROPIC_API_KEY
   - (Optional) OPENAI_API_KEY, COHERE_API_KEY, etc.
7. Click "Deploy"
""",
        "docker": """
# Docker Deployment

1. Build the image:
   ```bash
   docker build -t rag-starter-kit .
   ```

2. Run the container:
   ```bash
   docker run -p 8501:8501 \\
     -e ANTHROPIC_API_KEY=your-key \\
     rag-starter-kit
   ```

3. Or use docker-compose:
   ```bash
   docker-compose up -d
   ```
""",
        "railway": """
# Railway Deployment

1. Install Railway CLI: `npm i -g @railway/cli`
2. Login: `railway login`
3. Initialize: `railway init`
4. Add environment variables in Railway dashboard
5. Deploy: `railway up`
""",
    }

    return guides.get(platform, f"Deployment guide for {platform} not available.")
