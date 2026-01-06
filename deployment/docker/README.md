# Docker Deployment

Deploy RAG Starter Kit Pro using Docker.

## Quick Start

### 1. Build and Run

```bash
# Set your API key
export ANTHROPIC_API_KEY="sk-ant-your-key"

# Run with docker-compose
docker-compose up -d
```

### 2. Access the Application

Open http://localhost:8501 in your browser.

## Docker Commands

### Build only
```bash
docker build -t rag-starter-kit -f deployment/docker/Dockerfile .
```

### Run standalone
```bash
docker run -p 8501:8501 \
  -e ANTHROPIC_API_KEY=your-key \
  rag-starter-kit
```

### View logs
```bash
docker-compose logs -f rag-app
```

### Stop services
```bash
docker-compose down
```

### Remove volumes
```bash
docker-compose down -v
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| rag-app | 8501 | Main Streamlit application |
| chromadb | 8000 | ChromaDB vector database |
| ollama | 11434 | Local LLM inference (optional) |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| ANTHROPIC_API_KEY | Yes | Anthropic API key |
| OPENAI_API_KEY | No | OpenAI API key |
| COHERE_API_KEY | No | Cohere API key |
| PINECONE_API_KEY | No | Pinecone API key |

## Using Ollama

After starting the stack:

```bash
# Pull a model
docker exec -it ollama ollama pull llama3.2

# List models
docker exec -it ollama ollama list
```

## GPU Support (NVIDIA)

Uncomment the GPU configuration in `docker-compose.yml`:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

Install NVIDIA Container Toolkit first:
```bash
# Ubuntu
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

## Production Considerations

1. Use environment-specific compose files
2. Configure proper logging
3. Set up monitoring and alerting
4. Use secrets management (Docker secrets, Vault, etc.)
5. Configure resource limits
6. Set up backup for volumes
