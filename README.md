# 🚀 RAG Starter Kit Pro

A production-ready, modular Retrieval-Augmented Generation (RAG) application with multi-provider support, built with Streamlit.

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)]([https://streamlit.io](https://document-search-template.streamlit.app/))
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

### Full Version Capabilities
- 🚀 **Unlimited Documents & Queries** - No restrictions on usage
- 🧠 **4 LLM Providers** - Anthropic (Claude), OpenAI (GPT), Cohere, Ollama (local)
- 🗄️ **3 Vector Databases** - ChromaDB (default), Pinecone, Weaviate
- 📝 **50+ Prompt Templates** - General, domain-specific, and advanced templates
- 🔐 **Authentication & User Management** - Role-based access control
- 💰 **Cost Tracking (Experimental)** - Monitor token usage and costs
- 📊 **Analytics Dashboard** - Track queries, documents, and performance
- 🚀 **Production Deployment** - Docker, Railway, HuggingFace Spaces, Streamlit Cloud

### Core Features
- 📁 **Multi-Format Support**: PDF, DOCX, TXT, CSV, XLSX, JSON
- 🔍 **Hybrid Search**: Combines vector similarity and BM25 keyword search
- 💬 **Streaming Responses**: Real-time response generation
- 📊 **Source Citations**: View which documents informed each answer
- 🎨 **Clean UI**: Intuitive Streamlit interface with tab-based navigation
- 🔧 **Highly Configurable**: Adjust chunk size, search mode, and LLM parameters

## 🏗️ Architecture

```
rag-starter-kit-pro/
├── 🎯 app.py                          # Main Streamlit app
├── 📋 requirements.txt                # Dependencies
├── 📁 components/                     # UI Components
│   ├── file_uploader.py              # Document upload UI
│   ├── chat_interface.py             # Chat UI with template integration
│   ├── settings_panel.py             # Configuration panel
│   ├── citation_viewer.py            # Source display
│   ├── analytics.py                  # Analytics dashboard
│   └── cost_tracker.py               # Cost tracking (experimental)
├── 📁 core/                           # Core RAG Engine
│   ├── vector_stores/                # Vector DB implementations
│   │   ├── base.py                   # Base interface
│   │   ├── chroma.py                 # ChromaDB (default)
│   │   ├── pinecone_store.py         # Pinecone
│   │   └── weaviate_store.py         # Weaviate
│   ├── llm_providers/                # LLM integrations
│   │   ├── base.py                   # Base interface
│   │   ├── anthropic_provider.py     # Anthropic (Claude)
│   │   ├── openai_provider.py        # OpenAI (GPT)
│   │   ├── cohere_provider.py        # Cohere
│   │   ├── ollama_provider.py        # Ollama (local)
│   │   └── factory.py                # Provider factory
│   ├── document_processor.py         # Document loading & chunking
│   └── retrieval_engine.py           # Main RAG pipeline
├── 📁 prompts/                        # 50+ Prompt templates
│   ├── general/                      # Q&A, Summarization, Analysis
│   ├── domain_specific/              # Legal, Medical, Technical, Business
│   └── advanced/                     # Multi-hop, Comparison, Extraction
├── 📁 docs/                           # Documentation (10 guides)
├── 📁 deployment/                     # Deployment configs
│   ├── docker/
│   ├── railway/
│   ├── huggingface_spaces/
│   └── github_actions/
└── 📁 examples/                       # Integration examples
    └── custom_integrations/          # Slack, Discord, API wrapper
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd rag-starter-kit-pro

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up API Key

Create `.streamlit/secrets.toml`:

```toml
# Required: At least one LLM provider
ANTHROPIC_API_KEY = "sk-ant-your-api-key-here"

# Optional: Additional providers
OPENAI_API_KEY = "sk-your-openai-key"
COHERE_API_KEY = "your-cohere-key"

# Optional: Cloud vector stores
PINECONE_API_KEY = "your-pinecone-key"
WEAVIATE_API_KEY = "your-weaviate-key"
```

Get your API keys:
- [Anthropic Console](https://console.anthropic.com/)
- [OpenAI Platform](https://platform.openai.com/)
- [Cohere Dashboard](https://dashboard.cohere.com/)

### 3. Run the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

### 4. Use the App

1. **Configure Provider**: Select your LLM provider and model in the sidebar
2. **Initialize Pipeline**: Click "Initialize Pipeline" (default: ChromaDB vector store)
3. **Upload Documents**: Go to "Upload Documents" tab and add your files
4. **Select Template** (Optional): Choose a prompt template from "Prompt Templates" tab
5. **Ask Questions**: Go to "Chat" tab and start querying your documents!

## 📋 Tab Overview

| Tab | Description |
|-----|-------------|
| 📤 Upload Documents | Upload and process your documents |
| 📝 Prompt Templates | Select from 50+ templates to customize responses |
| 💬 Chat | Ask questions with template integration |
| 📊 Analytics | View query and document statistics |
| 💰 Cost Tracking | Monitor usage costs (experimental) |
| ⚙️ Manage Data | Clear data, export chat history |

## 🔧 Configuration Options

### LLM Providers & Models

| Provider | Models | Default |
|----------|--------|---------|
| Anthropic | claude-sonnet-4-5, claude-opus-4-5, claude-haiku-4-5 | claude-sonnet-4-5 |
| OpenAI | gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo | gpt-4o |
| Cohere | command-r-plus, command-r, command | command-r-plus |
| Ollama | llama3.2, llama3.1, mistral, mixtral, codellama | llama3.2 |

### Vector Database

**Default**: ChromaDB (local, no API key required)

| Vector Store | Type | Best For |
|--------------|------|----------|
| ChromaDB | Local | Development, small-medium datasets |
| Pinecone | Cloud | Production, large-scale deployments |
| Weaviate | Cloud/Self-hosted | Enterprise, complex queries |

### Search Modes

| Mode | Description | Best For |
|------|-------------|----------|
| Hybrid (default) | Combines Vector + BM25 | Most use cases |
| Vector | Semantic similarity only | Conceptual queries |
| BM25 | Keyword matching only | Exact term search |

### Hybrid Search Settings

When using **Hybrid (Combined)** search mode, you can adjust the balance between semantic and keyword search:

| Value | Effect |
|-------|--------|
| 0.0 | Pure keyword (BM25) - exact term matching |
| 0.5 | Balanced (default) - equal weight to both |
| 1.0 | Pure semantic (Vector) - meaning-based matching |

**Tip**: Use higher semantic weight for conceptual questions, higher BM25 weight for specific terms/codes.

### Other Settings

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Chunk Size | 300 | 200-2000 | Characters per text chunk |
| Chunk Overlap | 50 | 0-500 | Overlap between chunks |
| N Results | 20 | 1-20 | Document chunks to retrieve |
| Temperature | 0.7 | 0-1 | Response creativity |
| Max Tokens | 4000 | 100-50,000 | Maximum response length |
| Semantic Weight | 0.5 | 0-1 | Hybrid search balance (0=BM25, 1=Vector) |

## 📝 Using Templates

### Template Types (Domain-Specific)

Each template type has a specialized prompt designed for its domain:

| Type | Description | What It Does |
|------|-------------|--------------|
| **Q&A** | General Question and Answer | Direct answers from documents |
| **Summarization** | Document Summarization | Extracts and condenses key information |
| **Analysis** | Critical Document Analysis | Identifies patterns, relationships, implications |
| **Legal** | Legal Document Review | Clauses, obligations, rights, potential issues (with disclaimer) |
| **Medical** | Medical Literature Analysis | Clinical findings, studies, terminology (with disclaimer) |
| **Technical** | Technical Documentation Expert | Specs, code examples, step-by-step guidance |
| **Business** | Business Intelligence & Strategy | KPIs, trends, risks, actionable insights |

### Response Styles

Each style produces distinctly different output formats:

| Style | Output Format | Best For |
|-------|---------------|----------|
| **Basic** | 1-2 focused paragraphs | Quick answers, simple queries |
| **Concise** | Bullet points, <100 words | Rapid review, key facts only |
| **Detailed** | Structured multi-section response | Deep analysis, comprehensive review |

### Example: Same Question, Different Styles

**Question**: "What are the main findings?"

- **Basic**: Clear 1-2 paragraph summary
- **Concise**: • Finding 1 • Finding 2 • Finding 3
- **Detailed**: Overview → Detailed Analysis → Evidence → Caveats

### How to Use

1. Go to **Prompt Templates** tab
2. Select a **Template Type** (domain-specific prompt)
3. Select a **Response Style** (output format)
4. Click **"Use This Template"** to activate
5. Click **"➡️ Proceed to Chat"** or go to **Chat** tab
6. Type your question - template formats it with retrieved context
7. View the full prompt via "View Full Prompt Sent to LLM" expander

### Chat Controls
- **🗑️ Clear Chat**: Clear conversation history
- **📥 Export Chat**: Download chat history as JSON
- **Clear Template**: Remove active template

## 📖 Documentation

- [Quick Start Guide](docs/01-quick-start.md)
- [Streamlit Cloud Deployment](docs/02-streamlit-cloud-deployment.md)
- [API Keys Setup](docs/03-api-keys-setup.md)
- [Authentication Setup](docs/04-authentication-setup.md)
- [Customization Guide](docs/05-customization-guide.md)
- [Prompt Engineering](docs/06-prompt-engineering.md)
- [Cost Optimization](docs/07-cost-optimization.md)
- [Advanced RAG Techniques](docs/08-advanced-rag.md)
- [Troubleshooting](docs/09-troubleshooting.md)
- [Alternative Deployments](docs/10-alternative-deployments.md)

## 🚀 Deployment

### Streamlit Cloud (Easiest)

1. Push to GitHub
2. Connect to [Streamlit Cloud](https://share.streamlit.io)
3. Add API keys in Secrets
4. Deploy!

### Docker

```bash
cd deployment/docker
docker-compose up
```

### Other Platforms

- [Railway](deployment/railway/)
- [Hugging Face Spaces](deployment/huggingface_spaces/)
- [GitHub Actions CI/CD](deployment/github_actions/)

## 📊 Programmatic Usage

```python
from core.retrieval_engine import create_pipeline, SearchMode

# Initialize the pipeline
pipeline = create_pipeline(
    api_key="your-api-key",
    search_mode="Hybrid (Combined)",
    chunk_size=300,
    chunk_overlap=50,
    n_results=20,
    llm_provider="anthropic",
    llm_model="claude-sonnet-4-5",
)

# Add documents
result = pipeline.add_documents(file_paths=["document.pdf", "data.csv"])
print(f"Added {result['chunks']} chunks from {result['documents']} documents")

# Query the pipeline
response = pipeline.query("What is the main topic of the documents?")
print(response.answer)
```

## 🎯 Use Cases

- 📄 **Document Q&A**: Ask questions about your documents
- 🔍 **Research Assistant**: Search through research papers
- 📚 **Knowledge Base**: Build a searchable knowledge base
- 💼 **Business Intelligence**: Query business documents
- 📖 **Study Aid**: Interact with textbooks and notes
- ⚖️ **Legal Research**: Analyze legal documents with specialized templates
- 🏥 **Medical Analysis**: Review medical literature with domain-specific prompts

## 📝 License

MIT License

---

Made with ❤️ using Claude, GPT, Cohere, and Ollama
