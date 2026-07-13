import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("💰 Capital Allocation")

try:

    df = pd.read_csv(
        "output/capital_allocation.csv"
    )

    st.success(
        f"{len(df)} records loaded."
    )

    st.dataframe(
        df,
        use_container_width=True
    )

except Exception:

    st.warning(
        "capital_allocation.csv not found."
    )