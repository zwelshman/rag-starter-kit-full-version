# Extended Prompt Library

Advanced prompts for specialized RAG use cases.

## Table of Contents

1. [Multi-Turn Conversation](#multi-turn-conversation)
2. [Structured Output](#structured-output)
3. [Evaluation Prompts](#evaluation-prompts)
4. [Custom Domain Prompts](#custom-domain-prompts)
5. [Error Handling](#error-handling)
6. [Meta-Prompts](#meta-prompts)

---

## Multi-Turn Conversation

### Conversation Memory Prompt

```
You are a helpful assistant with access to document context. Maintain conversation continuity.

Previous conversation:
{conversation_history}

Current context from documents:
{context}

User's current question: {question}

Respond considering both the conversation history and new context. Reference previous points when relevant.
```

### Follow-up Question Handler

```
Based on the previous exchange:
User asked: {previous_question}
You answered: {previous_answer}

Now the user asks: {current_question}

Determine if this is:
1. A follow-up requiring the same context
2. A clarification of your previous answer
3. A new topic

Respond appropriately:
```

---

## Structured Output

### JSON Output Template

```
Extract information from the context and return as valid JSON.

Context:
{context}

Question: {question}

Required JSON format:
{
  "answer": "Your answer here",
  "confidence": "high|medium|low",
  "sources": ["source1", "source2"],
  "key_facts": ["fact1", "fact2", "fact3"]
}

Return only valid JSON, no additional text.
```

### Table Extraction

```
Extract data from the context and format as a markdown table.

Context:
{context}

Extract the following fields: {fields}

Format as:
| Field 1 | Field 2 | Field 3 |
|---------|---------|---------|
| value   | value   | value   |
```

### Bullet Point Extraction

```
Extract key information as a structured bulleted list.

Context:
{context}

Topic: {topic}

Format:
• Main Point 1
  - Supporting detail
  - Supporting detail
• Main Point 2
  - Supporting detail
```

---

## Evaluation Prompts

### Relevance Scorer

```
Rate the relevance of this context to the question.

Question: {question}

Context:
{context}

Rate from 1-5:
1 = Not relevant at all
2 = Slightly relevant
3 = Moderately relevant
4 = Very relevant
5 = Perfectly relevant

Score: [1-5]
Explanation: [Brief explanation]
```

### Completeness Checker

```
Evaluate if this answer completely addresses the question.

Question: {question}
Answer: {answer}
Available Context: {context}

Evaluation:
- Completeness (1-5):
- Missing Information:
- Suggested Additions:
```

### Factuality Verifier

```
Verify if the answer is supported by the context.

Context (Ground Truth):
{context}

Answer to Verify:
{answer}

For each claim in the answer:
1. Identify the claim
2. Find supporting evidence in context (or note if missing)
3. Rate: Supported / Partially Supported / Not Supported / Contradicted

Overall Factuality Score: [0-100]%
```

---

## Custom Domain Prompts

### Research Paper Analysis

```
Analyze this research paper section as an academic reviewer.

Paper Section:
{context}

Question: {question}

Provide:
1. Key findings
2. Methodology assessment
3. Limitations noted
4. Implications for the field
5. Suggested citations: [If any papers should be referenced]
```

### Financial Document Analysis

```
You are a financial analyst reviewing documents.

Document Content:
{context}

Question: {question}

Consider:
- Financial metrics and ratios
- Risk factors
- Regulatory compliance
- Market implications

Important: Flag any discrepancies or concerns.
```

### Code Documentation

```
You are a technical documentation specialist.

Code/Technical Content:
{context}

Question: {question}

Provide:
- Clear explanation
- Code examples if applicable
- Best practices
- Common pitfalls
- Related concepts
```

---

## Error Handling

### Insufficient Context Handler

```
{standard_prompt}

IMPORTANT: If the context doesn't contain sufficient information:
1. Clearly state what information is missing
2. Provide any partial answer that IS supported
3. Suggest what additional documents might help
4. DO NOT make up or assume information

Format for insufficient context:
"Based on the available context, [partial answer]. However, the context doesn't contain [missing info]. To fully answer, you might need [suggestions]."
```

### Contradiction Handler

```
{standard_prompt}

If you find contradictory information in the context:
1. Acknowledge the contradiction
2. Present both viewpoints
3. Identify which source appears more authoritative (if determinable)
4. Recommend verification

Format:
"The sources contain conflicting information:
- Source A states: [claim]
- Source B states: [claim]
[Analysis and recommendation]"
```

### Ambiguity Handler

```
{standard_prompt}

If the question is ambiguous:
1. Identify the ambiguity
2. Provide answers for the most likely interpretations
3. Ask for clarification if needed

Format:
"This question could be interpreted as:
1. [Interpretation A] → [Answer A]
2. [Interpretation B] → [Answer B]

Could you clarify which you meant?"
```

---

## Meta-Prompts

### Prompt Optimizer

```
You are a prompt engineering expert. Analyze and improve this prompt.

Original Prompt:
{original_prompt}

Goal: {goal}

Evaluate:
1. Clarity (1-10):
2. Specificity (1-10):
3. Potential issues:
4. Suggested improvements:

Improved Prompt:
[Your improved version]
```

### Query Reformulator

```
Reformulate this query to improve RAG retrieval results.

Original Query: {query}

Generate 3 alternative formulations:
1. More specific version:
2. Broader version:
3. Technical/formal version:

Also generate:
- Key terms to search: [term1, term2, term3]
- Questions to ask: [q1, q2]
```

### Context Quality Assessor

```
Assess the quality of retrieved context for answering a question.

Question: {question}

Retrieved Context:
{context}

Assessment:
1. Coverage Score (1-10): How well does context cover the question?
2. Relevance Score (1-10): How relevant is each chunk?
3. Redundancy (1-10): How much overlap between chunks?
4. Gaps Identified: What's missing?
5. Retrieval Suggestions: How to improve retrieval?
```

---

## Usage Tips

1. **Combine prompts**: Mix and match sections as needed
2. **Customize placeholders**: Replace generic `{context}` with domain-specific labels
3. **Add constraints**: Include word limits, format requirements
4. **Include examples**: Few-shot prompts improve output quality
5. **Iterate**: Test and refine based on actual outputs

## Template Variables Reference

| Variable | Description |
|----------|-------------|
| `{context}` | Retrieved document chunks |
| `{question}` | User's query |
| `{conversation_history}` | Previous Q&A pairs |
| `{format}` | Desired output format |
| `{constraints}` | Any limitations or requirements |
| `{examples}` | Few-shot examples |
