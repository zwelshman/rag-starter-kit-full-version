# Streamlit Cloud Deployment Guide

Deploy your RAG Starter Kit Pro to Streamlit Cloud for free hosting.

## Prerequisites

- GitHub account
- Streamlit Cloud account (free at share.streamlit.io)
- Repository with your RAG application

## Step-by-Step Deployment

### 1. Prepare Your Repository

Ensure your repository has these files:
- `app.py` (main application)
- `requirements.txt` (dependencies)
- `.streamlit/config.toml` (optional, for theming)

### 2. Push to GitHub

```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

### 3. Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your GitHub repository
4. Choose the branch (usually `main`)
5. Set main file path to `app.py`

### 4. Configure Secrets

In the Streamlit Cloud dashboard:

1. Click on your app
2. Go to "Settings" > "Secrets"
3. Add your secrets in TOML format:

```toml
ANTHROPIC_API_KEY = "sk-ant-your-key-here"
OPENAI_API_KEY = "sk-your-openai-key"
COHERE_API_KEY = "your-cohere-key"
PINECONE_API_KEY = "your-pinecone-key"
```

### 5. Deploy

Click "Deploy" and wait for the build to complete.

## Configuration Options

### Custom Domain

1. Go to app settings
2. Click "Custom subdomain"
3. Enter your preferred subdomain

### Resource Limits

Streamlit Cloud provides:
- 1 GB memory (free tier)
- Automatic HTTPS
- Continuous deployment from GitHub

### Environment Variables

Besides secrets, you can set environment variables:

```toml
[server]
headless = true
port = 8501

[theme]
primaryColor = "#10B981"
```

## Optimization Tips

### 1. Reduce Cold Start Time

```python
# Use caching for expensive operations
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')
```

### 2. Optimize Dependencies

Keep `requirements.txt` minimal:
```
streamlit>=1.28.0
anthropic>=0.7.0
chromadb>=0.4.18
sentence-transformers>=2.2.2
```

### 3. Use Efficient Models

- Use `all-MiniLM-L6-v2` for embeddings (fast, small)
- Use Haiku for cost-effective responses
- Consider Ollama for local testing

## Troubleshooting

### Build Failures

Check the build logs for:
- Missing dependencies
- Python version compatibility
- File path issues

### Memory Errors

- Reduce model size
- Use `st.cache_resource` for large objects
- Process documents in batches

### Secrets Not Loading

- Verify TOML syntax
- Check for special characters (escape with `\`)
- Restart the app after adding secrets

## Monitoring

### View Logs

1. Go to app settings
2. Click "Manage app"
3. Select "Logs"

### Analytics

Streamlit Cloud provides:
- Viewer count
- Session duration
- Error tracking

## Security Best Practices

1. Never commit API keys to Git
2. Use secrets management
3. Rotate keys periodically
4. Enable authentication for sensitive data

## Next Steps

- [Alternative Deployments](10-alternative-deployments.md) - Other hosting options
- [Cost Optimization](07-cost-optimization.md) - Reduce API costs
- [Authentication Setup](04-authentication-setup.md) - Add user authentication
