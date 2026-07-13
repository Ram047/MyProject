import streamlit as st

from src.dashboard.utils.db import (
    get_companies,
    get_pl
)

st.set_page_config(layout="wide")

st.title("📈 Financial Trends")

companies = get_companies()

company = st.selectbox(
    "Select Company",
    companies["company_name"]
)

ticker = company

df = get_pl(ticker)

if df.empty:
    st.warning("No financial trend data available.")
else:
    st.line_chart(
        df.set_index("year")[["sales", "net_profit"]]
    )

    st.dataframe(
        df,
        use_container_width=True
    )