"""
Analytics Dashboard Component
Provides usage analytics, query insights, and performance metrics.
"""

import streamlit as st
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import Counter
import json

logger = logging.getLogger("rag_app.components.analytics")


def init_analytics_state():
    """Initialize analytics session state."""
    if 'analytics_data' not in st.session_state:
        st.session_state.analytics_data = {
            "queries": [],
            "documents": [],
            "sessions": [],
            "errors": [],
        }
    if 'daily_stats' not in st.session_state:
        st.session_state.daily_stats = {}


def track_query(query: str, response_time: float, tokens_used: int, sources_count: int, success: bool = True):
    """
    Track a query for analytics.

    Args:
        query: The query text
        response_time: Time taken to respond (seconds)
        tokens_used: Number of tokens used
        sources_count: Number of sources retrieved
        success: Whether the query was successful
    """
    init_analytics_state()

    query_data = {
        "timestamp": datetime.now().isoformat(),
        "query": query[:200],  # Truncate for storage
        "response_time": response_time,
        "tokens_used": tokens_used,
        "sources_count": sources_count,
        "success": success,
    }

    st.session_state.analytics_data["queries"].append(query_data)

    # Update daily stats
    today = datetime.now().strftime("%Y-%m-%d")
    if today not in st.session_state.daily_stats:
        st.session_state.daily_stats[today] = {
            "queries": 0,
            "tokens": 0,
            "avg_response_time": 0,
            "errors": 0,
        }

    stats = st.session_state.daily_stats[today]
    stats["queries"] += 1
    stats["tokens"] += tokens_used
    if not success:
        stats["errors"] += 1

    # Update running average
    n = stats["queries"]
    stats["avg_response_time"] = (stats["avg_response_time"] * (n - 1) + response_time) / n

    logger.debug(f"Query tracked: {query[:50]}...")


def track_document_upload(filename: str, chunks: int, file_size: int):
    """
    Track a document upload for analytics.

    Args:
        filename: Name of the uploaded file
        chunks: Number of chunks created
        file_size: File size in bytes
    """
    init_analytics_state()

    doc_data = {
        "timestamp": datetime.now().isoformat(),
        "filename": filename,
        "chunks": chunks,
        "file_size": file_size,
    }

    st.session_state.analytics_data["documents"].append(doc_data)
    logger.debug(f"Document upload tracked: {filename}")


def get_analytics_summary() -> Dict[str, Any]:
    """Get a summary of analytics data."""
    init_analytics_state()

    queries = st.session_state.analytics_data["queries"]
    documents = st.session_state.analytics_data["documents"]

    if not queries:
        return {
            "total_queries": 0,
            "total_documents": 0,
            "total_tokens": 0,
            "avg_response_time": 0,
            "success_rate": 0,
        }

    total_tokens = sum(q["tokens_used"] for q in queries)
    avg_response_time = sum(q["response_time"] for q in queries) / len(queries)
    success_count = sum(1 for q in queries if q["success"])

    return {
        "total_queries": len(queries),
        "total_documents": len(documents),
        "total_tokens": total_tokens,
        "avg_response_time": round(avg_response_time, 2),
        "success_rate": round(success_count / len(queries) * 100, 1),
        "total_chunks": sum(d["chunks"] for d in documents),
    }


def render_analytics_dashboard():
    """Render the analytics dashboard."""
    init_analytics_state()

    st.header("📊 Analytics Dashboard")

    # Summary metrics
    summary = get_analytics_summary()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Queries",
            summary["total_queries"],
            help="Total number of queries made"
        )

    with col2:
        st.metric(
            "Documents Indexed",
            summary["total_documents"],
            help="Total documents uploaded"
        )

    with col3:
        st.metric(
            "Avg Response Time",
            f"{summary['avg_response_time']}s",
            help="Average query response time"
        )

    with col4:
        st.metric(
            "Success Rate",
            f"{summary['success_rate']}%",
            help="Percentage of successful queries"
        )

    st.divider()

    # Detailed analytics tabs
    tab1, tab2, tab3 = st.tabs(["Query History", "Document Stats", "Performance"])

    with tab1:
        render_query_history()

    with tab2:
        render_document_stats()

    with tab3:
        render_performance_metrics()


