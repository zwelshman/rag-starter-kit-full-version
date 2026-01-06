# Quick Start Guide

Get your RAG Starter Kit Pro up and running in minutes.

## Prerequisites

- Python 3.9 or higher
- API key from at least one LLM provider (Anthropic recommended)
- Git (for cloning the repository)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/rag-starter-kit-pro.git
cd rag-starter-kit-pro
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

Create a `.streamlit/secrets.toml` file:

```toml
# Required: At least one LLM provider
ANTHROPIC_API_KEY = "sk-ant-your-anthropic-api-key"

# Optional: Additional providers
OPENAI_API_KEY = "sk-your-openai-api-key"
COHERE_API_KEY = "your-cohere-api-key"

# Optional: Cloud vector stores
PINECONE_API_KEY = "your-pinecone-key"
WEAVIATE_API_KEY = "your-weaviate-key"
```

### 5. Run the Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## First Steps

### 1. Configure Your Provider

1. Look at the sidebar on the left
2. Select your LLM provider (Anthropic, OpenAI, Cohere, or Ollama)
3. Choose a model from the dropdown:
   - **Anthropic**: claude-sonnet-4-5 (default), claude-opus-4-5, claude-haiku-4-5
   - **OpenAI**: gpt-4o (default), gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo
   - **Cohere**: command-r-plus (default), command-r, command
   - **Ollama**: llama3.2 (default), llama3.1, mistral, mixtral, codellama
4. Click "Initialize Pipeline"
5. The sidebar will show the default vector database: **ChromaDB**

### 2. Upload Documents

1. Go to the **📤 Upload Documents** tab
2. Click "Browse files" to select documents
3. Supported formats: TXT, PDF, DOCX, XLSX, CSV, JSON
4. Click "Process Documents" to index them
5. Check **⚙️ Manage Data** tab to see your uploaded files

### 3. Select a Template (Optional)

1. Go to the **📝 Prompt Templates** tab
2. Choose a **Template Type** (each has domain-specific prompts):
   - **Q&A**: General question and answer
   - **Summarization**: Extract and condense key information
   - **Analysis**: Identify patterns, insights, implications
   - **Legal**: Review clauses, terms, legal considerations
   - **Medical**: Clinical findings, studies, guidelines
   - **Technical**: Specifications, code, technical details
   - **Business**: Metrics, trends, strategic insights
3. Choose a **Response Style**:
   - **Basic**: Simple and straightforward responses
   - **Concise**: Brief, direct answers only
   - **Detailed**: Comprehensive answers with examples
4. Click **"Use This Template"** to activate
5. Click **"➡️ Proceed to Chat"** to go to the Chat tab

### 4. Ask Questions

1. Go to the **💬 Chat** tab
2. You'll see your active template displayed in a green banner at the top
3. Use the control buttons:
   - **🗑️ Clear Chat**: Clear conversation history
   - **📥 Export Chat**: Download chat history as JSON
   - **Clear Template**: Remove active template
4. Type your question in the input field
5. Press Enter to send
6. View the full prompt sent to the LLM by clicking "View Full Prompt Sent to LLM"
7. View sources by clicking "View Sources" in the response

## Tab Overview

| Tab | Description |
|-----|-------------|
| 📤 Upload Documents | Upload and process your documents |
| 📝 Prompt Templates | Select from 50+ templates to customize responses |
| 💬 Chat | Ask questions with template integration |
| 📊 Analytics | View query and document statistics |
| 💰 Cost Tracking (Experimental) | Monitor usage costs |
| ⚙️ Manage Data | View loaded documents, clear data, export chat |

## Quick Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| LLM Provider | AI model provider | Anthropic |
| LLM Model | Specific model | claude-sonnet-4-5 |
| Vector Store | Document storage | ChromaDB |
| Search Mode | Retrieval method | Hybrid |
| Chunk Size | Text chunk size | 300 |
| Chunk Overlap | Overlap between chunks | 50 |
| N Results | Chunks to retrieve | 20 |
| Temperature | Response creativity | 0.7 |
| Max Tokens | Max response length | 2000 |

## Troubleshooting

### "API key not found"
- Check that your `.streamlit/secrets.toml` file exists
- Verify the key format is correct (e.g., `sk-ant-...` for Anthropic)
- Restart the application

### "Model not found" error
- Ensure you're using the correct model name (e.g., `claude-sonnet-4-5`)
- Check that your API key has access to the selected model
- Available Anthropic models: claude-sonnet-4-5, claude-opus-4-5, claude-haiku-4-5

### "No documents loaded"
- Ensure documents are in a supported format
- Check file size (max 10MB per file)
- Try re-uploading
- Check the **⚙️ Manage Data** tab to see loaded files

### "Connection error"
- Verify your internet connection
- Check if the API service is available
- Review API key permissions

### Template not showing in Chat
- Make sure you clicked "Use This Template" in the Prompt Templates tab
- The active template will be displayed at the top of the Chat tab
- You can clear the template using the "Clear Template" button

## Next Steps

- [API Keys Setup](03-api-keys-setup.md) - Detailed API configuration
- [Customization Guide](05-customization-guide.md) - Customize the application
- [Deployment Guide](02-streamlit-cloud-deployment.md) - Deploy to production
- [Prompt Engineering](06-prompt-engineering.md) - Create effective prompts
