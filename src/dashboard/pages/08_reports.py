import streamlit as st
import os

st.set_page_config(layout="wide")

st.title("📄 Reports")

files = [
    "output/screener_output.xlsx",
    "output/peer_comparison.xlsx",
    "output/day16_preset_validation.txt",
    "output/ratio_edge_cases.log",
    "output/sprint2_retrospective.md",
    "output/sprint3_retrospective.md",
]

available = []

for file in files:

    if os.path.exists(file):
        available.append(file)

st.subheader("Generated Reports")

for file in available:

    st.success(file)

st.write(
    f"Total reports available: {len(available)}"
)