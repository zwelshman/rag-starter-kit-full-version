"""
Chat Interface Component
Handles the chat UI and interaction with the RAG pipeline.
"""

import streamlit as st
import logging
import time
from core.retrieval_engine import SearchMode

logger = logging.getLogger("rag_app.components.chat_interface")


def render_chat_interface(temperature: float = 0.7, max_tokens: int = 1000, n_results: int = 20):
    """
    Render the chat interface.

    Args:
        temperature: LLM temperature setting
        max_tokens: Maximum tokens for response
        n_results: Number of document chunks to retrieve
    """
    st.header("Ask Questions")

    if not st.session_state.get('rag_pipeline'):
        st.info("Please initialize the pipeline in the sidebar to start asking questions.")
        return

    pipeline_stats = st.session_state.rag_pipeline.get_stats()
    if not st.session_state.get('documents_loaded') and pipeline_stats['vector_store_count'] == 0:
        st.info("Please upload and process some documents first.")
        return

    # Template integration and controls
    active_template = st.session_state.get('active_template')

    # Control buttons row
    col1, col2, col3, col4 = st.columns([2, 2, 2, 4])
    with col1:
        if st.button("🗑️ Clear Chat", type="secondary", use_container_width=True):
            st.session_state.chat_history = []
            logger.info("Chat history cleared from Chat tab")
            st.rerun()
    with col2:
        # Export chat history
        chat_history = st.session_state.get('chat_history', [])
        if chat_history:
            import json
            chat_export = json.dumps(chat_history, indent=2, default=str)
            st.download_button(
                label="📥 Export Chat",
                data=chat_export,
                file_name="chat_history.json",
                mime="application/json",
                use_container_width=True
            )
        else:
            st.button("📥 Export Chat", type="secondary", use_container_width=True, disabled=True)
    with col3:
        if active_template:
            if st.button("Clear Template", type="secondary", use_container_width=True):
                st.session_state.active_template = None
                st.rerun()

    # Show active template status
    if active_template:
        st.success(f"📝 **Active Template:** {active_template['name']}")
        with st.expander("View Template Content", expanded=False):
            st.code(active_template.get('content', 'No content'), language="text")
            st.caption("Your question will replace `{question}` in the template above.")
    else:
        st.info("💡 **Tip:** Select a template from the **Prompt Templates** tab to customize how your questions are formatted.")

    st.divider()

    # Display chat history
    for message in st.session_state.get('chat_history', []):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Show the formatted prompt that was sent (for assistant messages with template)
            if message["role"] == "assistant" and message.get("formatted_prompt"):
                sources_count = len(message.get("sources", []))
                with st.expander("🔍 View Full Prompt Sent to LLM"):
                    st.caption(f"Retrieved {sources_count} document chunks from vector database")
                    st.code(message["formatted_prompt"], language="text")

            # Show sources for assistant messages
            if message["role"] == "assistant" and "sources" in message:
                from .citation_viewer import render_sources_expander
                render_sources_expander(message["sources"])

    # Chat input
    if question := st.chat_input("Ask a question about your documents..."):
        start_time = time.time()

        logger.info("=" * 60)
        logger.info("USER QUERY RECEIVED")
        logger.info("=" * 60)
        logger.info(f"Question: {question[:100]}{'...' if len(question) > 100 else ''}")
        logger.info(f"Temperature: {temperature}")
        logger.info(f"Max tokens: {max_tokens}")

        # Format question with template if active
        formatted_prompt = None
        if active_template:
            template_content = active_template.get('content', '{question}')
            # Replace placeholders
            formatted_prompt = template_content.replace('{question}', question)
            logger.info(f"Using template: {active_template['name']}")

        # Add user message to history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

        st.session_state.chat_history.append({
            "role": "user",
            "content": question,
        })

        # Display user message
        with st.chat_message("user"):
            st.markdown(question)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Searching documents and generating response..."):
                try:
                    # Use streaming if supported
                    response_placeholder = st.empty()
                    full_response = ""

                    # Get sources first
                    logger.info(f"Searching for relevant documents (n_results={n_results})...")
                    sources = st.session_state.rag_pipeline.search(question, n_results=n_results)
                    logger.info(f"Found {len(sources)} relevant document chunks")

                    # Log source information
                    for i, src in enumerate(sources, 1):
                        source_name = src.get('metadata', {}).get('source', 'Unknown')
                        score_key = 'score' if 'score' in src else 'rrf_score'
                        score = src.get(score_key, 'N/A')
                        logger.info(f"  Source {i}: {source_name} (score: {score})")

                    # Build context from sources for template (use all retrieved sources)
                    context_text = "\n\n".join([
                        f"[Source: {src.get('metadata', {}).get('source', 'Unknown')}]\n{src.get('content', '')[:500]}..."
                        if len(src.get('content', '')) > 500
                        else f"[Source: {src.get('metadata', {}).get('source', 'Unknown')}]\n{src.get('content', '')}"
                        for src in sources  # Use all retrieved sources
                    ])

                    # Format the actual prompt with real context
                    actual_prompt = None
                    if formatted_prompt:
                        actual_prompt = formatted_prompt.replace('{context}', context_text)

                    # Stream the response
                    logger.info("Generating response...")
                    for token in st.session_state.rag_pipeline.query_stream(
                        question=formatted_prompt if formatted_prompt else question,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    ):
                        full_response += token
                        response_placeholder.markdown(full_response + "▌")

                    response_placeholder.markdown(full_response)

                    # Calculate metrics
                    response_time = time.time() - start_time
                    tokens_used = len(full_response.split())  # Approximate

                    logger.info(f"Response generated: {len(full_response)} characters")
                    logger.info(f"Response time: {response_time:.2f}s")
                    logger.info("QUERY COMPLETE")
                    logger.info("=" * 60)

                    # Show the actual prompt that was sent (with real context)
                    if actual_prompt:
                        with st.expander("🔍 View Full Prompt Sent to LLM", expanded=False):
                            st.caption(f"Retrieved {len(sources)} document chunks from vector database")
                            st.code(actual_prompt, language="text")

                    # Show sources
                    if sources:
                        from .citation_viewer import render_sources_expander
                        render_sources_expander(sources)

                    # Add assistant message to history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": full_response,
                        "sources": sources,
                        "formatted_prompt": actual_prompt,  # Store actual prompt with real context
                    })

                    # Track query for analytics
                    from components.analytics import track_query
                    track_query(
                        query=question,
                        response_time=response_time,
                        tokens_used=tokens_used,
                        sources_count=len(sources),
                        success=True
                    )

                    # Track cost (experimental)
                    from components.cost_tracker import track_query_cost
                    provider = st.session_state.get('llm_provider', 'anthropic')
                    model = st.session_state.get('llm_model', 'claude-sonnet-4-5')
                    # Estimate input tokens from context + question
                    context_text = " ".join([s.get('content', '') for s in sources])
                    input_tokens = len((context_text + question).split())
                    track_query_cost(
                        provider=provider,
                        model=model,
                        input_tokens=input_tokens,
                        output_tokens=tokens_used
                    )

                    # Auto-scroll to bottom of chat and refresh button states
                    st.rerun()

                except Exception as e:
                    logger.error(f"Query failed: {e}")
                    st.error(f"Error generating response: {e}")

                    # Track failed query
                    from components.analytics import track_query
                    track_query(
                        query=question,
                        response_time=time.time() - start_time,
                        tokens_used=0,
                        sources_count=0,
                        success=False
                    )
