"""
Weaviate Vector Store
Cloud and self-hosted vector database for RAG applications.
"""

import os
import logging
from typing import List, Dict, Any, Optional
import hashlib
import uuid

from .base import BaseVectorStore

logger = logging.getLogger("rag_app.vectorstore.weaviate")


class WeaviateVectorStore(BaseVectorStore):
    """
    Weaviate vector store implementation.
    Supports both cloud and self-hosted deployments.
    """

    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        class_name: str = "Document",
        embedding_model: str = "all-MiniLM-L6-v2",
        **kwargs,
    ):
        """
        Initialize Weaviate vector store.

        Args:
            url: Weaviate cluster URL (or set WEAVIATE_URL env var)
            api_key: Weaviate API key (or set WEAVIATE_API_KEY env var)
            class_name: Weaviate class name for documents
            embedding_model: SentenceTransformer model for embeddings
        """
        try:
            import weaviate
            from weaviate.classes.init import Auth
        except ImportError:
            raise ImportError("Weaviate package not installed. Run: pip install weaviate-client")

        self.url = url or os.getenv("WEAVIATE_URL", "http://localhost:8080")
        self.api_key = api_key or os.getenv("WEAVIATE_API_KEY")
        self.class_name = class_name

        # Initialize Weaviate client
        if self.api_key:
            self.client = weaviate.connect_to_weaviate_cloud(
                cluster_url=self.url,
                auth_credentials=Auth.api_key(self.api_key),
            )
        else:
            self.client = weaviate.connect_to_local(
                host=self.url.replace("http://", "").replace("https://", "").split(":")[0],
                port=int(self.url.split(":")[-1]) if ":" in self.url.split("/")[-1] else 8080,
            )

        # Create collection if not exists
        self._ensure_collection()

        # Initialize embedding model
        try:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer(embedding_model)
            self.dimension = self.embedding_model.get_sentence_embedding_dimension()
        except ImportError:
            raise ImportError("sentence-transformers not installed. Run: pip install sentence-transformers")

        logger.info(f"Weaviate vector store initialized: url={self.url}, class={class_name}")

    def _ensure_collection(self):
        """Ensure the Weaviate collection exists."""
        try:
            from weaviate.classes.config import Configure, Property, DataType

            collections = self.client.collections.list_all()
            if self.class_name not in [c.name for c in collections.values()]:
                logger.info(f"Creating Weaviate collection: {self.class_name}")
                self.client.collections.create(
                    name=self.class_name,
                    vectorizer_config=Configure.Vectorizer.none(),
                    properties=[
                        Property(name="content", data_type=DataType.TEXT),
                        Property(name="source", data_type=DataType.TEXT),
                        Property(name="chunk_index", data_type=DataType.INT),
                        Property(name="doc_id", data_type=DataType.TEXT),
                    ],
                )
        except Exception as e:
            logger.warning(f"Collection check/creation warning: {e}")

    def _generate_uuid(self, content: str, source: str) -> str:
        """Generate a deterministic UUID for a document chunk."""
        hash_input = f"{source}:{content[:100]}"
        hash_bytes = hashlib.md5(hash_input.encode()).digest()
        return str(uuid.UUID(bytes=hash_bytes))

    def add_documents(self, chunks: List, batch_size: int = 100) -> int:
        """
        Add document chunks to Weaviate.

        Args:
            chunks: List of TextChunk objects
            batch_size: Number of documents to add per batch

        Returns:
            Number of documents added
        """
        if not chunks:
            return 0

        logger.info(f"Adding {len(chunks)} chunks to Weaviate")

        collection = self.client.collections.get(self.class_name)
        added_count = 0

        with collection.batch.dynamic() as batch:
            for chunk in chunks:
                content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                metadata = chunk.metadata if hasattr(chunk, 'metadata') else {}

                # Generate embedding
                embedding = self.embedding_model.encode(content).tolist()

                # Generate UUID
                doc_uuid = self._generate_uuid(content, metadata.get('source', 'unknown'))

                # Prepare properties
                properties = {
                    "content": content,
                    "source": metadata.get("source", "unknown"),
                    "chunk_index": metadata.get("chunk_index", 0),
                    "doc_id": chunk.id if hasattr(chunk, 'id') else doc_uuid,
                }

                batch.add_object(
                    properties=properties,
                    vector=embedding,
                    uuid=doc_uuid,
                )
                added_count += 1

        logger.info(f"Successfully added {added_count} chunks to Weaviate")
        return added_count

    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents in Weaviate.

        Args:
            query: Search query
            n_results: Number of results to return
            where: Filter conditions for metadata

        Returns:
            List of search results with content, metadata, and score
        """
        from weaviate.classes.query import MetadataQuery

        logger.info(f"Searching Weaviate: query='{query[:50]}...', n_results={n_results}")

        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()

        collection = self.client.collections.get(self.class_name)

        # Build query
        query_builder = collection.query.near_vector(
            near_vector=query_embedding,
            limit=n_results,
            return_metadata=MetadataQuery(distance=True),
        )

        # Apply filters if provided
        if where:
            from weaviate.classes.query import Filter
            filters = []
            for key, value in where.items():
                filters.append(Filter.by_property(key).equal(value))
            if filters:
                query_builder = query_builder.with_where(filters[0])

        results = query_builder.objects

        # Format results
        formatted_results = []
        for obj in results:
            score = 1 - obj.metadata.distance if obj.metadata.distance else 0.0
            formatted_results.append({
                "content": obj.properties.get("content", ""),
                "metadata": {
                    "source": obj.properties.get("source", "unknown"),
                    "chunk_index": obj.properties.get("chunk_index", 0),
                },
                "score": score,
                "id": str(obj.uuid),
            })

        logger.info(f"Weaviate search returned {len(formatted_results)} results")
        return formatted_results

    def clear(self) -> None:
        """Clear all documents from the Weaviate collection."""
        logger.info(f"Clearing all documents from Weaviate collection: {self.class_name}")
        self.client.collections.delete(self.class_name)
        self._ensure_collection()
        logger.info("Weaviate collection cleared and recreated")

    def count(self) -> int:
        """Get the number of documents in the Weaviate collection."""
        collection = self.client.collections.get(self.class_name)
        result = collection.aggregate.over_all(total_count=True)
        return result.total_count if result.total_count else 0

    def delete_by_source(self, source: str) -> int:
        """
        Delete all chunks from a specific source.

        Args:
            source: Source identifier to delete

        Returns:
            Number of objects deleted
        """
        from weaviate.classes.query import Filter

        logger.info(f"Deleting chunks from source: {source}")
        collection = self.client.collections.get(self.class_name)

        count_before = self.count()
        collection.data.delete_many(
            where=Filter.by_property("source").equal(source)
        )
        count_after = self.count()

        deleted = count_before - count_after
        logger.info(f"Deleted {deleted} objects from source: {source}")
        return deleted

    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        return {
            "total_objects": self.count(),
            "class_name": self.class_name,
            "url": self.url,
        }

    def close(self):
        """Close the Weaviate client connection."""
        self.client.close()

    def __del__(self):
        """Cleanup on deletion."""
        try:
            self.close()
        except Exception:
            pass
