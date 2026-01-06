# Cost Optimization Guide

Minimize API costs while maintaining quality in your RAG application.

## Understanding Costs

### LLM Provider Pricing (per 1M tokens)

| Provider | Model | Input | Output |
|----------|-------|-------|--------|
| Anthropic | Claude Sonnet 4.5 | $3.00 | $15.00 |
| Anthropic | Claude 3 Haiku | $0.25 | $1.25 |
| OpenAI | GPT-4o | $2.50 | $10.00 |
| OpenAI | GPT-4o-mini | $0.15 | $0.60 |
| Cohere | Command R+ | $3.00 | $15.00 |
| Cohere | Command R | $0.50 | $1.50 |
| Ollama | Any | Free | Free |

### Vector Store Pricing

| Provider | Free Tier | Paid |
|----------|-----------|------|
| ChromaDB | Unlimited (local) | N/A |
| Pinecone | 100K vectors | $70/month |
| Weaviate | 100K vectors | $25/month |

## Cost Reduction Strategies

### 1. Model Selection

**Use appropriate models for each task:**

```python
def select_model(task_complexity):
    if task_complexity == "simple":
        return "claude-3-haiku"  # Cheapest
    elif task_complexity == "moderate":
        return "gpt-4o-mini"     # Balanced
    else:
        return "claude-sonnet-4-5"  # Best quality
```

**Implement model routing:**

```python
def route_query(query):
    # Simple queries -> cheaper model
    if len(query) < 50 and is_simple_question(query):
        return LLMClient(provider="anthropic", model="claude-3-haiku")

    # Complex queries -> better model
    return LLMClient(provider="anthropic", model="claude-sonnet-4-5")
```

### 2. Token Optimization

**Reduce context length:**

```python
def optimize_context(chunks, max_tokens=2000):
    """Select most relevant chunks within token budget."""
    selected = []
    total_tokens = 0

    for chunk in chunks:
        chunk_tokens = count_tokens(chunk.content)
        if total_tokens + chunk_tokens <= max_tokens:
            selected.append(chunk)
            total_tokens += chunk_tokens
        else:
            break

    return selected
```

**Compress prompts:**

```python
# Instead of verbose prompts
verbose = "Please analyze the following context and provide a comprehensive answer to the user's question..."

# Use concise prompts
concise = "Answer based on context:"
```

### 3. Caching

**Response caching:**

```python
import hashlib
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_query(query_hash):
    return stored_responses.get(query_hash)

def query_with_cache(question, context):
    cache_key = hashlib.md5(f"{question}:{context}".encode()).hexdigest()

    cached = cached_query(cache_key)
    if cached:
        return cached

    response = llm.generate(question, context)
    store_response(cache_key, response)
    return response
```

**Embedding caching:**

```python
@st.cache_resource
def get_cached_embeddings(text_hash):
    return embedding_cache.get(text_hash)
```

### 4. Batch Processing

**Batch similar queries:**

```python
def batch_queries(queries, batch_size=5):
    """Process multiple queries in a single API call."""
    combined_prompt = "\n\n".join([
        f"Question {i+1}: {q}" for i, q in enumerate(queries)
    ])

    response = llm.generate(
        f"Answer each question:\n{combined_prompt}"
    )

    return parse_batch_response(response)
```

### 5. Local Processing

**Use Ollama for development:**

```python
import os

def get_llm_client():
    if os.getenv("ENVIRONMENT") == "development":
        return LLMClient(provider="ollama", model="llama3.2")
    return LLMClient(provider="anthropic", model="claude-sonnet-4-5")
```

**Local embeddings:**

```python
# Free, local embeddings
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(texts)
```

## Cost Monitoring

### Built-in Cost Tracker

```python
from components.cost_tracker import track_query_cost, get_cost_summary

# Track each query
track_query_cost(
    provider="anthropic",
    model="claude-sonnet-4-5",
    input_tokens=500,
    output_tokens=200
)

# Get summary
summary = get_cost_summary()
print(f"Today's cost: ${summary['today_cost']:.4f}")
```

### Budget Alerts

```python
# Set budget limits
st.session_state.cost_budget = {
    "daily_limit": 5.00,
    "monthly_limit": 100.00,
    "alerts_enabled": True,
}
```

### Cost Dashboard

Access the Cost Tracking tab in the app to view:
- Real-time cost tracking
- Provider breakdown
- Token usage statistics
- Budget utilization

## Optimization Checklist

- [ ] Use appropriate model for task complexity
- [ ] Implement response caching
- [ ] Optimize chunk sizes and counts
- [ ] Use local models for development
- [ ] Set up cost monitoring and alerts
- [ ] Review and compress system prompts
- [ ] Batch similar queries when possible
- [ ] Use cheaper models for simple tasks
- [ ] Cache frequently accessed embeddings
- [ ] Monitor and optimize token usage

## Cost Comparison Calculator

```python
def compare_costs(queries_per_day, avg_input_tokens, avg_output_tokens):
    """Compare monthly costs across providers."""
    monthly_queries = queries_per_day * 30

    costs = {}
    for provider, models in PRICING.items():
        for model, pricing in models.items():
            input_cost = (monthly_queries * avg_input_tokens / 1_000_000) * pricing["input"]
            output_cost = (monthly_queries * avg_output_tokens / 1_000_000) * pricing["output"]
            costs[f"{provider}/{model}"] = input_cost + output_cost

    return sorted(costs.items(), key=lambda x: x[1])
```

## Example: 50% Cost Reduction

**Before optimization:**
- Model: Claude Sonnet 4.5
- Context: 5000 tokens
- 1000 queries/day
- Monthly cost: ~$540

**After optimization:**
- Use Haiku for simple queries (60%)
- Reduce context to 2000 tokens
- Cache frequent queries (30% hit rate)
- Monthly cost: ~$270

**Savings: $270/month (50%)**
