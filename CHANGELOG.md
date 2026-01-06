# Changelog

All notable changes to RAG Starter Kit Pro will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.8] - 2025-01-05

### Added
- **Hybrid Search Weighting**: New slider to adjust balance between semantic (vector) and keyword (BM25) search
  - 0.0 = Pure BM25 keyword matching
  - 0.5 = Balanced (default)
  - 1.0 = Pure semantic vector search
  - Visual indicator shows current balance percentages
  - Only visible when Hybrid search mode is selected

### Documentation
- Added Hybrid Search Settings section to README
- Updated settings table with semantic weight parameter

## [2.0.7] - 2025-01-05

### Fixed
- **Export Chat Button**: Now correctly enables after running a query (was staying disabled)
- **Cost Tracking**: Fixed model name mismatch - prices now correctly calculated for `claude-sonnet-4-5`, `claude-opus-4-5`, `claude-haiku-4-5`
- **Chat UI**: Added auto-refresh after response to update button states and scroll position

## [2.0.6] - 2025-01-05

### Fixed
- **N Results Parameter**: Chat interface now correctly passes `n_results` from settings slider to search
  - Previously hardcoded to 5 results regardless of slider value
  - Now properly uses the configured value (default: 20)
- **Context Display**: Full prompt view now shows all retrieved sources, not just first 5

## [2.0.5] - 2025-01-05

### Improved
- **Response Styles**: Clear differentiation with format hints:
  - Basic: 1-2 focused paragraphs
  - Concise: Bullet points, <100 words
  - Detailed: Structured, multi-section response
- **Domain-Specific Prompts**: Enhanced all templates with unique, specialized instructions:
  - Q&A: Direct answers from documents
  - Summarization: Extract and condense with logical organization
  - Analysis: Critical patterns, relationships, implications
  - Legal: Clauses, obligations, rights with legal precision
  - Medical: Clinical findings with proper terminology
  - Technical: Specs, code examples, step-by-step guidance
  - Business: KPIs, trends, strategic insights

### Changed
- **Max Tokens**: Increased limit from 4,000 to 50,000 for detailed analysis

### Documentation
- Updated README.md with response style format hints
- Cleaned up duplicate content in documentation

## [2.0.4] - 2025-01-05

### Added
- **Domain-Specific Templates**: Each template type now has specialized prompts:
  - Q&A: General question answering
  - Summarization: Extract and condense key information
  - Analysis: Identify patterns, insights, implications
  - Legal: Review clauses, terms, legal considerations (with disclaimer)
  - Medical: Clinical findings, studies, guidelines (with disclaimer)
  - Technical: Specifications, code, technical details
  - Business: Metrics, trends, strategic insights
- **Proceed to Chat Button**: Added "➡️ Proceed to Chat" button after template selection

### Improved
- **Template System**: Templates now combine domain-specific context with response style modifiers
- **User Flow**: Clearer navigation from template selection to chat

### Documentation
- Updated README.md with template types table and use cases
- Updated Quick Start guide with domain-specific template descriptions

## [2.0.3] - 2025-01-05

### Fixed
- **Model Names**: Fixed Anthropic model names to use correct format (claude-sonnet-4-5, claude-opus-4-5, claude-haiku-4-5)
- **Template Context Display**: "View Full Prompt Sent to LLM" now shows actual retrieved context instead of `{context}` placeholder

### Improved
- **Prompt Preview**: Shows "Retrieved X document chunks from vector database" with actual content
- **Context Visibility**: Users can now see exactly what document content was sent to the LLM

### Documentation
- Updated all model references to correct Anthropic model names
- Updated troubleshooting guide for model name errors

## [2.0.2] - 2025-01-05

### Added
- **Template Response Styles**: Choose from Basic, Concise, or Detailed response styles
  - Basic: Simple and straightforward responses
  - Concise: Brief, direct answers only
  - Detailed: Comprehensive answers with examples
- **Export Chat Button**: Added "📥 Export Chat" button to Chat tab for quick access
- **Clear Chat Button**: Added "🗑️ Clear Chat" button to Chat tab for convenience

### Improved
- **Template Selection UI**: Redesigned with side-by-side Template Type and Response Style dropdowns
- **Chat Controls**: All chat controls (Clear, Export, Clear Template) now in convenient button row
- **Template Types**: Expanded to include Q&A, Summarization, Analysis, Legal, Medical, Technical, Business

### Documentation
- Updated README.md with new template styles and chat controls
- Updated Quick Start guide with template style selection instructions

## [2.0.1] - 2025-01-05

### Fixed
- **LLM Model Names**: Corrected Anthropic model names (claude-sonnet-4-5, claude-opus-4, claude-3-5-haiku-latest)
- **Pipeline Initialization**: Fixed create_pipeline() to accept llm_provider and llm_model parameters
- **Cost Tracking Model Reference**: Fixed default model name in cost tracking

