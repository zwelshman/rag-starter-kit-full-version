# Railway Deployment

Deploy RAG Starter Kit Pro to Railway.

## Quick Start

### 1. Install Railway CLI

```bash
npm install -g @railway/cli
```

### 2. Login and Initialize

```bash
railway login
railway init
```

### 3. Deploy

```bash
railway up
```

### 4. Add Environment Variables

In the Railway dashboard:
1. Go to your project
2. Click on the service
3. Go to "Variables"
4. Add your API keys:
   - `ANTHROPIC_API_KEY`
   - `OPENAI_API_KEY` (optional)
   - `COHERE_API_KEY` (optional)

## Configuration

The `railway.json` file configures:
- Build: Uses Nixpacks
- Start Command: Runs Streamlit with dynamic port
- Health Check: Uses Streamlit's health endpoint

## Custom Domain

1. Go to Settings in Railway dashboard
2. Click "Generate Domain" or add custom domain
3. Configure DNS if using custom domain

## Scaling

Railway automatically scales based on usage:
- Configure in Railway dashboard
- Set memory/CPU limits as needed

## Costs

- Free tier: $5 of usage
- Paid: Pay per usage (CPU, memory, network)

## Troubleshooting

### Build Failures
Check the build logs in Railway dashboard.

### Port Issues
Railway sets `$PORT` automatically. The app is configured to use it.

### Memory Issues
Increase memory allocation in Railway settings.
