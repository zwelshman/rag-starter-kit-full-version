"""
Cost Tracking Component
Track and analyze API costs across different providers.
"""

import streamlit as st
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

logger = logging.getLogger("rag_app.components.cost_tracker")


# Pricing data (per 1M tokens as of 2024)
PRICING = {
    "openai": {
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        "gpt-4": {"input": 30.00, "output": 60.00},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    },
    "anthropic": {
        "claude-sonnet-4-5": {"input": 3.00, "output": 15.00},
        "claude-opus-4-5": {"input": 15.00, "output": 75.00},
        "claude-haiku-4-5": {"input": 0.25, "output": 1.25},
        "claude-3-opus": {"input": 15.00, "output": 75.00},
        "claude-3-sonnet": {"input": 3.00, "output": 15.00},
        "claude-3-haiku": {"input": 0.25, "output": 1.25},
    },
    "cohere": {
        "command-r-plus": {"input": 3.00, "output": 15.00},
        "command-r": {"input": 0.50, "output": 1.50},
        "command": {"input": 1.00, "output": 2.00},
        "command-light": {"input": 0.30, "output": 0.60},
    },
    "ollama": {
        "llama3.2": {"input": 0.00, "output": 0.00},
        "llama3.1": {"input": 0.00, "output": 0.00},
        "mistral": {"input": 0.00, "output": 0.00},
        "mixtral": {"input": 0.00, "output": 0.00},
    },
}


@dataclass
class CostEntry:
    """Represents a single cost entry."""
    timestamp: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    query_type: str = "chat"


def init_cost_state():
    """Initialize cost tracking session state."""
    if 'cost_history' not in st.session_state:
        st.session_state.cost_history = []
    if 'cost_budget' not in st.session_state:
        st.session_state.cost_budget = {
            "daily_limit": 10.00,
            "monthly_limit": 100.00,
            "alerts_enabled": True,
        }
    if 'cost_alerts' not in st.session_state:
        st.session_state.cost_alerts = []


def calculate_cost(
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int
) -> float:
    """
    Calculate the cost for a specific API call.

    Args:
        provider: LLM provider name
        model: Model name
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        Cost in USD
    """
    provider_pricing = PRICING.get(provider.lower(), {})
    model_pricing = provider_pricing.get(model, {"input": 0, "output": 0})

    input_cost = (input_tokens / 1_000_000) * model_pricing["input"]
    output_cost = (output_tokens / 1_000_000) * model_pricing["output"]

    return round(input_cost + output_cost, 6)


def track_query_cost(
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    query_type: str = "chat"
) -> float:
    """
    Track the cost of a query.

    Args:
        provider: LLM provider name
        model: Model name
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        query_type: Type of query (chat, embedding, etc.)

    Returns:
        Cost in USD
    """
    init_cost_state()

    cost = calculate_cost(provider, model, input_tokens, output_tokens)

    entry = CostEntry(
        timestamp=datetime.now().isoformat(),
        provider=provider,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost=cost,
        query_type=query_type,
    )

    st.session_state.cost_history.append(entry.__dict__)

    # Check budget alerts
    check_budget_alerts()

    logger.debug(f"Cost tracked: ${cost:.6f} for {provider}/{model}")
    return cost


def get_cost_summary() -> Dict[str, Any]:
    """Get a summary of all costs."""
    init_cost_state()

    history = st.session_state.cost_history
    if not history:
        return {
            "total_cost": 0.0,
            "today_cost": 0.0,
            "month_cost": 0.0,
            "total_queries": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "by_provider": {},
            "by_model": {},
        }

    today = datetime.now().strftime("%Y-%m-%d")
    month = datetime.now().strftime("%Y-%m")

    today_cost = sum(
        e["cost"] for e in history
        if e["timestamp"].startswith(today)
    )

    month_cost = sum(
        e["cost"] for e in history
        if e["timestamp"].startswith(month)
    )

    # Aggregate by provider
    by_provider = {}
    for e in history:
        provider = e["provider"]
        if provider not in by_provider:
            by_provider[provider] = {"cost": 0.0, "queries": 0}
        by_provider[provider]["cost"] += e["cost"]
        by_provider[provider]["queries"] += 1

    # Aggregate by model
    by_model = {}
    for e in history:
        model = e["model"]
        if model not in by_model:
            by_model[model] = {"cost": 0.0, "queries": 0}
        by_model[model]["cost"] += e["cost"]
        by_model[model]["queries"] += 1

    return {
        "total_cost": sum(e["cost"] for e in history),
        "today_cost": today_cost,
        "month_cost": month_cost,
        "total_queries": len(history),
        "total_input_tokens": sum(e["input_tokens"] for e in history),
        "total_output_tokens": sum(e["output_tokens"] for e in history),
        "by_provider": by_provider,
        "by_model": by_model,
    }


def check_budget_alerts():
    """Check if any budget thresholds have been crossed."""
    init_cost_state()

    if not st.session_state.cost_budget["alerts_enabled"]:
        return

    summary = get_cost_summary()
    budget = st.session_state.cost_budget

    # Check daily limit
    if summary["today_cost"] >= budget["daily_limit"]:
        alert = f"Daily budget limit (${budget['daily_limit']:.2f}) reached!"
        if alert not in st.session_state.cost_alerts:
            st.session_state.cost_alerts.append(alert)
            logger.warning(alert)

    # Check monthly limit (80% warning)
    if summary["month_cost"] >= budget["monthly_limit"] * 0.8:
        alert = f"80% of monthly budget (${budget['monthly_limit']:.2f}) used!"
        if alert not in st.session_state.cost_alerts:
            st.session_state.cost_alerts.append(alert)
            logger.warning(alert)


