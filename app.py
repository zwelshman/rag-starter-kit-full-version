"""
Streamlit RAG Kit - Full Version
A modular, production-ready RAG application with multiple LLM providers and vector stores.

Features:
- ✅ Unlimited documents and queries
- ✅ 4 LLM providers (OpenAI, Claude, Cohere, Ollama)
- ✅ 3 vector DBs (Pinecone, ChromaDB, Weaviate)
- ✅ 50+ prompt templates
- ✅ Authentication & user management
- ✅ Cost tracking & analytics
- ✅ Production deployment ready
"""

import streamlit as st
import sys
import logging

# Import components
from components import (
    render_file_upload,
    render_chat_interface,
    render_sidebar,
)
from components.auth import render_auth, check_authentication, get_current_user
from components.analytics import render_analytics_dashboard
from components.cost_tracker import render_cost_dashboard, track_query_cost

# Import utilities
from utils.session_state import init_session_state
from utils.session_manager import SessionManager


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("rag_app")
logger.setLevel(logging.INFO)


# Page configuration
st.set_page_config(
    page_title="RAG Starter Kit Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)


def render_welcome_section():
    """Render welcome section with feature highlights."""
    with st.expander("🚀 Welcome to RAG Starter Kit Pro", expanded=False):
        st.markdown("""
### Full Version Features

| Feature | Status |
|---------|--------|
| Unlimited Documents | ✅ |
| Unlimited Queries | ✅ |
| Multiple LLM Providers | ✅ OpenAI, Claude, Cohere, Ollama |
| Multiple Vector Stores | ✅ ChromaDB, Pinecone, Weaviate |
| 50+ Prompt Templates | ✅ |
| Authentication & User Management | ✅ |
| Cost Tracking & Analytics | ✅ |
| Production Deployment | ✅ |

---

#### Quick Start Guide

1. **Configure API Keys** - Set up your provider keys in the sidebar
2. **Choose Your Stack** - Select LLM provider and vector store
3. **Upload Documents** - No limits on document count
4. **Start Querying** - Unlimited queries with full analytics

---

#### Keyboard Shortcuts

- `Ctrl + Enter` - Submit query
- `Ctrl + K` - Clear chat
- `Ctrl + U` - Upload documents
        """)


def render_clear_data():
    """Render data management section."""
    st.header("🗑️ Manage Data")

    # Show currently loaded files
    uploaded_files = st.session_state.get('uploaded_files', [])
    if uploaded_files:
        st.subheader("📁 Loaded Documents")
        for i, filename in enumerate(uploaded_files, 1):
            st.markdown(f"  {i}. `{filename}`")
        st.caption(f"Total: {len(uploaded_files)} document(s) in knowledge base")
        st.divider()
    else:
        st.info("No documents loaded yet. Upload documents in the Upload tab.")
        st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Clear Chat History", use_container_width=True):
            logger.info("Clearing chat history")
            st.session_state.chat_history = []
            st.success("Chat history cleared")
            st.rerun()

    with col2:
        if st.button("Clear All Documents", type="secondary", use_container_width=True):
            if st.session_state.get('rag_pipeline'):
                logger.info("Clearing all documents from pipeline")
                st.session_state.rag_pipeline.clear()
                st.session_state.documents_loaded = False
                st.session_state.document_count = 0
                st.session_state.uploaded_files = []
                logger.info("All documents cleared successfully")
                st.success("All documents cleared")
                st.rerun()

    with col3:
        if st.button("Export Chat History", type="primary", use_container_width=True):
            if st.session_state.get('chat_history'):
                import json
                chat_export = json.dumps(st.session_state.chat_history, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=chat_export,
                    file_name="chat_history.json",
                    mime="application/json"
                )
            else:
                st.warning("No chat history to export")


def render_prompt_library():
    """Render prompt template library."""
    st.header("📝 Prompt Template Library")

    # Show active template status
    active_template = st.session_state.get('active_template')
    if active_template:
        st.success(f"✅ Active Template: **{active_template['name']}**")
        st.caption("Go to the Chat tab to ask questions using this template.")
        col_clear, col_proceed = st.columns(2)
        with col_clear:
            if st.button("Clear Active Template", type="secondary", use_container_width=True):
                st.session_state.active_template = None
                st.rerun()
        with col_proceed:
            if st.button("➡️ Proceed to Chat", type="primary", use_container_width=True):
                st.session_state.active_tab = "chat"
                st.info("👆 Click the **💬 Chat** tab above to start asking questions!")
        st.divider()

    st.markdown("""
    **How Templates Work:**
    1. Select a template type and response style below
    2. Click "Use This Template" to activate it
    3. Click "Proceed to Chat" or go to the **Chat** tab
    4. Type your question - the template formats it with retrieved context
    5. View exactly what was sent in the "View Full Prompt Sent to LLM" expander
    """)
    st.divider()

    # Domain-specific template bases - each with unique, specialized prompts
    template_types = {
        "Q&A": {
            "description": "General Question and Answer",
            "system_context": "You are a knowledgeable assistant that provides accurate, helpful answers based on the provided documents.",
            "instruction": "Answer the user's question using only information from the context below. If the context doesn't contain relevant information, clearly state that."
        },
        "Summarization": {
            "description": "Document Summarization",
            "system_context": "You are an expert document summarizer skilled at extracting and condensing key information while preserving essential meaning and nuance.",
            "instruction": "Create a summary that captures the main points, key findings, and important details from the context. Organize the summary logically and highlight the most significant information relevant to the question."
        },
        "Analysis": {
            "description": "Critical Document Analysis",
            "system_context": "You are a critical analyst skilled at examining documents to identify patterns, relationships, implications, and insights that may not be immediately obvious.",
            "instruction": "Analyze the context critically. Identify key themes, patterns, and relationships. Evaluate the strength of arguments or evidence presented. Highlight implications and provide analytical insights related to the question."
        },
        "Legal": {
            "description": "Legal Document Review",
            "system_context": "You are a legal research assistant specializing in document review. You identify relevant legal provisions, obligations, rights, and potential issues with precision. DISCLAIMER: This is for informational purposes only and does not constitute legal advice.",
            "instruction": "Review the legal context and address the question by: (1) identifying relevant clauses, provisions, or legal principles, (2) explaining obligations, rights, or restrictions that apply, (3) noting any ambiguities, potential issues, or areas requiring attention, (4) citing specific sections or paragraphs where applicable."
        },
        "Medical": {
            "description": "Medical Literature Analysis",
            "system_context": "You are a medical research assistant with expertise in analyzing clinical literature, studies, and healthcare documentation. You use precise medical terminology and evidence-based reasoning. DISCLAIMER: This is for informational purposes only and does not constitute medical advice. Always consult healthcare professionals for medical decisions.",
            "instruction": "Review the medical context and address the question by: (1) identifying relevant clinical findings, diagnoses, or treatments mentioned, (2) referencing applicable studies, guidelines, or protocols, (3) explaining mechanisms, outcomes, or implications using appropriate medical terminology, (4) noting any limitations, contraindications, or areas requiring professional consultation."
        },
        "Technical": {
            "description": "Technical Documentation Expert",
            "system_context": "You are a technical documentation specialist who excels at explaining complex technical concepts clearly and accurately. You reference specifications precisely and provide practical, implementable guidance.",
            "instruction": "Address the technical question using the documentation provided by: (1) explaining relevant concepts, architectures, or processes clearly, (2) citing specific specifications, parameters, or requirements, (3) providing code examples, configurations, or step-by-step procedures where applicable, (4) noting dependencies, prerequisites, or potential issues to be aware of."
        },
        "Business": {
            "description": "Business Intelligence & Strategy",
            "system_context": "You are a business analyst skilled at extracting actionable insights from business documents. You identify key metrics, market trends, competitive factors, and strategic implications.",
            "instruction": "Analyze the business context and address the question by: (1) identifying relevant KPIs, metrics, or financial data, (2) highlighting market trends, competitive dynamics, or industry factors, (3) assessing opportunities, risks, or strategic considerations, (4) providing actionable recommendations or insights where the data supports them."
        },
    }

    # Response style modifiers - clearly differentiated output formats
    response_styles = {
        "Basic": {
            "description": "Clear, straightforward answers (1-2 paragraphs)",
            "modifier": "\n\nProvide a clear, straightforward answer in 1-2 paragraphs. Focus on directly answering the question without excessive detail.",
            "format_hint": "📝 Output: 1-2 focused paragraphs"
        },
        "Concise": {
            "description": "Brief bullet points, minimal text",
            "modifier": "\n\nBe extremely concise. Use bullet points where possible. Aim for the shortest answer that fully addresses the question. If information is not available in the context, simply state: \"Information not found in the provided documents.\"",
            "format_hint": "📋 Output: Bullet points, <100 words"
        },
        "Detailed": {
            "description": "Comprehensive analysis with structure",
            "modifier": "\n\nProvide a comprehensive, well-structured response. Include:\n- An overview/summary of your findings\n- Detailed explanations with supporting evidence from the context\n- Specific examples, quotes, or data points where relevant\n- Any caveats, limitations, or additional considerations\n\nUse headers or sections to organize longer responses.",
            "format_hint": "📊 Output: Structured, multi-section response"
        },
    }

    col1, col2 = st.columns(2)

    with col1:
        selected_type = st.selectbox(
            "Template Type",
            options=list(template_types.keys()),
            format_func=lambda x: f"{x} - {template_types[x]['description']}",
            help="Choose the domain or task type"
        )

    with col2:
        selected_style = st.selectbox(
            "Response Style",
            options=list(response_styles.keys()),
            help="Choose how detailed you want the response"
        )

    # Get selected configurations
    type_config = template_types[selected_type]
    style_config = response_styles[selected_style]

    # Build the complete template
    template_content = f"""{type_config['system_context']}

{type_config['instruction']}{style_config['modifier']}

Context:
{{context}}

Question: {{question}}

Answer:"""

    # Show domain and style descriptions with visual differentiation
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.info(f"**{selected_type}**: {type_config['description']}")
    with col_info2:
        st.success(f"**{selected_style}**: {style_config['format_hint']}")

    # Show template preview
    st.markdown("#### Template Preview")
    st.code(template_content, language="text")

    st.caption("**{context}** = Retrieved document chunks | **{question}** = Your question")

    # Buttons
    if st.button("Use This Template", type="primary", use_container_width=True):
        st.session_state.active_template = {
            'name': f"{selected_type} ({selected_style})",
            'content': template_content
        }
        st.success(f"✅ Template '{selected_type} ({selected_style})' is now active!")
        st.rerun()

    # Show proceed button only after template is selected
    if st.session_state.get('active_template'):
        if st.button("➡️ Proceed to Chat", type="secondary", use_container_width=True):
            st.info("👆 Click the **💬 Chat** tab above to start asking questions!")


def load_prompt_template(category: str, template: str) -> str:
    """Load a prompt template from file."""
    import os

    template_mapping = {
        "q&a": "qa.txt",
        "summarization": "summarization.txt",
        "analysis": "analysis.txt",
        "legal": "legal.txt",
        "medical": "medical.txt",
        "technical": "technical.txt",
        "business": "business.txt",
        "multi-hop reasoning": "multi_hop.txt",
        "comparison": "comparison.txt",
        "extraction": "extraction.txt",
    }

    category_mapping = {
        "general": "general",
        "domain-specific": "domain_specific",
        "advanced": "advanced",
    }

    filename = template_mapping.get(template, "qa.txt")
    cat_folder = category_mapping.get(category, "general")
    filepath = os.path.join("prompts", cat_folder, filename)

    try:
        with open(filepath, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f"# {template.title()} Template\n\nTemplate file not found. Create it at: {filepath}"


def main():
    """Main application entry point."""
    logger.info("=" * 60)
    logger.info("RAG STARTER KIT - PRO VERSION")
    logger.info("=" * 60)
    logger.info("Multi-provider support enabled")
    logger.info("Unlimited documents and queries")

    # Initialize session state
    init_session_state()

    # Check authentication if enabled
    if st.session_state.get('auth_enabled', False):
        if not check_authentication():
            render_auth()
            return

    # App header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🚀 RAG Starter Kit Pro")
        user = get_current_user()
        if user:
            st.caption(f"Welcome, {user['name']} • Full Version • Unlimited Access")
        else:
            st.caption("Full Version • Unlimited Documents • Unlimited Queries")
    with col2:
        st.markdown(
            """
            <div style='text-align: right; padding-top: 10px;'>
                <p style='color: #10B981; font-size: 0.9em; margin: 0;'>
                    ✅ Pro Version Active
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Render welcome section
    render_welcome_section()

    # Render sidebar and get generation settings
    temperature, max_tokens, n_results = render_sidebar()

    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📤 Upload Documents",
        "📝 Prompt Templates",
        "💬 Chat",
        "📊 Analytics",
        "💰 Cost Tracking (Experimental)",
        "⚙️ Manage Data",
    ])

    with tab1:
        render_file_upload()

    with tab2:
        render_prompt_library()

    with tab3:
        render_chat_interface(temperature, max_tokens, n_results)

    with tab4:
        render_analytics_dashboard()

    with tab5:
        render_cost_dashboard()

    with tab6:
        render_clear_data()

    # Footer
    st.divider()
    footer_col1, footer_col2 = st.columns([2, 1])
    with footer_col1:
        st.caption(
            "RAG Starter Kit Pro • OpenAI, Claude, Cohere, Ollama • "
            "ChromaDB, Pinecone, Weaviate • Unlimited Usage"
        )
    with footer_col2:
        st.markdown(
            """
            <div style='text-align: right;'>
                <p style='color: #10B981; font-size: 0.85em;'>
                    ✅ Licensed Version
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    logger.debug("Main render complete")


if __name__ == "__main__":
    main()
