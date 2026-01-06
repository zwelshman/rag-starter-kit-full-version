# Hugging Face Spaces Deployment

Deploy RAG Starter Kit Pro to Hugging Face Spaces.

## Quick Start

### 1. Create a Space

1. Go to [huggingface.co/spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Choose:
   - Owner: Your username/organization
   - Space name: rag-starter-kit
   - SDK: Streamlit
   - Visibility: Public or Private

### 2. Clone the Space

```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/rag-starter-kit
cd rag-starter-kit
```

### 3. Copy Your Files

```bash
cp -r /path/to/rag-starter-kit/* .
```

### 4. Update README

Ensure the README.md has the correct front matter (see app.py in this directory).

### 5. Push to Hugging Face

```bash
git add .
git commit -m "Initial deployment"
git push
```

### 6. Add Secrets

In Space Settings → Repository secrets:
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY` (optional)
- Other API keys as needed

## README Front Matter

Your README.md must have this front matter:

```yaml
---
title: RAG Starter Kit Pro
emoji: 🚀
colorFrom: green
colorTo: blue
sdk: streamlit
sdk_version: 1.28.0
app_file: app.py
pinned: false
---
```

## Hardware Options

- CPU Basic (free)
- CPU Upgrade ($0.03/hr)
- GPU: T4 small/medium ($0.40-0.60/hr)

## Persistence

Hugging Face Spaces don't persist data by default.
For persistence, use:
- Hugging Face Datasets
- External vector stores (Pinecone, Weaviate)

## Private Spaces

For private Spaces, set visibility to "Private" during creation.
Access requires Hugging Face authentication.

## Troubleshooting

### Build Errors
Check the "Logs" tab in your Space.

### Secret Not Found
Verify secrets are added in Repository secrets, not regular settings.

### Out of Memory
Consider upgrading hardware or optimizing the application.
