"""
REST API Wrapper for RAG Starter Kit Pro
Exposes RAG functionality via FastAPI endpoints.
"""

import os
import sys
import logging
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add parent path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from core.retrieval_engine import create_pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG Starter Kit Pro API",
    description="REST API for RAG queries and document management",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global pipeline instance
pipeline = None


def get_pipeline():
    """Dependency to get or create RAG pipeline."""
    global pipeline
    if pipeline is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")
        pipeline = create_pipeline(api_key=api_key)
    return pipeline


# Request/Response Models
class QueryRequest(BaseModel):
    question: str
    temperature: float = 0.7
    max_tokens: int = 1000
    n_results: int = 5


class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    tokens_used: int


class SearchRequest(BaseModel):
    query: str
    n_results: int = 5
    mode: str = "hybrid"


class SearchResult(BaseModel):
    content: str
    source: str
    score: float


class StatsResponse(BaseModel):
    document_count: int
    chunk_count: int
    vector_store_type: str
    llm_provider: str


# API Endpoints
@app.get("/")
async def root():
    """API health check."""
    return {"status": "healthy", "version": "1.0.0"}


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest, rag=Depends(get_pipeline)):
    """Query the RAG system."""
    try:
        # Search for relevant documents
        results = rag.search(request.question, n_results=request.n_results)

        # Generate response
        response = ""
        for token in rag.query_stream(
            request.question,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        ):
            response += token

        return QueryResponse(
            answer=response,
            sources=[{"content": r["content"][:200], "source": r["metadata"].get("source", "unknown")} for r in results],
            tokens_used=len(response.split())  # Approximate
        )

    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search", response_model=List[SearchResult])
async def search(request: SearchRequest, rag=Depends(get_pipeline)):
    """Search documents without generating a response."""
    try:
        results = rag.search(
            request.query,
            n_results=request.n_results
        )

        return [
            SearchResult(
                content=r["content"],
                source=r["metadata"].get("source", "unknown"),
                score=r.get("score", 0.0)
            )
            for r in results
        ]

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    rag=Depends(get_pipeline)
):
    """Upload and index a document."""
    try:
        # Read file content
        content = await file.read()

        # Add to pipeline
        result = rag.add_documents(
            file_bytes_list=[(content, file.filename)]
        )

        return {
            "message": "Document uploaded successfully",
            "filename": file.filename,
            "chunks": result.get("chunks", 0)
        }

    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/documents")
async def clear_documents(rag=Depends(get_pipeline)):
    """Clear all documents from the system."""
    try:
        rag.clear()
        return {"message": "All documents cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", response_model=StatsResponse)
async def get_stats(rag=Depends(get_pipeline)):
    """Get pipeline statistics."""
    try:
        stats = rag.get_stats()
        return StatsResponse(
            document_count=stats.get("document_count", 0),
            chunk_count=stats.get("chunk_count", 0),
            vector_store_type=stats.get("vector_store", "unknown"),
            llm_provider=stats.get("llm_provider", "unknown")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "api_wrapper:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


"""
Usage:

1. Install dependencies:
   pip install fastapi uvicorn python-multipart

2. Set environment variables:
   export ANTHROPIC_API_KEY="sk-ant-..."

3. Run the API:
   python api_wrapper.py

4. Access API docs:
   http://localhost:8000/docs

5. Example requests:

   # Query
   curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{"question": "What is RAG?"}'

   # Upload document
   curl -X POST http://localhost:8000/documents/upload \
     -F "file=@document.pdf"

   # Search
   curl -X POST http://localhost:8000/search \
     -H "Content-Type: application/json" \
     -d '{"query": "machine learning"}'
"""
