import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(
    page_title="Sector Analysis",
    layout="wide"
)

DB_PATH = "database/stock_analysis.db"


# --------------------------------------------------
# Database
# --------------------------------------------------

@st.cache_data(ttl=600)
def load_sector_data():

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT

        fr.company_id,

        c.company_name,

        s.broad_sector,

        s.sub_sector,

        pl.sales,

        fr.return_on_equity_pct,

        mc.market_cap_crore,

        fr.composite_quality_score,

        fr.debt_to_equity,

        fr.revenue_cagr_5yr,

        fr.net_profit_margin_pct

    FROM financial_ratios fr

    LEFT JOIN companies c
        ON fr.company_id = c.id

    LEFT JOIN sectors s
        ON fr.company_id = s.company_id

    LEFT JOIN profitandloss pl
        ON fr.company_id = pl.company_id
        AND fr.year = pl.year

    LEFT JOIN market_cap mc
        ON fr.company_id = mc.company_id
        AND fr.year = mc.year

    WHERE fr.year = 2024
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


df = load_sector_data()

st.title("🏭 Sector Analysis")

sector = st.selectbox(

    "Select Sector",

    sorted(df["broad_sector"].dropna().unique())

)

sector_df = df[
    df["broad_sector"] == sector
]

if sector_df.empty:

    st.warning("No companies available.")

    st.stop()
    st.markdown("---")

st.subheader("Sector Bubble Chart")

fig = px.scatter(

    sector_df,

    x="sales",

    y="return_on_equity_pct",

    size="market_cap_crore",

    color="sub_sector",

    hover_name="company_name",

    text="company_id",

    height=650

)

fig.update_traces(

    textposition="top center"

)

fig.update_layout(

    xaxis_title="Revenue (₹ Crore)",

    yaxis_title="ROE (%)"

)

st.plotly_chart(

    fig,

    width="stretch"

)
st.markdown("---")

st.subheader("Sector Median KPIs")

median = (

    sector_df[

        [

            "return_on_equity_pct",

            "debt_to_equity",

            "revenue_cagr_5yr",

            "net_profit_margin_pct",

            "composite_quality_score"

        ]

    ]

    .median()

)

bar = px.bar(

    x=[

        "ROE",

        "Debt/Equity",

        "Revenue CAGR",

        "Net Profit Margin",

        "Composite Score"

    ],

    y=median.values,

    text=median.round(2),

    height=450

)

bar.update_layout(

    yaxis_title="Median Value"

)

st.plotly_chart(

    bar,

    width="stretch"

)

st.success(

    f"{len(sector_df)} companies in {sector}"

)