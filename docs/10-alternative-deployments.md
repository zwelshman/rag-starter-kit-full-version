# Alternative Deployment Options

Deploy RAG Starter Kit Pro to various platforms beyond Streamlit Cloud.

## Docker Deployment

### Basic Docker Setup

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build and Run

```bash
# Build image
docker build -t rag-starter-kit .

# Run container
docker run -p 8501:8501 \
  -e ANTHROPIC_API_KEY=your-key \
  rag-starter-kit
```

### Docker Compose

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  # Optional: Local ChromaDB
  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8000:8000"
    volumes:
      - chroma-data:/chroma/chroma

volumes:
  chroma-data:
```

## Railway Deployment

### 1. Create Railway Project

```bash
npm install -g @railway/cli
railway login
railway init
```

### 2. Configure Railway

Create `railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "streamlit run app.py --server.port=$PORT --server.address=0.0.0.0",
    "healthcheckPath": "/_stcore/health"
  }
}
```

### 3. Deploy

```bash
railway up
```

### 4. Add Environment Variables

In Railway dashboard, add:
- `ANTHROPIC_API_KEY`
- Other API keys as needed

## Hugging Face Spaces

### 1. Create Space

1. Go to huggingface.co/spaces
2. Click "Create new Space"
3. Select "Streamlit" SDK
4. Choose visibility (public/private)

### 2. Configure README

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

### 3. Upload Files

```bash
git clone https://huggingface.co/spaces/your-username/rag-starter-kit
cd rag-starter-kit
# Copy your files
git add .
git commit -m "Initial deployment"
git push
```

### 4. Add Secrets

In Space Settings → Repository secrets:
- Add `ANTHROPIC_API_KEY`
- Add other secrets

## AWS Deployment

### AWS App Runner

```yaml
# apprunner.yaml
version: 1.0
runtime: python3
build:
  commands:
    build:
      - pip install -r requirements.txt
run:
  command: streamlit run app.py --server.port=8080 --server.address=0.0.0.0
  network:
    port: 8080
```

### AWS ECS with Fargate

1. Push Docker image to ECR
2. Create ECS cluster
3. Define task definition
4. Create service

### AWS Lambda (API-only)

For API-only deployment without Streamlit UI:

```python
# lambda_handler.py
from mangum import Mangum
from fastapi import FastAPI

app = FastAPI()

@app.post("/query")
async def query(question: str):
    response = pipeline.query(question)
    return {"answer": response}

handler = Mangum(app)
```

## Google Cloud Platform

### Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/rag-starter-kit

# Deploy
gcloud run deploy rag-starter-kit \
  --image gcr.io/PROJECT_ID/rag-starter-kit \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars ANTHROPIC_API_KEY=your-key
```

### App Engine

Create `app.yaml`:
```yaml
runtime: python39
entrypoint: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0

instance_class: F2

env_variables:
  ANTHROPIC_API_KEY: "your-key"

automatic_scaling:
  min_instances: 0
  max_instances: 2
```

Deploy:
```bash
gcloud app deploy
```

## Azure Deployment

### Azure Container Apps

```bash
# Create container app
az containerapp create \
  --name rag-starter-kit \
  --resource-group myResourceGroup \
  --environment myContainerAppEnv \
  --image your-registry/rag-starter-kit:latest \
  --target-port 8501 \
  --env-vars ANTHROPIC_API_KEY=your-key
```

### Azure App Service

```bash
# Create web app
az webapp create \
  --resource-group myResourceGroup \
  --plan myAppServicePlan \
  --name rag-starter-kit \
  --runtime "PYTHON:3.11"

# Configure
az webapp config appsettings set \
  --name rag-starter-kit \
  --settings ANTHROPIC_API_KEY=your-key
```

## Kubernetes Deployment

### Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rag-starter-kit
spec:
  replicas: 2
  selector:
    matchLabels:
      app: rag-starter-kit
  template:
    metadata:
      labels:
        app: rag-starter-kit
    spec:
      containers:
      - name: app
        image: your-registry/rag-starter-kit:latest
        ports:
        - containerPort: 8501
        env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: anthropic-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: rag-starter-kit
spec:
  selector:
    app: rag-starter-kit
  ports:
  - port: 80
    targetPort: 8501
  type: LoadBalancer
```

### Deploy

```bash
kubectl apply -f deployment.yaml
```

## Render

### 1. Create Service

1. Go to render.com
2. New → Web Service
3. Connect your repository
4. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

### 2. Environment Variables

Add in Render dashboard:
- `ANTHROPIC_API_KEY`
- `PYTHON_VERSION=3.11`

## Comparison Table

| Platform | Free Tier | Scaling | Setup Complexity |
|----------|-----------|---------|------------------|
| Streamlit Cloud | Yes | Limited | Easy |
| Railway | $5 credit | Auto | Easy |
| HF Spaces | Yes (public) | Limited | Easy |
| Docker | N/A | Manual | Medium |
| AWS | Free tier | Auto | Complex |
| GCP | Free tier | Auto | Complex |
| Azure | Free tier | Auto | Complex |
| Kubernetes | N/A | Auto | Complex |
| Render | Yes | Auto | Easy |

## Choosing a Platform

**For prototypes/demos:**
- Streamlit Cloud
- Hugging Face Spaces

**For production:**
- AWS/GCP/Azure for enterprise
- Railway/Render for startups
- Kubernetes for large scale

**For self-hosted:**
- Docker + Docker Compose
- Kubernetes
