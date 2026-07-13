import streamlit as st

from src.dashboard.utils.db import get_sectors

st.set_page_config(layout="wide")

st.title("🏭 Sector Analysis")

df = get_sectors()

sector = st.selectbox(
    "Broad Sector",
    sorted(df["broad_sector"].unique())
)

filtered = df[
    df["broad_sector"] == sector
]

st.metric(
    "Companies",
    len(filtered)
)

st.dataframe(
    filtered,
    use_container_width=True
)