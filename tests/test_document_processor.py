"""
Tests for Document Processor
Tests for document loading and chunking.
"""

import pytest
import os
import tempfile
from io import BytesIO


class TestDocumentProcessor:
    """Tests for DocumentProcessor class."""

    def test_initialization(self):
        """Test DocumentProcessor initialization."""
        from core.document_processor import DocumentProcessor

        processor = DocumentProcessor(chunk_size=500, chunk_overlap=100)

        assert processor.chunk_size == 500
        assert processor.chunk_overlap == 100

    def test_load_text_file(self):
        """Test loading a text file."""
        from core.document_processor import DocumentProcessor

        processor = DocumentProcessor()

        # Create test text content
        test_content = b"This is a test document.\nIt has multiple lines.\nFor testing purposes."

        docs = processor.load_from_bytes(test_content, "test.txt")

        assert len(docs) > 0
        assert "test document" in docs[0].content

    def test_split_documents(self):
        """Test document splitting."""
        from core.document_processor import DocumentProcessor, Document

        processor = DocumentProcessor(chunk_size=50, chunk_overlap=10)

        # Create a document with enough content to split
        long_content = "This is a test. " * 20
        doc = Document(content=long_content, metadata={"source": "test.txt"})

        chunks = processor.split_documents([doc])

        assert len(chunks) > 1
        assert all(hasattr(c, 'content') for c in chunks)
        assert all(hasattr(c, 'metadata') for c in chunks)

    def test_load_json_file(self):
        """Test loading a JSON file."""
        from core.document_processor import DocumentProcessor
        import json

        processor = DocumentProcessor()

        test_json = {
            "title": "Test Document",
            "content": "This is the content",
            "metadata": {"author": "Test"}
        }

        json_bytes = json.dumps(test_json).encode()
        docs = processor.load_from_bytes(json_bytes, "test.json")

        assert len(docs) > 0

    def test_load_csv_file(self):
        """Test loading a CSV file."""
        from core.document_processor import DocumentProcessor

        processor = DocumentProcessor()

        csv_content = b"name,value\ntest1,100\ntest2,200"
        docs = processor.load_from_bytes(csv_content, "test.csv")

        assert len(docs) > 0

    def test_unsupported_extension(self):
        """Test handling of unsupported file extension."""
        from core.document_processor import DocumentProcessor

        processor = DocumentProcessor()

        # Should handle gracefully
        docs = processor.load_from_bytes(b"test content", "test.xyz")

        # Either returns empty or handles as text
        assert isinstance(docs, list)

    def test_chunk_metadata(self):
        """Test that chunks have proper metadata."""
        from core.document_processor import DocumentProcessor, Document

        processor = DocumentProcessor(chunk_size=50, chunk_overlap=10)

        doc = Document(
            content="This is test content. " * 10,
            metadata={"source": "test.txt", "author": "Test"}
        )

        chunks = processor.split_documents([doc])

        for chunk in chunks:
            assert "source" in chunk.metadata
            assert chunk.metadata["source"] == "test.txt"
            assert hasattr(chunk, 'chunk_index')

    def test_empty_document(self):
        """Test handling of empty document."""
        from core.document_processor import DocumentProcessor

        processor = DocumentProcessor()

        docs = processor.load_from_bytes(b"", "empty.txt")

        # Should handle gracefully
        assert isinstance(docs, list)

    def test_chunk_ids_are_unique(self):
        """Test that chunk IDs are unique."""
        from core.document_processor import DocumentProcessor, Document

        processor = DocumentProcessor(chunk_size=50, chunk_overlap=10)

        doc = Document(
            content="Test content for chunking. " * 20,
            metadata={"source": "test.txt"}
        )

        chunks = processor.split_documents([doc])

        ids = [c.id for c in chunks]
        assert len(ids) == len(set(ids)), "Chunk IDs should be unique"


class TestDocumentProcessorIntegration:
    """Integration tests with real files."""

    def test_process_real_text_file(self):
        """Test processing a real text file."""
        from core.document_processor import DocumentProcessor

        processor = DocumentProcessor()

        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test document.\n" * 100)
            temp_path = f.name

        try:
            with open(temp_path, 'rb') as f:
                docs = processor.load_from_bytes(f.read(), os.path.basename(temp_path))

            assert len(docs) > 0

            chunks = processor.split_documents(docs)
            assert len(chunks) > 0

        finally:
            os.unlink(temp_path)


class TestSupportedFormats:
    """Tests for supported file formats."""

    def test_supported_extensions_constant(self):
        """Test that supported extensions are defined."""
        from core.document_processor import SUPPORTED_EXTENSIONS

        assert '.txt' in SUPPORTED_EXTENSIONS
        assert '.pdf' in SUPPORTED_EXTENSIONS
        assert '.docx' in SUPPORTED_EXTENSIONS
        assert '.csv' in SUPPORTED_EXTENSIONS
        assert '.json' in SUPPORTED_EXTENSIONS
        assert '.xlsx' in SUPPORTED_EXTENSIONS
