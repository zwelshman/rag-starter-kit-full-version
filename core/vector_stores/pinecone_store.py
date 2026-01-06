"""
Pinecone Vector Store
Cloud-based vector database for production RAG applications.
"""

import os
import logging
from typing import List, Dict, Any, Optional
import hashlib

from .base import BaseVectorStore

logger = logging.getLogger("rag_app.vectorstore.pinecone")


class PineconeVectorStore(BaseVectorStore):
    """
    Pinecone vector store implementation.
    Production-ready cloud vector database.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        environment: Optional[str] = None,
        index_name: str = "rag-documents",
        embedding_model: str = "all-MiniLM-L6-v2",
        dimension: int = 384,
        metric: str = "cosine",
        **kwargs,
    ):
        """
        Initialize Pinecone vector store.

        Args:
            api_key: Pinecone API key (or set PINECONE_API_KEY env var)
            environment: Pinecone environment (e.g., 'us-east-1')
            index_name: Name of the Pinecone index
            embedding_model: SentenceTransformer model for embeddings
            dimension: Vector dimension (must match embedding model)
            metric: Distance metric ('cosine', 'euclidean', 'dotproduct')
        """
        try:
            from pinecone import Pinecone, ServerlessSpec
        except ImportError:
            raise ImportError("Pinecone package not installed. Run: pip install pinecone-client")

        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        if not self.api_key:
            raise ValueError("Pinecone API key not provided. Set PINECONE_API_KEY or pass api_key parameter.")

        self.index_name = index_name
        self.dimension = dimension
        self.metric = metric

        # Initialize Pinecone client
        self.pc = Pinecone(api_key=self.api_key)

        # Create or connect to index
        existing_indexes = [idx.name for idx in self.pc.list_indexes()]
        if index_name not in existing_indexes:
            logger.info(f"Creating Pinecone index: {index_name}")
            self.pc.create_index(
                name=index_name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(
                    cloud="aws",
                    region=environment or "us-east-1"
                )
            )

        self.index = self.pc.Index(index_name)

        # Initialize embedding model
        try:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer(embedding_model)
        except ImportError:
            raise ImportError("sentence-transformers not installed. Run: pip install sentence-transformers")

        logger.info(f"Pinecone vector store initialized: index={index_name}, dimension={dimension}")

    def _generate_id(self, content: str, source: str) -> str:
        """Generate a unique ID for a document chunk."""
        hash_input = f"{source}:{content[:100]}"
        return hashlib.md5(hash_input.encode()).hexdigest()

    def add_documents(self, chunks: List, batch_size: int = 100) -> int:
        """
        Add document chunks to Pinecone.

        Args:
            chunks: List of TextChunk objects
            batch_size: Number of documents to upsert per batch

        Returns:
            Number of documents added
        """
        if not chunks:
            return 0

        logger.info(f"Adding {len(chunks)} chunks to Pinecone")

        # Prepare vectors
        vectors_to_upsert = []
        for chunk in chunks:
            content = chunk.content if hasattr(chunk, 'content') else str(chunk)
            metadata = chunk.metadata if hasattr(chunk, 'metadata') else {}

            # Generate embedding
            embedding = self.embedding_model.encode(content).tolist()

            # Generate ID
            doc_id = chunk.id if hasattr(chunk, 'id') else self._generate_id(content, metadata.get('source', 'unknown'))

            # Prepare metadata (Pinecone requires flat structure)
            pinecone_metadata = {
                "content": content[:1000],  # Truncate for Pinecone metadata limits
                "source": metadata.get("source", "unknown"),
                "chunk_index": metadata.get("chunk_index", 0),
            }

            vectors_to_upsert.append({
                "id": doc_id,
                "values": embedding,
                "metadata": pinecone_metadata,
            })

        # Upsert in batches
        added_count = 0
        for i in range(0, len(vectors_to_upsert), batch_size):
            batch = vectors_to_upsert[i:i + batch_size]
            self.index.upsert(vectors=batch)
            added_count += len(batch)
            logger.debug(f"Upserted batch {i // batch_size + 1}: {len(batch)} vectors")

        logger.info(f"Successfully added {added_count} chunks to Pinecone")
        return added_count

    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents in Pinecone.

        Args:
            query: Search query
            n_results: Number of results to return
            where: Filter conditions for metadata

        Returns:
            List of search results with content, metadata, and score
        """
        logger.info(f"Searching Pinecone: query='{query[:50]}...', n_results={n_results}")

        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()

        # Build filter if provided
        filter_dict = None
        if where:
            filter_dict = where

        # Query Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=n_results,
            include_metadata=True,
            filter=filter_dict,
        )

        # Format results
        formatted_results = []
        for match in results.get("matches", []):
            metadata = match.get("metadata", {})
            formatted_results.append({
                "content": metadata.get("content", ""),
                "metadata": {
                    "source": metadata.get("source", "unknown"),
                    "chunk_index": metadata.get("chunk_index", 0),
                },
                "score": match.get("score", 0.0),
                "id": match.get("id", ""),
            })

        logger.info(f"Pinecone search returned {len(formatted_results)} results")
        return formatted_results

    def clear(self) -> None:
        """Clear all documents from the Pinecone index."""
        logger.info(f"Clearing all documents from Pinecone index: {self.index_name}")
        self.index.delete(delete_all=True)
        logger.info("Pinecone index cleared")

    def count(self) -> int:
        """Get the number of documents in the Pinecone index."""
        stats = self.index.describe_index_stats()
        return stats.get("total_vector_count", 0)

    def delete_by_source(self, source: str) -> int:
        """
        Delete all chunks from a specific source.

        Args:
            source: Source identifier to delete

        Returns:
            Number of vectors deleted (approximate)
        """
        logger.info(f"Deleting chunks from source: {source}")
        # Pinecone doesn't return count, so we estimate
        count_before = self.count()
        self.index.delete(filter={"source": {"$eq": source}})
        count_after = self.count()
        deleted = count_before - count_after
        logger.info(f"Deleted approximately {deleted} vectors from source: {source}")
        return deleted

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        stats = self.index.describe_index_stats()
        return {
            "total_vectors": stats.get("total_vector_count", 0),
            "dimension": stats.get("dimension", self.dimension),
            "index_fullness": stats.get("index_fullness", 0),
            "namespaces": stats.get("namespaces", {}),
        }
