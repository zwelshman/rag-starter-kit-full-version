"""
Simplified RAG Starter Kit - Claude Only
Minimal, focused implementation using only Anthropic Claude
"""

import streamlit as st
import sys
import logging
import os
from dotenv import load_dotenv

from core.llm_providers import ClaudeProvider
from core.document_processor import DocumentProcessor
from core.retrieval_engine import RetrievalEngine

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("rag_simple")

# Page configuration
st.set_page_config(
    page_title="RAG Kit - Claude",
    page_icon="🚀",
    layout="wide",
)

def init_session_state():
    """Initialize session state"""
    if 'llm' not in st.session_state:
        try:
            st.session_state.llm = ClaudeProvider(
                model="claude-3-5-sonnet-20241022"
            )
            logger.info("Claude provider initialized")
        except ValueError as e:
            logger.error(f"Failed to initialize Claude: {e}")
            st.error(f"❌ Failed to initialize Claude: {e}")
            st.stop()
    
    if 'doc_processor' not in st.session_state:
        st.session_state.doc_processor = DocumentProcessor()
    
    if 'retrieval_engine' not in st.session_state:
        st.session_state.retrieval_engine = RetrievalEngine()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'documents_loaded' not in st.session_state:
        st.session_state.documents_loaded = False


def render_sidebar():
    """Render sidebar controls"""
    with st.sidebar:
        st.header("⚙️ Settings")
        
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Lower = more focused, Higher = more creative"
        )
        
        max_tokens = st.slider(
            "Max Tokens",
            min_value=256,
            max_value=4096,
            value=1024,
            step=256,
        )
        
        n_results = st.slider(
            "Retrieved Documents",
            min_value=1,
            max_value=10,
            value=3,
            help="Number of document chunks to retrieve"
        )
        
        st.divider()
        st.caption("**Model**: Claude 3.5 Sonnet")
        st.caption("**Vector DB**: ChromaDB")
        
        return temperature, max_tokens, n_results


def render_upload_tab():
    """Render document upload interface"""
    st.header("📤 Upload Documents")
    
    uploaded_files = st.file_uploader(
        "Upload PDF or DOCX files",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        help="Upload documents for RAG processing"
    )
    
    if uploaded_files:
        if st.button("Process Documents", type="primary", use_container_width=True):
            with st.spinner("Processing documents..."):  
                try:
                    for uploaded_file in uploaded_files:
                        # Save temporarily
                        temp_path = f"/tmp/{uploaded_file.name}"
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Process document
                        docs = st.session_state.doc_processor.process(temp_path)
                        
                        # Add to retrieval engine
                        for doc in docs:
                            st.session_state.retrieval_engine.add_document(doc)
                        
                        logger.info(f"Processed {len(docs)} chunks from {uploaded_file.name}")
                        st.success(f"✅ Processed {uploaded_file.name}")
                    
                    st.session_state.documents_loaded = True
                    st.rerun()
                    
                except Exception as e:
                    logger.error(f"Error processing documents: {e}")
                    st.error(f"❌ Error: {e}")
    
    if st.session_state.documents_loaded:
        st.success("✅ Documents loaded and ready for querying")


def render_chat_tab(temperature: float, max_tokens: int, n_results: int):
    """Render chat interface"""
    st.header("💬 Chat")
    
    if not st.session_state.documents_loaded:
        st.info("📁 Please upload documents first in the Upload tab")
        return
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    query = st.chat_input("Ask a question about your documents...")
    
    if query:
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": query})
        
        with st.chat_message("user"):
            st.write(query)
        
        with st.spinner("Claude is thinking..."):
            try:
                # Retrieve context
                context_docs = st.session_state.retrieval_engine.retrieve(
                    query, 
                    n_results=n_results
                )
                context = "\n\n".join([doc.page_content for doc in context_docs])
                
                # Generate response
                response = st.session_state.llm.generate_with_context(
                    query=query,
                    context=context,
                    system_prompt="You are a helpful assistant. Answer questions based on the provided context. If the context doesn't contain relevant information, say so.",
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                # Add assistant message
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                
                with st.chat_message("assistant"):
                    st.write(response)
                    
                    with st.expander("📄 View Context"):
                        st.text(context)
                
                logger.info(f"Query processed: {query[:50]}...")
                
            except Exception as e:
                logger.error(f"Error generating response: {e}")
                st.error(f"❌ Error: {e}")


def main():
    """Main application"""
    logger.info("=" * 50)
    logger.info("RAG STARTER KIT - CLAUDE ONLY (SIMPLIFIED)")
    logger.info("=" * 50)
    
    init_session_state()
    
    # Header
    st.title("🚀 RAG Kit - Claude Only")
    st.caption("Simplified RAG with Anthropic Claude 3.5 Sonnet")
    
    # Sidebar
    temperature, max_tokens, n_results = render_sidebar()
    
    # Tabs
    tab1, tab2 = st.tabs(["📤 Upload", "💬 Chat"])
    
    with tab1:
        render_upload_tab()
    
    with tab2:
        render_chat_tab(temperature, max_tokens, n_results)
    
    # Footer
    st.divider()
    st.caption("🔐 Your data is processed locally. No external API calls except to Claude.")


if __name__ == "__main__":
    main()