import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

st.set_page_config(
    page_title="Nifty 100 Analytics",
    layout="wide"
)

DB_PATH = "database/stock_analysis.db"


@st.cache_data(ttl=600)
def load_home_data(year):

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        fr.company_id,
        fr.year,
        fr.return_on_equity_pct,
        fr.debt_to_equity,
        fr.revenue_cagr_5yr,
        fr.free_cash_flow_cr,
        fr.composite_quality_score,
        mc.pe_ratio,
        s.broad_sector,
        s.sub_sector,
        c.company_name

    FROM financial_ratios fr

    LEFT JOIN market_cap mc
        ON fr.company_id = mc.company_id
        AND fr.year = mc.year

    LEFT JOIN sectors s
        ON fr.company_id = s.company_id

    LEFT JOIN companies c
        ON fr.company_id = c.id

    WHERE fr.year=?
    """

    df = pd.read_sql(query, conn, params=[str(year)])

    conn.close()

    return df


st.sidebar.header("Filters")

selected_year = st.sidebar.selectbox(
    "Financial Year",
    [2024, 2023, 2022, 2021, 2020, 2019],
    index=0
)

df = load_home_data(selected_year)

st.title("📈 Nifty 100 Analytics Dashboard")

st.markdown("---")

avg_roe = round(df["return_on_equity_pct"].mean(), 2)

median_pe = round(df["pe_ratio"].median(), 2)

median_de = round(df["debt_to_equity"].median(), 2)

total_companies = df["company_id"].nunique()

median_revenue = round(
    df["revenue_cagr_5yr"].median(),
    2
)

debt_free = (
    df["debt_to_equity"] == 0
).sum()

c1, c2, c3 = st.columns(3)

c4, c5, c6 = st.columns(3)

c1.metric("Average ROE", f"{avg_roe}%")

c2.metric("Median P/E", median_pe)

c3.metric("Median D/E", median_de)

c4.metric("Total Companies", total_companies)

c5.metric(
    "Median Revenue CAGR",
    f"{median_revenue}%"
)

c6.metric(
    "Debt-Free Companies",
    debt_free
)

st.markdown("---")

left, right = st.columns([1, 1])

with left:

    st.subheader("Sector Breakdown")

    sector = (
        df.groupby("broad_sector")
        .size()
        .reset_index(name="Companies")
    )

    fig = px.pie(
        sector,
        names="broad_sector",
        values="Companies",
        hole=.55
    )

    fig.update_layout(
        height=500
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with right:

    st.subheader(
        "Top 5 Companies by Composite Score"
    )

    top = (
        df.sort_values(
            "composite_quality_score",
            ascending=False
        )
        .head(5)
    )

    st.dataframe(

        top[
            [
                "company_id",
                "company_name",
                "composite_quality_score",
                "return_on_equity_pct",
                "debt_to_equity",
                "revenue_cagr_5yr"
            ]
        ],

        width="stretch"
    )

st.markdown("---")

st.subheader("Dataset Preview")

st.dataframe(
    df,
    width="stretch"
)