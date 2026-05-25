"""Sentinel AI Dashboard — Streamlit UI for monitoring reviews."""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from models import init_db, get_recent_reviews, get_review_stats

st.set_page_config(
    page_title="Sentinel AI Dashboard",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ Sentinel AI Dashboard")
st.markdown("AI-powered PR security & quality review — monitoring dashboard")

# Initialize DB
init_db()

# ── Sidebar ──────────────────────────────────────────────────
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Overview", "Recent Reviews", "Settings"])

# ── Overview ─────────────────────────────────────────────────
if page == "Overview":
    stats = get_review_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Reviews", stats["total_reviews"])
    col2.metric("Total Findings", stats["total_findings"])
    
    sev = stats.get("severity_breakdown", {})
    col3.metric("Critical/High", sev.get("critical", 0) + sev.get("high", 0))
    col4.metric("Medium/Low", sev.get("medium", 0) + sev.get("low", 0))
    
    st.subheader("Severity Breakdown")
    if sev:
        sev_df = pd.DataFrame(
            list(sev.items()), columns=["Severity", "Count"]
        )
        st.bar_chart(sev_df.set_index("Severity"))
    
    st.subheader("Tool Breakdown")
    tools = stats.get("tool_breakdown", {})
    if tools:
        tool_df = pd.DataFrame(
            list(tools.items()), columns=["Tool", "Count"]
        )
        st.bar_chart(tool_df.set_index("Tool"))

# ── Recent Reviews ───────────────────────────────────────────
elif page == "Recent Reviews":
    st.subheader("Recent Reviews")
    reviews = get_recent_reviews(50)
    
    if reviews:
        df = pd.DataFrame(reviews)
        df["created_at"] = pd.to_datetime(df["created_at"])
        
        # Format for display
        display_df = df[["id", "owner", "repo", "pull_number", "status", "total_findings", "created_at"]].copy()
        display_df.columns = ["ID", "Owner", "Repo", "PR#", "Status", "Findings", "Created"]
        
        st.dataframe(display_df, use_container_width=True)
        
        # Detail view
        st.subheader("Review Detail")
        selected_id = st.selectbox("Select review ID", df["id"].tolist())
        if selected_id:
            review = next(r for r in reviews if r["id"] == selected_id)
            st.json(review)
    else:
        st.info("No reviews yet. Install the GitHub App and open a PR to get started.")

# ── Settings ─────────────────────────────────────────────────
elif page == "Settings":
    st.subheader("Configuration")
    st.markdown("""
    ### Environment Variables
    
    | Variable | Description |
    |----------|-------------|
    | `GH_APP_ID` | GitHub App ID |
    | `GH_APP_PRIVATE_KEY` | Path to private key PEM file |
    | `GH_WEBHOOK_SECRET` | Webhook secret |
    | `OPENROUTER_API_KEY` | OpenRouter API key |
    | `OPENROUTER_MODEL` | Model to use (default: openai/gpt-4o-mini) |
    | `DATABASE_URL` | Database connection string |
    | `ENABLE_STATIC_ANALYSIS` | Enable bandit/flake8/semgrep (default: true) |
    | `ENABLE_LLM_REVIEW` | Enable LLM review (default: true) |
    
    ### Quick Start
    
    1. Create a GitHub App at https://github.com/settings/apps
    2. Set the webhook URL to your deployed endpoint
    3. Generate a private key
    4. Install the app on your repos
    5. Open a PR — Sentinel reviews automatically
    """)
