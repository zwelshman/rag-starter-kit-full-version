# Advanced RAG Techniques

Take your RAG application to the next level with advanced techniques.

## Hybrid Search

### Combining Vector and Keyword Search

RAG Starter Kit Pro uses Reciprocal Rank Fusion (RRF) to combine results:

```python
def reciprocal_rank_fusion(vector_results, bm25_results, k=60):
    """Combine rankings using RRF."""
    scores = {}

    for rank, result in enumerate(vector_results):
        doc_id = result['id']
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)

    for rank, result in enumerate(bm25_results):
        doc_id = result['id']
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

### Tuning Hybrid Search

```python
# Adjust search weights
pipeline.configure_search(
    vector_weight=0.7,  # 70% semantic similarity
    bm25_weight=0.3,    # 30% keyword matching
    rrf_k=60            # RRF constant
)
```

## Query Expansion

### Synonym Expansion

```python
from nltk.corpus import wordnet

def expand_query(query):
    """Expand query with synonyms."""
    words = query.split()
    expanded = []

    for word in words:
        synonyms = set([word])
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                synonyms.add(lemma.name())
        expanded.append(" OR ".join(synonyms))

    return " ".join(expanded)
```

### LLM-Based Query Rewriting

```python
def rewrite_query(original_query):
    prompt = f"""
    Rewrite this query to improve search results.
    Generate 3 alternative phrasings.

    Original: {original_query}

    Alternatives:
    1.
    2.
    3.
    """
    return llm.generate(prompt)
```

## Reranking

### Cross-Encoder Reranking

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def rerank_results(query, results, top_k=5):
    """Rerank results using cross-encoder."""
    pairs = [(query, r['content']) for r in results]
    scores = reranker.predict(pairs)

    ranked = sorted(zip(results, scores), key=lambda x: x[1], reverse=True)
    return [r for r, s in ranked[:top_k]]
```

### LLM-Based Reranking

```python
def llm_rerank(query, results):
    prompt = f"""
    Rank these passages by relevance to the query.
    Return the indices in order of relevance.

    Query: {query}

    Passages:
    {enumerate_passages(results)}

    Ranking (most to least relevant):
    """
    ranking = llm.generate(prompt)
    return reorder_results(results, parse_ranking(ranking))
```

## Multi-Step Retrieval

### Iterative Retrieval

```python
def iterative_retrieve(query, max_iterations=3):
    """Retrieve in multiple steps, refining based on results."""
    all_results = []
    current_query = query

    for i in range(max_iterations):
        results = pipeline.search(current_query)
        all_results.extend(results)

        # Generate follow-up query based on gaps
        current_query = generate_followup(query, results)

        if not current_query:  # No more gaps
            break

    return deduplicate(all_results)
```

### Multi-Hop Reasoning

```python
def multi_hop_query(question):
    """Break complex questions into sub-questions."""

    # Step 1: Decompose question
    sub_questions = decompose_question(question)

    # Step 2: Answer each sub-question
    sub_answers = []
    for sq in sub_questions:
        results = pipeline.search(sq)
        answer = pipeline.generate(sq, results)
        sub_answers.append(answer)

    # Step 3: Synthesize final answer
    return synthesize_answers(question, sub_answers)
```

## Context Optimization

### Dynamic Context Selection

```python
def select_context(results, max_tokens=4000):
    """Dynamically select context based on relevance and diversity."""
    selected = []
    seen_topics = set()
    total_tokens = 0

    for result in results:
        # Skip if too similar to existing context
        if is_redundant(result, selected):
            continue

        tokens = count_tokens(result['content'])
        if total_tokens + tokens > max_tokens:
            break

        selected.append(result)
        total_tokens += tokens

    return selected
```

### Context Compression

```python
def compress_context(context, target_tokens=2000):
    """Compress context while preserving key information."""
    prompt = f"""
    Compress the following text to approximately {target_tokens} tokens.
    Preserve all key facts and information.

    Text:
    {context}

    Compressed:
    """
    return llm.generate(prompt)
```

## Evaluation and Monitoring

### RAG Metrics

```python
def evaluate_rag_response(question, context, response, ground_truth):
    """Evaluate RAG response quality."""
    metrics = {
        "faithfulness": check_faithfulness(response, context),
        "relevance": check_relevance(response, question),
        "answer_correctness": check_correctness(response, ground_truth),
        "context_precision": check_context_precision(context, ground_truth),
        "context_recall": check_context_recall(context, ground_truth),
    }
    return metrics
```

### A/B Testing Framework

```python
class RAGExperiment:
    def __init__(self, variant_a, variant_b):
        self.variants = {"A": variant_a, "B": variant_b}
        self.results = {"A": [], "B": []}

    def run_query(self, query, variant=None):
        if variant is None:
            variant = random.choice(["A", "B"])

        response = self.variants[variant].query(query)
        return response, variant

    def record_feedback(self, variant, score):
        self.results[variant].append(score)

    def get_winner(self):
        avg_a = sum(self.results["A"]) / len(self.results["A"])
        avg_b = sum(self.results["B"]) / len(self.results["B"])
        return "A" if avg_a > avg_b else "B"
```

## Advanced Architectures

### RAG with Knowledge Graph

```python
def knowledge_graph_rag(query):
    """Combine RAG with knowledge graph queries."""

    # Extract entities from query
    entities = extract_entities(query)

    # Query knowledge graph
    kg_context = query_knowledge_graph(entities)

    # Retrieve documents
    doc_context = pipeline.search(query)

    # Combine contexts
    combined_context = merge_contexts(kg_context, doc_context)

    return pipeline.generate(query, combined_context)
```

### Agentic RAG

```python
class RAGAgent:
    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.tools = {
            "search": self.search,
            "calculate": self.calculate,
            "summarize": self.summarize,
        }

    def query(self, question):
        # Plan actions
        plan = self.plan(question)

        # Execute plan
        context = []
        for action in plan:
            result = self.tools[action['tool']](action['input'])
            context.append(result)

        # Generate response
        return self.generate(question, context)
```

## Best Practices

1. **Start simple, add complexity as needed**
2. **Measure before optimizing**
3. **Use appropriate models for each component**
4. **Cache expensive operations**
5. **Monitor quality metrics continuously**
6. **Test with diverse queries**
7. **Document your configurations**
