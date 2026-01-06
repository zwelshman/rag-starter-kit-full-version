# Customization Guide

Customize RAG Starter Kit Pro to match your needs.

## Theming

### Streamlit Theme

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#10B981"        # Emerald green
backgroundColor = "#FFFFFF"     # White
secondaryBackgroundColor = "#F3F4F6"
textColor = "#1F2937"
font = "sans serif"
```

### Custom CSS

Add custom styles in your app:

```python
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stButton > button {
        border-radius: 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)
```

## LLM Configuration

### Switching Providers

```python
from core.llm_providers import LLMClient

# Use OpenAI
client = LLMClient(provider="openai", model="gpt-4o")

# Use Cohere
client = LLMClient(provider="cohere", model="command-r-plus")

# Use Ollama (local)
client = LLMClient(provider="ollama", model="llama3.2")
```

### Custom System Prompts

```python
CUSTOM_SYSTEM_PROMPT = """
You are an expert assistant for [YOUR DOMAIN].
Always respond in [LANGUAGE/STYLE].
Focus on [SPECIFIC ASPECTS].
"""

response = pipeline.query(
    question=user_query,
    system_prompt=CUSTOM_SYSTEM_PROMPT
)
```

## Vector Store Configuration

### Using Pinecone

```python
from core.vector_stores import PineconeVectorStore

vector_store = PineconeVectorStore(
    api_key="your-key",
    index_name="my-documents",
    dimension=384,
    metric="cosine"
)
```

### Using Weaviate

```python
from core.vector_stores import WeaviateVectorStore

vector_store = WeaviateVectorStore(
    url="https://your-cluster.weaviate.cloud",
    api_key="your-key",
    class_name="Document"
)
```

## Document Processing

### Custom Chunking

```python
from core.document_processor import DocumentProcessor

processor = DocumentProcessor(
    chunk_size=500,      # Characters per chunk
    chunk_overlap=100,   # Overlap between chunks
)
```

### Adding New File Formats

```python
class DocumentProcessor:
    def _load_custom_format(self, file_path):
        # Your custom loading logic
        content = parse_custom_file(file_path)
        return [Document(content=content, metadata={"source": file_path})]
```

## Search Configuration

### Hybrid Search Tuning

```python
# Adjust BM25 parameters
bm25_search = BM25Search(k1=1.5, b=0.75)

# Adjust hybrid weights
hybrid_search = HybridSearch(
    vector_weight=0.7,  # 70% semantic
    bm25_weight=0.3     # 30% keyword
)
```

### Custom Reranking

```python
def custom_rerank(results, query):
    # Implement your reranking logic
    scored_results = []
    for result in results:
        custom_score = calculate_custom_score(result, query)
        scored_results.append((result, custom_score))
    return sorted(scored_results, key=lambda x: x[1], reverse=True)
```

## UI Customization

### Custom Components

```python
def custom_chat_message(message, is_user=False):
    if is_user:
        st.markdown(f"""
        <div class="user-message">
            <span class="avatar">👤</span>
            <p>{message}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="ai-message">
            <span class="avatar">🤖</span>
            <p>{message}</p>
        </div>
        """, unsafe_allow_html=True)
```

### Custom Sidebar

```python
def render_custom_sidebar():
    with st.sidebar:
        st.image("logo.png", width=200)
        st.title("My RAG App")

        # Custom settings
        theme = st.selectbox("Theme", ["Light", "Dark"])
        language = st.selectbox("Language", ["English", "Spanish", "French"])

        return theme, language
```

## Adding Features

### Custom Analytics

```python
def track_custom_metric(metric_name, value):
    if 'custom_metrics' not in st.session_state:
        st.session_state.custom_metrics = {}

    st.session_state.custom_metrics[metric_name] = value
```

### Export Functionality

```python
def export_to_pdf(chat_history):
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for message in chat_history:
        pdf.cell(200, 10, txt=message['content'], ln=True)

    return pdf.output(dest='S').encode('latin-1')
```

## API Integration

### REST API Wrapper

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class QueryRequest(BaseModel):
    question: str
    temperature: float = 0.7

@app.post("/query")
async def query(request: QueryRequest):
    response = pipeline.query(request.question)
    return {"answer": response}
```

### Webhook Integration

```python
import requests

def send_webhook(event_type, data):
    webhook_url = st.secrets.get("WEBHOOK_URL")
    if webhook_url:
        requests.post(webhook_url, json={
            "event": event_type,
            "data": data
        })
```

## Performance Optimization

### Caching

```python
@st.cache_resource
def load_embedding_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_cached_response(query_hash):
    return cached_responses.get(query_hash)
```

### Batch Processing

```python
def process_documents_batch(documents, batch_size=10):
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        pipeline.add_documents(batch)
        st.progress((i + batch_size) / len(documents))
```

## Extending Functionality

### Plugin System

```python
class PluginManager:
    def __init__(self):
        self.plugins = []

    def register(self, plugin):
        self.plugins.append(plugin)

    def process(self, data):
        for plugin in self.plugins:
            data = plugin.process(data)
        return data
```

### Custom Tools

```python
class WebSearchTool:
    def search(self, query):
        # Implement web search
        results = search_api.search(query)
        return results

# Register with pipeline
pipeline.register_tool("web_search", WebSearchTool())
```
