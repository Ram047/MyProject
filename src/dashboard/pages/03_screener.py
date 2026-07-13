import streamlit as st

from src.screener.presets import run_all_presets

st.set_page_config(layout="wide")

st.title("🔍 Stock Screener")

results = run_all_presets()

preset = st.selectbox(
    "Preset",
    list(results.keys())
)

df = results[preset]

st.success(
    f"{len(df)} companies matched."
)

st.dataframe(
    df,
    use_container_width=True
)