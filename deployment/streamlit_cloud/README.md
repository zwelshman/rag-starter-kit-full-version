# Streamlit Cloud Deployment

Deploy your RAG Starter Kit Pro to Streamlit Cloud.

## Quick Start

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select your repository
5. Configure secrets (see below)
6. Deploy!

## Required Secrets

Add these in Streamlit Cloud Settings → Secrets:

```toml
ANTHROPIC_API_KEY = "sk-ant-your-key-here"
```

## Optional Secrets

```toml
# Additional LLM providers
OPENAI_API_KEY = "sk-your-openai-key"
COHERE_API_KEY = "your-cohere-key"

# Vector stores
PINECONE_API_KEY = "your-pinecone-key"
WEAVIATE_URL = "https://your-cluster.weaviate.cloud"
WEAVIATE_API_KEY = "your-weaviate-key"

# Application settings
AUTH_ENABLED = "true"
SECRET_KEY = "your-secret-key"
```

## Configuration

Copy `secrets.toml.example` to your local `.streamlit/secrets.toml` for development.

## Resources

- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud)
- [Managing Secrets](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
