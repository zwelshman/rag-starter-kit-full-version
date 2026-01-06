# Prompt Template Library

This library contains 55+ prompt templates organized by category for various RAG use cases.

## Directory Structure

```
prompts/
├── general/                    # General-purpose templates
│   ├── qa.txt                 # 10 Q&A templates
│   ├── summarization.txt      # 10 summarization templates
│   └── analysis.txt           # 10 analysis templates
├── domain_specific/           # Domain-specific templates
│   ├── legal.txt              # 5 legal templates
│   ├── medical.txt            # 5 medical templates
│   ├── technical.txt          # 5 technical templates
│   └── business.txt           # 5 business templates
├── advanced/                  # Advanced reasoning templates
│   ├── multi_hop.txt          # 5 multi-hop reasoning templates
│   ├── comparison.txt         # 5 comparison templates
│   └── extraction.txt         # 5 extraction templates
├── default_system.txt         # Default system prompt
├── detailed_analysis.txt      # Detailed analysis prompt
├── concise_summary.txt        # Concise summary prompt
└── README.md                  # This file
```

## Template Count Summary

| Category | Templates |
|----------|-----------|
| General Q&A | 10 |
| Summarization | 10 |
| Analysis | 10 |
| Legal | 5 |
| Medical | 5 |
| Technical | 5 |
| Business | 5 |
| Multi-hop Reasoning | 5 |
| Comparison | 5 |
| Extraction | 5 |
| Legacy Templates | 3 |
| **Total** | **58** |

## How to Use Templates

### Basic Usage

1. Select a template from the Prompt Library tab in the app
2. The template will be loaded with placeholders like `{context}` and `{question}`
3. These placeholders are automatically filled when you make a query

### Customizing Templates

You can modify templates by:
1. Editing the template files directly
2. Creating new template files in the appropriate directory
3. Using the template as a base and modifying in the UI

### Template Format

Each template file contains multiple templates separated by `---`:

```text
## Template 1: Name
Description and instructions...

{context}
{question}

---

## Template 2: Name
...
```

### Available Placeholders

- `{context}` - Retrieved document chunks
- `{question}` - User's query
- `{format}` - Requested output format

## Available Templates

### `default_system.txt`
General-purpose system prompt for balanced responses.
- **Use case**: Most queries
- **Style**: Balanced detail and brevity
- **Citations**: Yes

### `detailed_analysis.txt`
For in-depth analysis and comprehensive answers.
- **Use case**: Complex questions requiring thorough analysis
- **Style**: Detailed and structured
- **Citations**: Extensive with page numbers

### `concise_summary.txt`
For brief, to-the-point answers.
- **Use case**: Quick lookups, simple questions
- **Style**: Very concise (under 3 sentences)
- **Citations**: Brief

## Creating Custom Prompts

1. Create a new `.txt` file in the appropriate directory
2. Write your system prompt instructions
3. Reference it in your code:

```python
with open('prompts/your_prompt.txt', 'r') as f:
    custom_prompt = f.read()

pipeline.system_prompt = custom_prompt
```

## Best Practices

1. **Be specific**: Clearly define the assistant's role
2. **Set boundaries**: Specify what to do when information is missing
3. **Citation format**: Define how sources should be cited
4. **Response style**: Specify length, tone, and structure
5. **Edge cases**: Handle ambiguous or insufficient context

## Examples by Domain

### Legal/Compliance
- Request exact citations with section numbers
- Emphasize accuracy over interpretation
- Require explicit statements about missing information

### Technical Documentation
- Focus on step-by-step instructions
- Include code examples when relevant
- Cite specific documentation sections

### Research/Academic
- Request comprehensive analysis
- Require multiple source citations
- Highlight confidence levels in conclusions

### Customer Support
- Friendly, helpful tone
- Actionable answers
- Escalation paths for complex issues

## Contributing New Templates

To add a new template:

1. Identify the appropriate category (general, domain_specific, or advanced)
2. Add your template following the existing format
3. Include clear instructions and examples
4. Update this README with the new template count
