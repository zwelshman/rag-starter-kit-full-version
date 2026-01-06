# Prompt Engineering Guide

Master the art of prompt engineering for optimal RAG performance.

## Fundamentals

### The RAG Prompt Structure

```
[System Prompt]
You are an expert assistant that answers questions based on provided context.

[Context]
{retrieved_documents}

[User Query]
{user_question}

[Response Format]
Answer the question based on the context. Cite your sources.
```

## System Prompt Best Practices

### 1. Define the Role

```
You are a [ROLE] specializing in [DOMAIN].
Your task is to [PRIMARY_OBJECTIVE].
```

Example:
```
You are a legal assistant specializing in contract law.
Your task is to answer questions about contract provisions accurately.
```

### 2. Set Constraints

```
Guidelines:
- Only use information from the provided context
- If information is not available, say "I don't have enough information"
- Cite sources using [Source: X] format
- Keep responses under 300 words unless asked for detail
```

### 3. Define Output Format

```
Response Format:
1. Direct answer (1-2 sentences)
2. Supporting details (bullet points)
3. Source citations
4. Confidence level (High/Medium/Low)
```

## Template Categories

### Q&A Templates

**Basic Q&A:**
```
Answer the following question based on the context provided.
Be concise and accurate.

Context:
{context}

Question: {question}
```

**Expert Analysis:**
```
As an expert in the field, analyze the following question.
Provide a detailed, nuanced answer with supporting evidence.

Context:
{context}

Question: {question}

Analysis:
```

### Summarization Templates

**Executive Summary:**
```
Create an executive summary of the following content.
Focus on key decisions, action items, and critical information.
Keep it under 200 words.

Content:
{context}

Summary:
```

**Bullet Points:**
```
Extract the key points from the following text.
Present as a bulleted list with no more than 7 points.

Text:
{context}

Key Points:
```

### Comparative Analysis

```
Compare and contrast the following items based on the context.
Create a structured comparison highlighting similarities and differences.

Context:
{context}

Items to Compare: {items}

Comparison:
| Aspect | Item A | Item B |
|--------|--------|--------|
```

## Advanced Techniques

### Chain-of-Thought Prompting

```
Think through this step by step:

Context:
{context}

Question: {question}

Step 1: Identify relevant information in the context
Step 2: Analyze how it relates to the question
Step 3: Formulate a logical answer
Step 4: Verify against the context

Answer:
```

### Few-Shot Prompting

```
Here are examples of how to answer questions:

Example 1:
Q: What is the return policy?
A: According to the terms (Section 4.2), returns are accepted within 30 days of purchase with original packaging. [Source: Terms.pdf]

Example 2:
Q: What are the payment options?
A: The document lists three payment options: credit card, bank transfer, and PayPal (Section 3.1). [Source: Payment.pdf]

Now answer this question:
Context: {context}
Question: {question}
```

### Self-Consistency

```
Answer the question three different ways, then provide the most consistent answer.

Context:
{context}

Question: {question}

Approach 1:
Approach 2:
Approach 3:

Final Answer (most consistent):
```

## Domain-Specific Prompts

### Legal

```
You are a legal assistant. When answering:
- Use precise legal terminology
- Cite specific sections/clauses
- Note any ambiguities or exceptions
- Distinguish between facts and interpretation
- Include relevant jurisdiction if applicable
```

### Technical

```
You are a technical documentation expert. When answering:
- Provide step-by-step instructions when applicable
- Include code examples in markdown format
- Note system requirements or dependencies
- Highlight warnings or common pitfalls
- Reference specific documentation sections
```

### Medical (Disclaimer Required)

```
You are a medical information assistant. When answering:
- Provide factual information from the context only
- Never provide diagnosis or treatment recommendations
- Always include disclaimer about consulting healthcare professionals
- Use clear, accessible language
- Cite medical literature or guidelines when available

DISCLAIMER: This information is for educational purposes only and should not replace professional medical advice.
```

## Handling Edge Cases

### Insufficient Context

```
If the context doesn't contain enough information to answer:
- Explicitly state what information is missing
- Suggest what additional documents might help
- Provide a partial answer if some information is available
- Never make up information
```

### Contradictory Sources

```
If sources contain contradictory information:
- Acknowledge the contradiction
- Present both viewpoints
- Note which source appears more authoritative/recent
- Let the user know they should verify
```

### Off-Topic Questions

```
If the question is not related to the provided context:
- Politely redirect to the available information
- Explain what topics can be addressed
- Suggest rephrasing the question
```

## Evaluation and Iteration

### Quality Metrics

1. **Relevance**: Does the answer address the question?
2. **Accuracy**: Is the information correct?
3. **Completeness**: Are all aspects covered?
4. **Conciseness**: Is it appropriately brief?
5. **Citations**: Are sources properly cited?

### A/B Testing Prompts

```python
def test_prompt_variants(question, context, variants):
    results = []
    for prompt in variants:
        response = llm.generate(
            prompt.format(context=context, question=question)
        )
        results.append({
            "prompt": prompt,
            "response": response,
            "score": evaluate_response(response)
        })
    return sorted(results, key=lambda x: x["score"], reverse=True)
```

### Continuous Improvement

1. Log user feedback on responses
2. Identify patterns in poor responses
3. Update prompts based on failure modes
4. Test new prompts against benchmarks
5. Deploy improvements incrementally
