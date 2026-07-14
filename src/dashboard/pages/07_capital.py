import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Capital Allocation Map",
    layout="wide"
)

st.title("💰 Capital Allocation Map")


@st.cache_data(ttl=600)
def load_data():

    return pd.read_csv(
        "output/capital_allocation.csv"
    )


df = load_data()

st.markdown("---")

# --------------------------------------------------
# Latest Year
# --------------------------------------------------

latest_year = sorted(
    df["year"].unique()
)[-1]

latest = df[
    df["year"] == latest_year
]

# --------------------------------------------------
# Treemap
# --------------------------------------------------

treemap = (

    latest.groupby(
        [
            "pattern_label",
            "company_id"
        ]
    )

    .size()

    .reset_index(name="count")

)

fig = px.treemap(

    treemap,

    path=[

        "pattern_label",

        "company_id"

    ],

    values="count",

    color="pattern_label",

    height=700

)

st.plotly_chart(
    fig,
    width="stretch"
)

st.markdown("---")

# --------------------------------------------------
# Pattern Selector
# --------------------------------------------------

patterns = sorted(
    latest["pattern_label"].unique()
)

selected = st.selectbox(

    "Capital Allocation Pattern",

    patterns

)

companies = latest[
    latest["pattern_label"] == selected
]

st.subheader(selected)

st.write(

    f"{len(companies)} companies"

)

st.dataframe(

    companies[

        [

            "company_id",

            "year",

            "cfo_sign",

            "cfi_sign",

            "cff_sign"

        ]

    ],

    width="stretch",

    hide_index=True

)

st.success(
    "Capital allocation map loaded successfully."
)