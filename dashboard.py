# Sentinel AI Dashboard (Streamlit)

import streamlit as st
import pandas as pd
from sentinel_ai.config import DATABASE_URL
import psycopg2

st.set_page_config(page_title="Sentinel AI Dashboard", layout="wide")
st.title("🛡️ Sentinel AI Dashboard")

st.header("Recent Reviews")
# Placeholder: fetch from DB
data = [
    {"Repo": "example/repo", "PR": 12, "Findings": 3, "Status": "Completed"},
    {"Repo": "myproject/api", "PR": 5, "Findings": 0, "Status": "Completed"},
]
st.table(pd.DataFrame(data))

st.header("Configuration")
st.info("Set your GitHub App credentials in .env to enable webhooks.")

st.header("Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total PRs Reviewed", "1,234")
col2.metric("Avg Findings/PR", "2.4")
col3.metric("Critical Issues", "56")
