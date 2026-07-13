import streamlit as st

from src.dashboard.utils.db import (
    get_companies,
    get_ratios,
    get_pl,
    get_bs,
    get_cf,
    get_valuation
)

st.set_page_config(layout="wide")

st.title("🏢 Company Profile")

companies = get_companies()

company = st.selectbox(
    "Select Company",
    companies.company_name.tolist()
)

ticker = companies.loc[
    companies.company_name == company
].index[0]

ticker = companies.iloc[ticker]["company_name"]

st.header(company)

tabs = st.tabs(
    [
        "Financial Ratios",
        "Profit & Loss",
        "Balance Sheet",
        "Cash Flow",
        "Valuation"
    ]
)

with tabs[0]:
    st.dataframe(
        get_ratios(ticker),
        use_container_width=True
    )

with tabs[1]:
    st.dataframe(
        get_pl(ticker),
        use_container_width=True
    )

with tabs[2]:
    st.dataframe(
        get_bs(ticker),
        use_container_width=True
    )

with tabs[3]:
    st.dataframe(
        get_cf(ticker),
        use_container_width=True
    )

with tabs[4]:
    st.dataframe(
        get_valuation(ticker),
        use_container_width=True
    )