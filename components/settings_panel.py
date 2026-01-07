"""
Settings Panel Component
Sidebar configuration panel for the RAG application.
"""

import streamlit as st
import logging
from typing import Tuple, Optional
from core.retrieval_engine import create_pipeline, SearchMode
from utils.auth import get_api_key

logger = logging.getLogger("rag_app.components.settings_panel")


# Available providers and models
PROVIDERS = {
    "Anthropic": {
        "key_name": "ANTHROPIC_API_KEY",
        "models": ["claude-sonnet-4-5", "claude-opus-4-5", "claude-haiku-4-5"],
        "default_model": "claude-sonnet-4-5",
    },
    "OpenAI": {
        "key_name": "OPENAI_API_KEY",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
        "default_model": "gpt-4o",
    },
    "Cohere": {
        "key_name": "COHERE_API_KEY",
        "models": ["command-r-plus", "command-r", "command"],
        "default_model": "command-r-plus",
    },
    "Hugging Face": {
        "key_name": "HF_API_KEY",
        "models": [
            "meta-llama/Meta-Llama-3.1-8B-Instruct",
            "meta-llama/Meta-Llama-3-8B-Instruct",
            "mistralai/Mistral-7B-Instruct-v0.3",
            "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "microsoft/Phi-3-mini-4k-instruct",
            "google/gemma-2-9b-it",
            "Qwen/Qwen2.5-7B-Instruct",
        ],
        "default_model": "meta-llama/Meta-Llama-3.1-8B-Instruct",
    },
    "Ollama (Local)": {
        "key_name": None,
        "models": ["llama3.2", "llama3.1", "mistral", "mixtral", "codellama"],
        "default_model": "llama3.2",
    },
}

# Default vector database
DEFAULT_VECTOR_DB = "ChromaDB"


def render_sidebar() -> Tuple[float, int]:
    """
    Render the sidebar with configuration options.

    Returns:
        Tuple of (temperature, max_tokens)
    """
    with st.sidebar:
        st.header("Configuration")

        # LLM Configuration
        st.subheader("LLM Settings")

        # Provider selection
        provider = st.selectbox(
            "Provider",
            options=list(PROVIDERS.keys()),
            index=0,
            help="Select the LLM provider",
        )

        provider_config = PROVIDERS[provider]

        # Model selection
        model = st.selectbox(
            "Model",
            options=provider_config["models"],
            index=0,
            help="Select the model to use",
        )

        # Store provider and model in session state for tracking
        # Normalize provider name for backend (e.g., "Hugging Face" -> "huggingface")
        provider_key = provider.lower().replace(" (local)", "").replace(" ", "")
        st.session_state.llm_provider = provider_key
        st.session_state.llm_model = model

        # Get API key from secrets or environment
        if provider_config["key_name"]:
            api_key = get_api_key(provider_config["key_name"])
            if api_key:
                st.success(f"{provider} API key loaded", icon="✅")
            else:
                st.warning(f"⚠️ Please add your {provider} API key to `.streamlit/secrets.toml`")
        else:
            api_key = None  # Ollama doesn't need API key
            st.info("Ollama runs locally - no API key needed")

        # Search Configuration
        st.subheader("Search Settings")

        search_mode = st.selectbox(
            "Search Mode",
            options=["Hybrid (Combined)", "Vector (Semantic)", "BM25 (Keyword)"],
            index=0,
            help="Select the search strategy",
        )

        # Hybrid search weighting (only shown for Hybrid mode)
        semantic_weight = 0.5  # Default
        if search_mode == "Hybrid (Combined)":
            semantic_weight = st.slider(
                "Semantic vs Keyword Balance",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.1,
                help="0.0 = Pure keyword (BM25), 1.0 = Pure semantic (Vector), 0.5 = Balanced",
            )
            # Show visual indicator
            bm25_pct = int((1 - semantic_weight) * 100)
            semantic_pct = int(semantic_weight * 100)
            st.caption(f"🔤 BM25: {bm25_pct}% | 🧠 Semantic: {semantic_pct}%")

        n_results = st.slider(
            "Number of Results",
            min_value=1,
            max_value=20,
            value=20,
            help="Number of document chunks to retrieve",
        )

        # Chunking Configuration
        st.subheader("Chunking Settings")

        chunk_size = st.slider(
            "Chunk Size",
            min_value=200,
            max_value=2000,
            value=300,
            step=100,
            help="Maximum size of each text chunk",
        )

        chunk_overlap = st.slider(
            "Chunk Overlap",
            min_value=0,
            max_value=500,
            value=50,
            step=50,
            help="Overlap between consecutive chunks",
        )

        # Generation Settings
        st.subheader("Generation Settings")

        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Controls randomness in generation",
        )

        max_tokens = st.slider(
            "Max Tokens",
            min_value=100,
            max_value=50000,
            value=4000,
            step=500,
            help="Maximum tokens in the response (up to 50,000 for detailed analysis)",
        )

        # Initialize/Update Pipeline button
        if st.button("Initialize Pipeline", type="primary", use_container_width=True):
            logger.info("Initialize Pipeline button clicked")
            if provider_config["key_name"] and not api_key:
                logger.warning("Pipeline initialization failed: No API key provided")
                st.error(f"Please enter your {provider} API key")
            else:
                try:
                    with st.spinner("Initializing pipeline..."):
                        logger.info(f"Starting pipeline initialization with {provider}/{model}...")
                        pipeline = create_pipeline(
                            api_key=api_key,
                            search_mode=search_mode,
                            chunk_size=chunk_size,
                            chunk_overlap=chunk_overlap,
                            n_results=n_results,
                            llm_provider=st.session_state.llm_provider,
                            llm_model=model,
                            semantic_weight=semantic_weight,
                        )
                        st.session_state.rag_pipeline = pipeline
                        st.session_state.llm_configured = True
                        st.session_state.temperature = temperature
                        st.session_state.max_tokens = max_tokens
                    st.success(f"Pipeline initialized with {model}!")
                    logger.info("Pipeline initialization complete - ready for documents")
                except Exception as e:
                    logger.error(f"Pipeline initialization failed: {e}")
                    st.error(f"Error initializing pipeline: {e}")

        # Show pipeline stats if initialized
        if st.session_state.get('rag_pipeline'):
            st.divider()
            st.subheader("Pipeline Status")
            stats = st.session_state.rag_pipeline.get_stats()
            st.metric("Documents Indexed", stats['vector_store_count'])
            st.caption(f"Provider: {st.session_state.get('llm_provider', 'anthropic')}")
            st.caption(f"Model: {st.session_state.get('llm_model', 'unknown')}")
            st.caption(f"Search Mode: {stats['search_mode']}")
            st.caption(f"Vector DB: {DEFAULT_VECTOR_DB}")
        else:
            st.divider()
            st.info(f"**Default Vector DB:** {DEFAULT_VECTOR_DB}")

        return temperature, max_tokens, n_results