def render_query_history():
    """Render query history section."""
    st.subheader("Recent Queries")

    queries = st.session_state.analytics_data.get("queries", [])

    if not queries:
        st.info("No queries recorded yet. Start asking questions to see analytics.")
        return

    # Show last 20 queries
    recent_queries = queries[-20:][::-1]

    for i, q in enumerate(recent_queries):
        with st.expander(f"Query {len(queries) - i}: {q['query'][:50]}..."):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Response Time:** {q['response_time']:.2f}s")
            with col2:
                st.write(f"**Tokens Used:** {q['tokens_used']}")
            with col3:
                status = "✅ Success" if q['success'] else "❌ Failed"
                st.write(f"**Status:** {status}")

            st.write(f"**Sources Retrieved:** {q['sources_count']}")
            st.write(f"**Timestamp:** {q['timestamp']}")


def render_document_stats():
    """Render document statistics section."""
    st.subheader("Document Statistics")

    documents = st.session_state.analytics_data.get("documents", [])

    if not documents:
        st.info("No documents uploaded yet.")
        return

    # Calculate stats
    total_chunks = sum(d["chunks"] for d in documents)
    total_size = sum(d["file_size"] for d in documents)
    avg_chunks = total_chunks / len(documents)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Documents", len(documents))
    with col2:
        st.metric("Total Chunks", total_chunks)
    with col3:
        st.metric("Avg Chunks/Doc", round(avg_chunks, 1))

    st.markdown("---")
    st.subheader("Document List")

    for doc in documents[::-1]:  # Most recent first
        st.write(f"📄 **{doc['filename']}** - {doc['chunks']} chunks ({doc['file_size'] / 1024:.1f} KB)")


def render_performance_metrics():
    """Render performance metrics section."""
    st.subheader("Performance Metrics")

    queries = st.session_state.analytics_data.get("queries", [])

    if not queries:
        st.info("No performance data available yet.")
        return

    # Response time distribution
    response_times = [q["response_time"] for q in queries]

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Response Time Statistics**")
        st.write(f"- Minimum: {min(response_times):.2f}s")
        st.write(f"- Maximum: {max(response_times):.2f}s")
        st.write(f"- Average: {sum(response_times) / len(response_times):.2f}s")

        # Percentiles
        sorted_times = sorted(response_times)
        p50_idx = int(len(sorted_times) * 0.5)
        p95_idx = int(len(sorted_times) * 0.95)
        st.write(f"- P50: {sorted_times[p50_idx]:.2f}s")
        st.write(f"- P95: {sorted_times[min(p95_idx, len(sorted_times) - 1)]:.2f}s")

    with col2:
        st.write("**Token Usage Statistics**")
        tokens = [q["tokens_used"] for q in queries]
        st.write(f"- Total Tokens: {sum(tokens):,}")
        st.write(f"- Avg per Query: {sum(tokens) / len(tokens):.0f}")
        st.write(f"- Min per Query: {min(tokens)}")
        st.write(f"- Max per Query: {max(tokens)}")

    # Daily breakdown
    st.markdown("---")
    st.subheader("Daily Statistics")

    daily_stats = st.session_state.daily_stats
    if daily_stats:
        for date, stats in sorted(daily_stats.items(), reverse=True)[:7]:
            st.write(f"**{date}**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.write(f"Queries: {stats['queries']}")
            with col2:
                st.write(f"Tokens: {stats['tokens']:,}")
            with col3:
                st.write(f"Avg Time: {stats['avg_response_time']:.2f}s")
            with col4:
                st.write(f"Errors: {stats['errors']}")


def export_analytics() -> str:
    """Export analytics data as JSON."""
    init_analytics_state()
    return json.dumps({
        "analytics": st.session_state.analytics_data,
        "daily_stats": st.session_state.daily_stats,
        "exported_at": datetime.now().isoformat(),
    }, indent=2)


def clear_analytics():
    """Clear all analytics data."""
    init_analytics_state()
    st.session_state.analytics_data = {
        "queries": [],
        "documents": [],
        "sessions": [],
        "errors": [],
    }
    st.session_state.daily_stats = {}
    logger.info("Analytics data cleared")
