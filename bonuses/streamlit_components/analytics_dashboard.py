"""
Analytics Dashboard Component
Comprehensive analytics visualization for RAG applications.
"""

import streamlit as st
from typing import Dict, List, Any
from datetime import datetime, timedelta
import json


def render_analytics_dashboard(analytics_data: Dict[str, Any] = None):
    """
    Render a comprehensive analytics dashboard.

    Features:
    - Query volume trends
    - Response time analysis
    - Token usage breakdown
    - Cost analysis
    - User engagement metrics
    - Document statistics
    """
    st.header("📊 Analytics Dashboard")

    # Use session state if no data provided
    if analytics_data is None:
        analytics_data = st.session_state.get('analytics_data', {
            'queries': [],
            'documents': [],
        })

    # Time range selector
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        time_range = st.selectbox(
            "Time Range",
            ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "All Time"]
        )
    with col2:
        metric_type = st.selectbox(
            "Metric Type",
            ["Overview", "Performance", "Costs", "Documents"]
        )
    with col3:
        if st.button("Refresh", use_container_width=True):
            st.rerun()

    st.divider()

    # Render based on selected view
    if metric_type == "Overview":
        render_overview(analytics_data)
    elif metric_type == "Performance":
        render_performance(analytics_data)
    elif metric_type == "Costs":
        render_costs(analytics_data)
    else:
        render_documents(analytics_data)


def render_overview(data: Dict):
    """Render overview metrics."""
    queries = data.get('queries', [])
    documents = data.get('documents', [])

    # Top metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Queries",
            len(queries),
            delta=f"+{len([q for q in queries[-10:]])} recent"
        )

    with col2:
        avg_time = sum(q.get('response_time', 0) for q in queries) / max(len(queries), 1)
        st.metric(
            "Avg Response Time",
            f"{avg_time:.2f}s"
        )

    with col3:
        total_tokens = sum(q.get('tokens_used', 0) for q in queries)
        st.metric(
            "Total Tokens",
            f"{total_tokens:,}"
        )

    with col4:
        success_rate = sum(1 for q in queries if q.get('success', True)) / max(len(queries), 1) * 100
        st.metric(
            "Success Rate",
            f"{success_rate:.1f}%"
        )

    st.divider()

    # Recent activity
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Recent Queries")
        for query in queries[-5:][::-1]:
            with st.container():
                st.text(f"🔍 {query.get('query', 'Unknown')[:50]}...")
                st.caption(f"{query.get('timestamp', 'Unknown time')}")

    with col2:
        st.subheader("Recent Documents")
        for doc in documents[-5:][::-1]:
            st.text(f"📄 {doc.get('filename', 'Unknown')}")
            st.caption(f"{doc.get('chunks', 0)} chunks")


def render_performance(data: Dict):
    """Render performance metrics."""
    queries = data.get('queries', [])

    st.subheader("📈 Performance Metrics")

    if not queries:
        st.info("No query data available yet.")
        return

    # Response time statistics
    response_times = [q.get('response_time', 0) for q in queries]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Min Response Time", f"{min(response_times):.2f}s")

    with col2:
        st.metric("Max Response Time", f"{max(response_times):.2f}s")

    with col3:
        avg = sum(response_times) / len(response_times)
        st.metric("Average", f"{avg:.2f}s")

    st.divider()

    # Response time distribution
    st.subheader("Response Time Distribution")

    # Create histogram data
    buckets = {"<1s": 0, "1-2s": 0, "2-5s": 0, "5-10s": 0, ">10s": 0}
    for rt in response_times:
        if rt < 1:
            buckets["<1s"] += 1
        elif rt < 2:
            buckets["1-2s"] += 1
        elif rt < 5:
            buckets["2-5s"] += 1
        elif rt < 10:
            buckets["5-10s"] += 1
        else:
            buckets[">10s"] += 1

    for bucket, count in buckets.items():
        percentage = count / len(response_times) * 100
        st.progress(percentage / 100, text=f"{bucket}: {count} ({percentage:.1f}%)")


def render_costs(data: Dict):
    """Render cost analysis."""
    st.subheader("💰 Cost Analysis")

    cost_data = st.session_state.get('cost_history', [])

    if not cost_data:
        st.info("No cost data available yet.")
        return

    total_cost = sum(c.get('cost', 0) for c in cost_data)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Cost", f"${total_cost:.4f}")

    with col2:
        today = datetime.now().strftime("%Y-%m-%d")
        today_cost = sum(
            c.get('cost', 0) for c in cost_data
            if c.get('timestamp', '').startswith(today)
        )
        st.metric("Today's Cost", f"${today_cost:.4f}")

    with col3:
        avg_cost = total_cost / max(len(cost_data), 1)
        st.metric("Avg Cost/Query", f"${avg_cost:.6f}")

    st.divider()

    # Cost by provider
    st.subheader("Cost by Provider")
    provider_costs = {}
    for c in cost_data:
        provider = c.get('provider', 'unknown')
        provider_costs[provider] = provider_costs.get(provider, 0) + c.get('cost', 0)

    for provider, cost in sorted(provider_costs.items(), key=lambda x: x[1], reverse=True):
        percentage = cost / total_cost * 100 if total_cost > 0 else 0
        st.progress(percentage / 100, text=f"{provider}: ${cost:.4f} ({percentage:.1f}%)")


def render_documents(data: Dict):
    """Render document statistics."""
    st.subheader("📄 Document Statistics")

    documents = data.get('documents', [])

    if not documents:
        st.info("No documents uploaded yet.")
        return

    # Document metrics
    total_chunks = sum(d.get('chunks', 0) for d in documents)
    total_size = sum(d.get('file_size', 0) for d in documents)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Documents", len(documents))

    with col2:
        st.metric("Total Chunks", total_chunks)

    with col3:
        st.metric("Total Size", f"{total_size / 1024:.1f} KB")

    st.divider()

    # Document list
    st.subheader("Uploaded Documents")

    for doc in documents:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"📄 **{doc.get('filename', 'Unknown')}**")
            with col2:
                st.write(f"{doc.get('chunks', 0)} chunks")
            with col3:
                st.write(f"{doc.get('file_size', 0) / 1024:.1f} KB")


def export_analytics(data: Dict) -> str:
    """Export analytics data as JSON."""
    export = {
        'exported_at': datetime.now().isoformat(),
        'analytics': data,
        'costs': st.session_state.get('cost_history', []),
    }
    return json.dumps(export, indent=2)
