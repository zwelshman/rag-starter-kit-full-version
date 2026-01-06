"""
File Upload Component
Handles document upload and processing UI.
"""

import streamlit as st
import logging
from typing import Optional
from core.document_processor import DocumentProcessor

logger = logging.getLogger("rag_app.components.file_uploader")


def render_file_upload(document_processor: Optional[DocumentProcessor] = None):
    """
    Render the file upload section.

    Args:
        document_processor: DocumentProcessor instance from core
    """
    st.header("Document Upload")

    # Supported file types
    from core.document_processor import SUPPORTED_EXTENSIONS
    st.caption(f"Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}")

    uploaded_files = st.file_uploader(
        "Upload your documents",
        type=[ext.lstrip('.') for ext in SUPPORTED_EXTENSIONS],
        accept_multiple_files=True,
        help="Upload documents to add to the knowledge base",
    )

    if uploaded_files:
        logger.info(f"Files selected for upload: {[f.name for f in uploaded_files]}")
        if st.button("Process Documents", type="primary"):
            if not st.session_state.get('rag_pipeline'):
                logger.warning("Process Documents clicked but pipeline not initialized")
                st.error("Please initialize the pipeline first (see sidebar)")
                return

            with st.spinner("Processing documents..."):
                logger.info("=" * 60)
                logger.info("DOCUMENT PROCESSING STARTED")
                logger.info("=" * 60)

                # Prepare file bytes list
                file_bytes_list = [
                    (file.getvalue(), file.name)
                    for file in uploaded_files
                ]

                for filename in [f.name for f in uploaded_files]:
                    logger.info(f"Processing file: {filename}")

                try:
                    result = st.session_state.rag_pipeline.add_documents(
                        file_bytes_list=file_bytes_list
                    )

                    logger.info(f"Documents processed: {result['documents']}")
                    logger.info(f"Chunks created: {result['chunks']}")
                    logger.info(f"Vector store count: {result.get('vector_store_count', 'N/A')}")
                    logger.info(f"BM25 index count: {result.get('bm25_count', 'N/A')}")
                    logger.info("DOCUMENT PROCESSING COMPLETE")
                    logger.info("=" * 60)

                    st.success(
                        f"Processed {result['documents']} documents into "
                        f"{result['chunks']} chunks"
                    )
                    st.session_state.documents_loaded = True
                    st.session_state.document_count = st.session_state.get('document_count', 0) + result['documents']

                    # Track document uploads for analytics
                    from components.analytics import track_document_upload
                    for file in uploaded_files:
                        chunks_per_doc = result['chunks'] // max(result['documents'], 1)
                        track_document_upload(
                            filename=file.name,
                            chunks=chunks_per_doc,
                            file_size=len(file.getvalue())
                        )

                    # Store uploaded file names in session state for display
                    if 'uploaded_files' not in st.session_state:
                        st.session_state.uploaded_files = []
                    for file in uploaded_files:
                        if file.name not in st.session_state.uploaded_files:
                            st.session_state.uploaded_files.append(file.name)

                except Exception as e:
                    logger.error(f"Document processing failed: {e}")
                    st.error(f"Error processing documents: {e}")
