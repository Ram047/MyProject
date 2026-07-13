import streamlit as st

from src.dashboard.utils.db import (
    get_sectors,
    get_peers
)

st.set_page_config(layout="wide")

st.title("👥 Peer Analysis")

sector_df = get_sectors()

groups = sorted(
    sector_df.sub_sector.unique().tolist()
)

group = st.selectbox(
    "Peer Group",
    groups
)

peer_df = get_peers(group)

st.write(
    f"Companies: {len(peer_df)}"
)

st.dataframe(
    peer_df,
    use_container_width=True
)