def render_cost_dashboard():
    """Render the cost tracking dashboard."""
    init_cost_state()

    st.header("💰 Cost Tracking Dashboard")

    # Show alerts
    if st.session_state.cost_alerts:
        for alert in st.session_state.cost_alerts:
            st.warning(alert)
        if st.button("Clear Alerts"):
            st.session_state.cost_alerts = []
            st.rerun()

    summary = get_cost_summary()

    # Top-level metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Cost",
            f"${summary['total_cost']:.4f}",
            help="All-time total cost"
        )

    with col2:
        budget = st.session_state.cost_budget
        daily_pct = (summary['today_cost'] / budget['daily_limit']) * 100 if budget['daily_limit'] > 0 else 0
        st.metric(
            "Today's Cost",
            f"${summary['today_cost']:.4f}",
            delta=f"{daily_pct:.1f}% of daily budget",
            delta_color="inverse" if daily_pct > 80 else "normal"
        )

    with col3:
        monthly_pct = (summary['month_cost'] / budget['monthly_limit']) * 100 if budget['monthly_limit'] > 0 else 0
        st.metric(
            "Monthly Cost",
            f"${summary['month_cost']:.4f}",
            delta=f"{monthly_pct:.1f}% of monthly budget",
            delta_color="inverse" if monthly_pct > 80 else "normal"
        )

    with col4:
        st.metric(
            "Total Queries",
            summary['total_queries'],
            help="Total number of API calls"
        )

    st.divider()

    # Detailed tabs
    tab1, tab2, tab3 = st.tabs(["Cost Breakdown", "Token Usage", "Budget Settings"])

    with tab1:
        render_cost_breakdown(summary)

    with tab2:
        render_token_usage(summary)

    with tab3:
        render_budget_settings()


def render_cost_breakdown(summary: Dict[str, Any]):
    """Render cost breakdown by provider and model."""
    st.subheader("Cost Breakdown")

    if not summary["by_provider"]:
        st.info("No cost data available yet. Start making queries to track costs.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**By Provider**")
        for provider, data in summary["by_provider"].items():
            st.write(f"🏢 **{provider.capitalize()}**")
            st.write(f"   - Cost: ${data['cost']:.4f}")
            st.write(f"   - Queries: {data['queries']}")

    with col2:
        st.markdown("**By Model**")
        for model, data in sorted(summary["by_model"].items(), key=lambda x: x[1]["cost"], reverse=True):
            st.write(f"🤖 **{model}**")
            st.write(f"   - Cost: ${data['cost']:.4f}")
            st.write(f"   - Queries: {data['queries']}")

    # Cost history
    st.markdown("---")
    st.subheader("Recent API Calls")

    history = st.session_state.cost_history[-10:][::-1]
    for entry in history:
        timestamp = entry["timestamp"].split("T")[1][:8]
        st.write(
            f"⏱️ {timestamp} | **{entry['provider']}/{entry['model']}** | "
            f"{entry['input_tokens']}→{entry['output_tokens']} tokens | "
            f"${entry['cost']:.6f}"
        )


def render_token_usage(summary: Dict[str, Any]):
    """Render token usage statistics."""
    st.subheader("Token Usage")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Input Tokens", f"{summary['total_input_tokens']:,}")

    with col2:
        st.metric("Total Output Tokens", f"{summary['total_output_tokens']:,}")

    if summary['total_queries'] > 0:
        avg_input = summary['total_input_tokens'] / summary['total_queries']
        avg_output = summary['total_output_tokens'] / summary['total_queries']

        st.markdown("---")
        st.write("**Averages per Query:**")
        st.write(f"- Input tokens: {avg_input:.0f}")
        st.write(f"- Output tokens: {avg_output:.0f}")
        st.write(f"- Cost: ${summary['total_cost'] / summary['total_queries']:.6f}")


def render_budget_settings():
    """Render budget settings form."""
    st.subheader("Budget Settings")

    budget = st.session_state.cost_budget

    with st.form("budget_form"):
        daily_limit = st.number_input(
            "Daily Budget Limit ($)",
            value=budget["daily_limit"],
            min_value=0.0,
            max_value=1000.0,
            step=1.0
        )

        monthly_limit = st.number_input(
            "Monthly Budget Limit ($)",
            value=budget["monthly_limit"],
            min_value=0.0,
            max_value=10000.0,
            step=10.0
        )

        alerts_enabled = st.checkbox(
            "Enable Budget Alerts",
            value=budget["alerts_enabled"]
        )

        if st.form_submit_button("Save Settings", use_container_width=True):
            st.session_state.cost_budget = {
                "daily_limit": daily_limit,
                "monthly_limit": monthly_limit,
                "alerts_enabled": alerts_enabled,
            }
            st.success("Budget settings saved!")

    st.markdown("---")
    if st.button("Clear Cost History", type="secondary"):
        st.session_state.cost_history = []
        st.session_state.cost_alerts = []
        st.success("Cost history cleared!")
        st.rerun()


def export_cost_data() -> str:
    """Export cost data as JSON."""
    init_cost_state()
    return json.dumps({
        "history": st.session_state.cost_history,
        "budget": st.session_state.cost_budget,
        "summary": get_cost_summary(),
        "exported_at": datetime.now().isoformat(),
    }, indent=2)


# Provider cost comparison helper
def get_cost_comparison(input_tokens: int, output_tokens: int) -> Dict[str, float]:
    """
    Get cost comparison across all providers/models.

    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        Dictionary of model -> cost
    """
    comparison = {}
    for provider, models in PRICING.items():
        for model, pricing in models.items():
            cost = calculate_cost(provider, model, input_tokens, output_tokens)
            comparison[f"{provider}/{model}"] = cost
    return dict(sorted(comparison.items(), key=lambda x: x[1]))
