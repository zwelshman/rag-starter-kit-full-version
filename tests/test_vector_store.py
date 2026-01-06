"""
Tests for Vector Store implementations
Tests for ChromaDB, Pinecone, and Weaviate stores.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass


@dataclass
class MockTextChunk:
    """Mock TextChunk for testing."""
    content: str
    metadata: dict
    chunk_index: int = 0
    id: str = "test-id"


class TestChromaVectorStore:
    """Tests for ChromaDB vector store."""

    def test_initialization(self):
        """Test ChromaDB store initialization."""
        from core.vector_stores import ChromaVectorStore

        store = ChromaVectorStore(
            collection_name="test_collection",
            persist_directory=None  # In-memory for tests
        )

        assert store is not None

    def test_add_and_search(self):
        """Test adding documents and searching."""
        from core.vector_stores import ChromaVectorStore

        store = ChromaVectorStore(
            collection_name="test_add_search",
            persist_directory=None
        )

        # Create test chunks
        chunks = [
            MockTextChunk(
                content="Python is a programming language",
                metadata={"source": "test.txt"},
                id="chunk-1"
            ),
            MockTextChunk(
                content="JavaScript is used for web development",
                metadata={"source": "test.txt"},
                id="chunk-2"
            ),
        ]

        # Add documents
        count = store.add_documents(chunks)
        assert count == 2

        # Search
        results = store.search("Python programming", n_results=2)
        assert len(results) > 0
        assert "Python" in results[0]["content"]

    def test_count(self):
        """Test document counting."""
        from core.vector_stores import ChromaVectorStore

        store = ChromaVectorStore(
            collection_name="test_count",
            persist_directory=None
        )

        # Initially empty
        assert store.count() == 0

        # Add a document
        chunks = [
            MockTextChunk(
                content="Test content",
                metadata={"source": "test.txt"},
                id="chunk-1"
            )
        ]
        store.add_documents(chunks)

        assert store.count() == 1

    def test_clear(self):
        """Test clearing documents."""
        from core.vector_stores import ChromaVectorStore

        store = ChromaVectorStore(
            collection_name="test_clear",
            persist_directory=None
        )

        # Add documents
        chunks = [
            MockTextChunk(
                content="Test content",
                metadata={"source": "test.txt"},
                id="chunk-1"
            )
        ]
        store.add_documents(chunks)
        assert store.count() > 0

        # Clear
        store.clear()
        assert store.count() == 0


class TestPineconeVectorStore:
    """Tests for Pinecone vector store (mocked)."""

    @patch('core.vector_stores.pinecone_store.Pinecone')
    @patch('core.vector_stores.pinecone_store.SentenceTransformer')
    def test_initialization(self, mock_st, mock_pinecone):
        """Test Pinecone store initialization."""
        from core.vector_stores import PineconeVectorStore

        # Setup mocks
        mock_pinecone.return_value.list_indexes.return_value = []
        mock_pinecone.return_value.Index.return_value = MagicMock()

        store = PineconeVectorStore(
            api_key="test-key",
            index_name="test-index"
        )

        assert store is not None

    @patch('core.vector_stores.pinecone_store.Pinecone')
    @patch('core.vector_stores.pinecone_store.SentenceTransformer')
    def test_add_documents(self, mock_st, mock_pinecone):
        """Test adding documents to Pinecone."""
        from core.vector_stores import PineconeVectorStore

        # Setup mocks
        mock_index = MagicMock()
        mock_pinecone.return_value.list_indexes.return_value = []
        mock_pinecone.return_value.Index.return_value = mock_index
        mock_st.return_value.encode.return_value = [0.1] * 384

        store = PineconeVectorStore(
            api_key="test-key",
            index_name="test-index"
        )

        chunks = [
            MockTextChunk(
                content="Test content",
                metadata={"source": "test.txt"},
                id="chunk-1"
            )
        ]

        count = store.add_documents(chunks)
        assert count == 1
        mock_index.upsert.assert_called()


class TestWeaviateVectorStore:
    """Tests for Weaviate vector store (mocked)."""

    @patch('core.vector_stores.weaviate_store.weaviate')
    @patch('core.vector_stores.weaviate_store.SentenceTransformer')
    def test_initialization(self, mock_st, mock_weaviate):
        """Test Weaviate store initialization."""
        from core.vector_stores import WeaviateVectorStore

        # Setup mocks
        mock_client = MagicMock()
        mock_weaviate.connect_to_local.return_value = mock_client
        mock_client.collections.list_all.return_value = {}

        store = WeaviateVectorStore(
            url="http://localhost:8080",
            class_name="TestDocument"
        )

        assert store is not None


class TestVectorStoreBase:
    """Tests for base vector store interface."""

    def test_base_class_is_abstract(self):
        """Test that BaseVectorStore is abstract."""
        from core.vector_stores import BaseVectorStore

        with pytest.raises(TypeError):
            BaseVectorStore()

    def test_required_methods(self):
        """Test that required methods are defined."""
        from core.vector_stores import BaseVectorStore
        import inspect

        methods = inspect.getmembers(BaseVectorStore, predicate=inspect.isfunction)
        method_names = [m[0] for m in methods]

        assert "add_documents" in method_names or hasattr(BaseVectorStore, "add_documents")
        assert "search" in method_names or hasattr(BaseVectorStore, "search")
        assert "clear" in method_names or hasattr(BaseVectorStore, "clear")
        assert "count" in method_names or hasattr(BaseVectorStore, "count")


class TestVectorStoreIntegration:
    """Integration tests (require services)."""

    @pytest.mark.skipif(
        not os.environ.get("PINECONE_API_KEY"),
        reason="PINECONE_API_KEY not set"
    )
    def test_pinecone_real_connection(self):
        """Test real Pinecone connection (requires API key)."""
        # Integration test placeholder
        pass

    @pytest.mark.skipif(
        not os.environ.get("WEAVIATE_URL"),
        reason="WEAVIATE_URL not set"
    )
    def test_weaviate_real_connection(self):
        """Test real Weaviate connection (requires server)."""
        # Integration test placeholder
        pass
