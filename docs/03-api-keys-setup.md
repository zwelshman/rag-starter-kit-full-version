# API Keys Setup Guide

Configure API keys for all supported LLM providers and vector stores.

## Overview

RAG Starter Kit Pro supports multiple providers:

| Provider | Type | API Key Required |
|----------|------|-----------------|
| Anthropic | LLM | Yes |
| OpenAI | LLM | Yes |
| Cohere | LLM | Yes |
| Hugging Face | LLM | Yes |
| Ollama | LLM | No (local) |
| Pinecone | Vector DB | Yes |
| Weaviate | Vector DB | Optional |
| ChromaDB | Vector DB | No (local) |

## Anthropic (Claude)

### Getting an API Key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up or log in
3. Navigate to "API Keys"
4. Click "Create Key"
5. Copy and save the key securely

### Configuration

```toml
# .streamlit/secrets.toml
ANTHROPIC_API_KEY = "sk-ant-api03-your-key-here"
```

### Available Models

| Model | Best For | Cost |
|-------|----------|------|
| claude-sonnet-4-5 | General use (default) | $$ |
| claude-opus-4-5 | Complex tasks | $$$ |
| claude-haiku-4-5 | Fast, cheap | $ |

## OpenAI

### Getting an API Key

1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up or log in
3. Navigate to "API Keys"
4. Click "Create new secret key"
5. Copy and save the key

### Configuration

```toml
OPENAI_API_KEY = "sk-your-openai-key-here"
```

### Available Models

| Model | Best For | Cost |
|-------|----------|------|
| gpt-4o | Best quality | $$$ |
| gpt-4o-mini | Balanced | $$ |
| gpt-3.5-turbo | Fast, cheap | $ |

## Cohere

### Getting an API Key

1. Go to [dashboard.cohere.com](https://dashboard.cohere.com)
2. Sign up or log in
3. Navigate to "API Keys"
4. Copy your key

### Configuration

```toml
COHERE_API_KEY = "your-cohere-api-key"
```

### Available Models

| Model | Best For | Cost |
|-------|----------|------|
| command-r-plus | RAG tasks | $$ |
| command-r | General | $ |
| command | Basic | $ |

## Hugging Face

### Getting an API Key

1. Go to [huggingface.co](https://huggingface.co)
2. Sign up or log in
3. Navigate to [Settings > Access Tokens](https://huggingface.co/settings/tokens)
4. Click "New token"
5. Give it a name and select "Read" access (or "Write" if needed)
6. Copy and save the token

### Configuration

```toml
HF_API_KEY = "hf_your-huggingface-token-here"
```

### Available Models

| Model | Best For | Notes |
|-------|----------|-------|
| meta-llama/Meta-Llama-3.1-8B-Instruct | General use (default) | Fast, capable |
| meta-llama/Meta-Llama-3-8B-Instruct | General use | Previous generation |
| mistralai/Mistral-7B-Instruct-v0.3 | Fast inference | Efficient |
| mistralai/Mixtral-8x7B-Instruct-v0.1 | Complex tasks | MoE architecture |
| microsoft/Phi-3-mini-4k-instruct | Quick responses | Small & fast |
| google/gemma-2-9b-it | Balanced | Google's open model |
| Qwen/Qwen2.5-7B-Instruct | Multilingual | Strong in multiple languages |

### Notes

- Hugging Face Inference API provides serverless access to open models
- Some models may require accepting terms on the model page first
- Free tier has rate limits; Pro subscription available for higher limits

## Ollama (Local)

### Installation

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from ollama.com
```

### Running Ollama

```bash
# Start the server
ollama serve

# Pull a model
ollama pull llama3.2
```

### Configuration

```toml
OLLAMA_HOST = "http://localhost:11434"
```

### Available Models

- llama3.2, llama3.1, llama3
- mistral, mixtral
- codellama, phi3, gemma2

## Pinecone

### Getting an API Key

1. Go to [app.pinecone.io](https://app.pinecone.io)
2. Sign up or log in
3. Create a project
4. Copy your API key

### Configuration

```toml
PINECONE_API_KEY = "your-pinecone-api-key"
PINECONE_ENVIRONMENT = "us-east-1"  # Your region
```

## Weaviate

### Cloud Setup

1. Go to [console.weaviate.cloud](https://console.weaviate.cloud)
2. Create a cluster
3. Copy your cluster URL and API key

### Configuration

```toml
WEAVIATE_URL = "https://your-cluster.weaviate.cloud"
WEAVIATE_API_KEY = "your-weaviate-api-key"
```

### Local Setup (Docker)

```bash
docker run -d \
  -p 8080:8080 \
  cr.weaviate.io/semitechnologies/weaviate:latest
```

```toml
WEAVIATE_URL = "http://localhost:8080"
```

## Security Best Practices

### 1. Never Commit Keys

Add to `.gitignore`:
```
.env
.streamlit/secrets.toml
```

### 2. Use Environment Variables

For production, use environment variables:
```bash
export ANTHROPIC_API_KEY="your-key"
```

### 3. Rotate Keys Regularly

- Rotate API keys every 90 days
- Revoke compromised keys immediately
- Use separate keys for development/production

### 4. Limit Key Permissions

- Use read-only keys when possible
- Set usage limits in provider dashboards
- Monitor usage for anomalies

## Verifying Configuration

Run this to verify your setup:

```python
from utils.auth import validate_api_key
import os

keys = {
    "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "COHERE_API_KEY": os.getenv("COHERE_API_KEY"),
}

for name, key in keys.items():
    if key:
        print(f"✅ {name}: Configured")
    else:
        print(f"❌ {name}: Not found")
```

## Troubleshooting

### "Invalid API Key"
- Check for extra spaces or newlines
- Verify key hasn't expired
- Ensure correct provider format

### "Rate Limit Exceeded"
- Upgrade your API plan
- Implement request throttling
- Use caching for repeated queries

### "Connection Refused" (Ollama)
- Ensure Ollama is running: `ollama serve`
- Check the port isn't blocked
- Verify OLLAMA_HOST is correct
