import streamlit as st
from src.dashboard.utils.db import get_companies

st.set_page_config(layout="wide")

st.title("🏠 Home")

companies = get_companies()

col1, col2, col3 = st.columns(3)

col1.metric("Companies", len(companies))
col2.metric("Database", "SQLite")
col3.metric("Universe", "Nifty 100")

st.markdown("---")

st.subheader("Company List")

st.dataframe(
    companies[
        [
            "company_name",
            "roe_percentage",
            "roce_percentage"
        ]
    ],
    use_container_width=True
)