### Improved
- **Template UX**: Enhanced template selection with clearer active template display in Chat tab
- **Chat Interface**: Added tip for users to select templates, improved template visibility
- **Manage Data**: Now displays list of all loaded documents with count
- **Default Vector DB Info**: Sidebar now shows ChromaDB as the default vector database
- **Tab Order**: Reordered tabs - Prompt Templates now comes right after Upload Documents
- **Cost Tracking Label**: Renamed to "Cost Tracking (Experimental)" for clarity

### Documentation
- Updated README.md with comprehensive Pro version features
- Updated Quick Start guide with correct model names and workflow
- Added tab overview and template usage instructions
- Documented default vector database (ChromaDB)

## [2.0.0] - 2025-01-05

### Added

#### LLM Providers
- **Cohere Integration** - Full support for Command R and Command R+ models
- **Ollama Integration** - Local LLM inference with support for Llama, Mistral, and more
- Expanded Anthropic support with multiple Claude models
- Provider cost estimation functions

#### Vector Stores
- **Pinecone Integration** - Cloud-native vector database support
- **Weaviate Integration** - Open-source vector database with cloud and self-hosted options
- Vector store factory pattern for easy switching

#### Authentication & User Management
- User registration and login system
- Role-based access control (admin, user, viewer)
- Session management with configurable timeout
- Brute force protection with account lockout

#### Analytics & Cost Tracking
- Real-time query analytics dashboard
- Token usage tracking and cost calculation
- Budget alerts and daily/monthly limits
- Provider-specific cost breakdowns
- Export analytics data

#### Prompt Templates
- **55+ prompt templates** organized by category:
  - General: Q&A, Summarization, Analysis (30 templates)
  - Domain-specific: Legal, Medical, Technical, Business (20 templates)
  - Advanced: Multi-hop reasoning, Comparison, Extraction (15 templates)
- Prompt template library UI

#### Documentation
- 10 comprehensive documentation guides:
  - Quick Start Guide
  - Streamlit Cloud Deployment
  - API Keys Setup
  - Authentication Setup
  - Customization Guide
  - Prompt Engineering Guide
  - Cost Optimization Guide
  - Advanced RAG Techniques
  - Troubleshooting Guide
  - Alternative Deployments

#### Deployment
- Docker support with docker-compose
- Railway deployment configuration
- Hugging Face Spaces support
- GitHub Actions CI/CD pipeline
- Streamlit Cloud optimized configuration

#### Examples & Integrations
- Slack bot integration
- Discord bot integration
- REST API wrapper (FastAPI)
- Sample documents

#### Bonuses
- Advanced chat component
- Analytics dashboard component
- Extended prompt library

### Changed
- **Unlimited documents** - Removed document limit from demo version
- **Unlimited queries** - Removed query limit from demo version
- Improved main app.py with full version features
- Enhanced sidebar with provider selection
- Updated UI theme and branding

### Improved
- Better error handling across all components
- Improved logging with structured format
- Enhanced cost tracking accuracy
- Optimized document processing pipeline

## [1.0.0] - 2024-12-01

### Added
- Initial demo version release
- Basic RAG pipeline with ChromaDB
- Anthropic Claude Sonnet 4.5 integration
- OpenAI GPT models support
- Hybrid search (Vector + BM25)
- Document upload (TXT, PDF, DOCX, XLSX, CSV, JSON)
- Chat interface with streaming
- Basic prompt templates
- Streamlit-based UI

### Limitations (Demo Version)
- 3 documents maximum
- 10 queries maximum
- Single LLM provider
- Local vector store only

---

## Migration Guide

### From 1.0.0 to 2.0.0

1. **Update requirements.txt**
   ```bash
   pip install -r requirements.txt
   ```

2. **Update imports** (if using custom code)
   ```python
   # Old
   from core.llm_providers import AnthropicClient

   # New - use factory
   from core.llm_providers import LLMClient
   client = LLMClient(provider="anthropic")
   ```

3. **Add new API keys** (optional)
   ```toml
   # .streamlit/secrets.toml
   COHERE_API_KEY = "your-key"
   PINECONE_API_KEY = "your-key"
   ```

4. **Enable new features**
   - Authentication: Set `AUTH_ENABLED = "true"`
   - Cost tracking: Automatically enabled

---

## Roadmap

### Planned for 2.1.0
- [ ] Multi-language support
- [ ] Advanced reranking options
- [ ] Custom embedding models
- [ ] Batch document processing
- [ ] Scheduled document updates

### Planned for 3.0.0
- [ ] Agent capabilities
- [ ] Tool use / function calling
- [ ] Knowledge graph integration
- [ ] Multi-modal support (images, audio)
