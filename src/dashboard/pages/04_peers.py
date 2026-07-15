import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go

st.set_page_config(
    page_title="Peer Comparison",
    layout="wide"
)

DB_PATH = "database/stock_analysis.db"


# --------------------------------------------------
# Database Helpers
# --------------------------------------------------

@st.cache_data(ttl=600)
def load_peer_groups():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT DISTINCT peer_group_name
        FROM peer_groups
        ORDER BY peer_group_name
        """,
        conn
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def load_peer_companies(group):

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT

        pg.company_id,

        c.company_name,

        pg.is_benchmark,

        fr.return_on_equity_pct,

        c.roce_percentage,

        fr.net_profit_margin_pct,

        fr.debt_to_equity,

        fr.free_cash_flow_cr,

        fr.pat_cagr_5yr,

        fr.revenue_cagr_5yr,

        fr.composite_quality_score

    FROM peer_groups pg

    LEFT JOIN companies c
        ON pg.company_id=c.id

    LEFT JOIN financial_ratios fr
        ON pg.company_id=fr.company_id

    WHERE

        pg.peer_group_name=?
        AND fr.year=2024
    """

    df = pd.read_sql(
        query,
        conn,
        params=[group]
    )

    conn.close()

    return df


# --------------------------------------------------
# Page
# --------------------------------------------------

st.title("👥 Peer Comparison")

groups = load_peer_groups()

peer_group = st.selectbox(
    "Peer Group",
    groups["peer_group_name"]
)

peer_df = load_peer_companies(peer_group)

if peer_df.empty:

    st.warning(
        "No companies available."
    )

    st.stop()

selected_company = st.selectbox(
    "Company",
    peer_df.company_id
)

company = peer_df[
    peer_df.company_id == selected_company
].iloc[0]
# --------------------------------------------------
# Radar Chart
# --------------------------------------------------

st.markdown("---")

st.subheader("Radar Comparison")

metrics = [

    "return_on_equity_pct",

    "roce_percentage",

    "net_profit_margin_pct",

    "debt_to_equity",

    "free_cash_flow_cr",

    "pat_cagr_5yr",

    "revenue_cagr_5yr",

    "composite_quality_score"

]

labels = [

    "ROE",

    "ROCE",

    "NPM",

    "D/E",

    "FCF",

    "PAT CAGR",

    "Revenue CAGR",

    "Composite"

]

peer_avg = peer_df[metrics].mean()

company_values = [
    company[m]
    for m in metrics
]

peer_values = [
    peer_avg[m]
    for m in metrics
]

fig = go.Figure()

fig.add_trace(

    go.Scatterpolar(

        r=company_values,

        theta=labels,

        fill="toself",

        name=company.company_id

    )

)

fig.add_trace(

    go.Scatterpolar(

        r=peer_values,

        theta=labels,

        fill="toself",

        name="Peer Average"

    )

)

fig.update_layout(

    polar=dict(

        radialaxis=dict(

            visible=True

        )

    ),

    showlegend=True,

    height=600

)

st.plotly_chart(
    fig,
    width="stretch"
)

# --------------------------------------------------
# KPI Table
# --------------------------------------------------

st.markdown("---")

st.subheader("Peer Group Comparison")

display = peer_df[
    [

        "company_id",

        "company_name",

        "is_benchmark",

        "return_on_equity_pct",

        "roce_percentage",

        "net_profit_margin_pct",

        "debt_to_equity",

        "free_cash_flow_cr",

        "pat_cagr_5yr",

        "revenue_cagr_5yr",

        "composite_quality_score"

    ]

].copy()


def highlight_benchmark(row):

    if row["is_benchmark"]:

        return [

            "background-color:#FFD966"

        ] * len(row)

    return [

        ""

    ] * len(row)


styled = (

    display.style

    .apply(

        highlight_benchmark,

        axis=1

    )

    .format({

        "return_on_equity_pct":"{:.2f}",

        "roce_percentage":"{:.2f}",

        "net_profit_margin_pct":"{:.2f}",

        "debt_to_equity":"{:.2f}",

        "free_cash_flow_cr":"{:,.0f}",

        "pat_cagr_5yr":"{:.2f}",

        "revenue_cagr_5yr":"{:.2f}",

        "composite_quality_score":"{:.2f}"

    })

)

st.dataframe(

    styled,

    width="stretch",

    hide_index=True

)

# --------------------------------------------------
# Peer Summary
# --------------------------------------------------

st.markdown("---")

c1, c2, c3 = st.columns(3)

c1.metric(

    "Companies",

    len(peer_df)

)

c2.metric(

    "Average ROE",

    round(

        peer_df["return_on_equity_pct"].mean(),

        2

    )

)

c3.metric(

    "Average Composite Score",

    round(

        peer_df["composite_quality_score"].mean(),

        2

    )

)

st.success(

    "Peer comparison loaded successfully."

)