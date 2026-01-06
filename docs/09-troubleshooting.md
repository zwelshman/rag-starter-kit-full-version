# Troubleshooting Guide

Solutions to common issues with RAG Starter Kit Pro.

## Installation Issues

### "ModuleNotFoundError: No module named 'X'"

**Solution:**
```bash
pip install -r requirements.txt
```

If specific package fails:
```bash
pip install package_name --upgrade
```

### "Python version not supported"

**Requirement:** Python 3.9+

Check version:
```bash
python --version
```

### "sentence-transformers installation fails"

**Solution for M1/M2 Macs:**
```bash
pip install torch --extra-index-url https://download.pytorch.org/whl/cpu
pip install sentence-transformers
```

## API Key Issues

### "API key not found"

**Check 1:** Verify file exists
```bash
cat .streamlit/secrets.toml
```

**Check 2:** Verify format
```toml
# Correct format:
ANTHROPIC_API_KEY = "sk-ant-..."

# Wrong formats:
ANTHROPIC_API_KEY="sk-ant-..."  # Missing spaces
ANTHROPIC_API_KEY: "sk-ant-..."  # Wrong delimiter
```

**Check 3:** Environment variables
```bash
echo $ANTHROPIC_API_KEY
```

### "Invalid API key"

- Verify key hasn't expired
- Check for trailing spaces/newlines
- Ensure correct provider format
- Generate new key if needed

### "Rate limit exceeded"

**Immediate:** Wait 60 seconds and retry

**Long-term solutions:**
- Upgrade API plan
- Implement request throttling
- Add caching
- Use cheaper model for development

## Document Processing Issues

### "Failed to process document"

**Check file format:**
```python
SUPPORTED_FORMATS = ['.txt', '.pdf', '.docx', '.xlsx', '.csv', '.json']
```

**Check file size:**
- Maximum recommended: 10MB per file
- Split large files

**Check file encoding:**
```python
# Try different encodings
with open(file, 'r', encoding='utf-8') as f:
    content = f.read()
```

### "PDF extraction failed"

**Install system dependencies:**
```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils

# macOS
brew install poppler
```

**Alternative:** Use pypdf instead of pdfplumber

### "No text extracted from document"

- Check if PDF is image-based (needs OCR)
- Verify document isn't password protected
- Try alternative extraction method

## Vector Store Issues

### "ChromaDB connection error"

**Reset ChromaDB:**
```bash
rm -rf ./chroma_db
```

**Check persistence directory permissions**

### "Pinecone index not found"

**Verify index exists:**
```python
import pinecone
pinecone.list_indexes()
```

**Create index if missing:**
```python
pinecone.create_index("your-index", dimension=384)
```

### "Weaviate connection refused"

**Check if server is running:**
```bash
docker ps | grep weaviate
```

**Start Weaviate:**
```bash
docker-compose up -d weaviate
```

## Search Quality Issues

### "Irrelevant search results"

**Solutions:**
1. Adjust chunk size (try 300-500 characters)
2. Increase chunk overlap
3. Use hybrid search mode
4. Add query expansion
5. Implement reranking

### "Missing information in context"

**Solutions:**
1. Increase number of results (n_results)
2. Lower similarity threshold
3. Check document was properly indexed
4. Use keyword search for specific terms

### "Slow search performance"

**Solutions:**
1. Use smaller embedding model
2. Implement caching
3. Reduce number of results
4. Use approximate nearest neighbors

## LLM Response Issues

### "Hallucinations / incorrect information"

**Solutions:**
1. Add explicit grounding instructions
2. Use lower temperature (0.3-0.5)
3. Add "I don't know" handling
4. Implement citation requirements

### "Response doesn't use context"

**Check:**
1. Context is being passed to LLM
2. System prompt includes grounding instructions
3. Context isn't too long (truncation)

**Debug:**
```python
print(f"Context length: {len(context)}")
print(f"Context preview: {context[:500]}")
```

### "Response cut off / incomplete"

**Solution:** Increase max_tokens
```python
response = llm.generate(
    prompt,
    max_tokens=2000  # Increase from default
)
```

## Streamlit Issues

### "StreamlitAPIException"

**Common causes:**
- Using st.write() outside main thread
- Session state access before initialization
- Widget key conflicts

**Solution:**
```python
# Initialize session state first
if 'key' not in st.session_state:
    st.session_state.key = default_value
```

### "Memory error / App crashes"

**Solutions:**
1. Use `@st.cache_resource` for large objects
2. Process documents in batches
3. Clear session state periodically
4. Restart the app

### "App runs slowly"

**Solutions:**
1. Add caching for expensive operations
2. Use async processing where possible
3. Optimize database queries
4. Profile code to find bottlenecks

## Ollama Issues

### "Connection refused"

**Start Ollama:**
```bash
ollama serve
```

**Check port:**
```bash
curl http://localhost:11434/api/tags
```

### "Model not found"

**Pull model:**
```bash
ollama pull llama3.2
```

**List available models:**
```bash
ollama list
```

## Deployment Issues

### "Build failed on Streamlit Cloud"

**Check:**
1. requirements.txt syntax
2. Python version compatibility
3. Build logs for specific errors

### "Secrets not loading"

**Verify in Streamlit Cloud:**
1. Go to app settings
2. Check "Secrets" section
3. Verify TOML syntax
4. Restart app after changes

## Getting Help

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Collect Information

When reporting issues, include:
1. Python version
2. Package versions (`pip freeze`)
3. Error message/traceback
4. Steps to reproduce
5. Operating system

### Support Channels

- GitHub Issues: Bug reports and feature requests
- Email Support: support@example.com
- Documentation: Check docs/ folder
