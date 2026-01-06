"""
Advanced Chat Component
Enhanced chat interface with additional features.
"""

import streamlit as st
from typing import List, Dict, Optional
import json
from datetime import datetime


def render_advanced_chat(
    pipeline,
    temperature: float = 0.7,
    max_tokens: int = 1000,
    show_sources: bool = True,
    enable_feedback: bool = True,
    enable_export: bool = True,
):
    """
    Render an advanced chat interface with enhanced features.

    Features:
    - Message reactions/feedback
    - Export conversations
    - Message editing
    - Source preview with highlights
    - Token usage display
    - Conversation branching
    """
    st.header("💬 Advanced Chat")

    # Initialize chat state
    if 'advanced_chat_history' not in st.session_state:
        st.session_state.advanced_chat_history = []
    if 'chat_branches' not in st.session_state:
        st.session_state.chat_branches = {}

    # Toolbar
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        search_query = st.text_input("Search chat history", placeholder="Search...")

    with col2:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.advanced_chat_history = []
            st.rerun()

    with col3:
        if enable_export and st.button("Export", use_container_width=True):
            export_chat(st.session_state.advanced_chat_history)

    with col4:
        view_mode = st.selectbox("View", ["Chat", "Timeline", "Sources"])

    st.divider()

    # Display messages based on view mode
    if view_mode == "Chat":
        render_chat_view(search_query, enable_feedback, show_sources)
    elif view_mode == "Timeline":
        render_timeline_view()
    else:
        render_sources_view()

    # Input area
    st.divider()
    render_input_area(pipeline, temperature, max_tokens)


def render_chat_view(search_query: str, enable_feedback: bool, show_sources: bool):
    """Render the standard chat view."""
    messages = st.session_state.advanced_chat_history

    # Filter messages if searching
    if search_query:
        messages = [
            m for m in messages
            if search_query.lower() in m.get('content', '').lower()
        ]

    # Display messages
    for i, message in enumerate(messages):
        with st.chat_message(message['role']):
            st.markdown(message['content'])

            # Message metadata
            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                if message.get('timestamp'):
                    st.caption(f"🕐 {message['timestamp']}")

            with col2:
                if message.get('tokens'):
                    st.caption(f"📊 {message['tokens']} tokens")

            # Feedback buttons
            if enable_feedback and message['role'] == 'assistant':
                with col3:
                    feedback_col1, feedback_col2 = st.columns(2)
                    with feedback_col1:
                        if st.button("👍", key=f"up_{i}"):
                            record_feedback(i, "positive")
                    with feedback_col2:
                        if st.button("👎", key=f"down_{i}"):
                            record_feedback(i, "negative")

            # Show sources
            if show_sources and message.get('sources'):
                with st.expander("📚 Sources"):
                    for source in message['sources']:
                        st.markdown(f"**{source['source']}**")
                        st.markdown(f"> {source['content'][:200]}...")


def render_timeline_view():
    """Render a timeline view of the conversation."""
    st.subheader("📅 Conversation Timeline")

    messages = st.session_state.advanced_chat_history

    for message in messages:
        timestamp = message.get('timestamp', 'Unknown time')
        role = "You" if message['role'] == 'user' else "Assistant"
        content = message['content'][:100] + "..." if len(message['content']) > 100 else message['content']

        st.markdown(f"""
        <div style='border-left: 3px solid {"#0084ff" if message["role"] == "user" else "#10B981"}; padding-left: 10px; margin: 10px 0;'>
            <strong>{timestamp}</strong> - {role}<br>
            <span style='color: #666;'>{content}</span>
        </div>
        """, unsafe_allow_html=True)


def render_sources_view():
    """Render a view focused on sources."""
    st.subheader("📚 All Sources Used")

    all_sources = []
    for message in st.session_state.advanced_chat_history:
        if message.get('sources'):
            all_sources.extend(message['sources'])

    # Deduplicate sources
    unique_sources = {}
    for source in all_sources:
        key = source.get('source', 'unknown')
        if key not in unique_sources:
            unique_sources[key] = source

    for source_name, source in unique_sources.items():
        with st.expander(f"📄 {source_name}"):
            st.write(source.get('content', 'No content available'))


def render_input_area(pipeline, temperature: float, max_tokens: int):
    """Render the chat input area."""
    col1, col2 = st.columns([6, 1])

    with col1:
        user_input = st.chat_input("Ask a question...")

    with col2:
        attach_file = st.file_uploader("📎", type=['txt', 'pdf'], label_visibility="collapsed")

    if user_input:
        # Add user message
        st.session_state.advanced_chat_history.append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now().strftime("%H:%M:%S"),
        })

        # Generate response
        with st.chat_message("assistant"):
            placeholder = st.empty()
            response = ""
            sources = []

            try:
                if pipeline:
                    # Get sources
                    search_results = pipeline.search(user_input, n_results=5)
                    sources = [
                        {'source': r['metadata'].get('source', 'unknown'), 'content': r['content'][:200]}
                        for r in search_results
                    ]

                    # Stream response
                    for token in pipeline.query_stream(
                        user_input,
                        temperature=temperature,
                        max_tokens=max_tokens
                    ):
                        response += token
                        placeholder.markdown(response + "▌")

                    placeholder.markdown(response)
                else:
                    response = "Please initialize the RAG pipeline first."
                    placeholder.markdown(response)

            except Exception as e:
                response = f"Error: {str(e)}"
                placeholder.error(response)

            # Add assistant message
            st.session_state.advanced_chat_history.append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now().strftime("%H:%M:%S"),
                'tokens': len(response.split()),
                'sources': sources,
            })

        st.rerun()


def record_feedback(message_index: int, feedback_type: str):
    """Record user feedback on a message."""
    if 'feedback' not in st.session_state:
        st.session_state.feedback = {}

    st.session_state.feedback[message_index] = {
        'type': feedback_type,
        'timestamp': datetime.now().isoformat(),
    }

    st.success(f"Feedback recorded: {feedback_type}")


def export_chat(messages: List[Dict]):
    """Export chat history."""
    export_data = {
        'exported_at': datetime.now().isoformat(),
        'messages': messages,
    }

    json_str = json.dumps(export_data, indent=2)

    st.download_button(
        label="Download Chat History",
        data=json_str,
        file_name=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
    )
