import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go

st.set_page_config(
    page_title="Trend Analysis",
    layout="wide"
)

DB_PATH = "database/stock_analysis.db"


# --------------------------------------------------
# Database Helpers
# --------------------------------------------------

@st.cache_data(ttl=600)
def load_companies():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT
            id,
            company_name
        FROM companies
        ORDER BY company_name
        """,
        conn
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def load_trend_data(company_id):

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT

        fr.year,

        fr.return_on_equity_pct,

        fr.net_profit_margin_pct,

        fr.revenue_cagr_5yr,

        fr.pat_cagr_5yr,

        fr.debt_to_equity,

        fr.interest_coverage,

        fr.free_cash_flow_cr,

        pl.sales,

        pl.net_profit,

        c.roce_percentage

    FROM financial_ratios fr

    LEFT JOIN profitandloss pl
        ON fr.company_id = pl.company_id
        AND fr.year = pl.year

    LEFT JOIN companies c
        ON fr.company_id = c.id

    WHERE fr.company_id = ?

    ORDER BY CAST(fr.year AS INTEGER)
    """

    df = pd.read_sql(
        query,
        conn,
        params=[company_id]
    )

    conn.close()

    return df


# --------------------------------------------------
# Page
# --------------------------------------------------

st.title("📈 Trend Analysis")

companies = load_companies()

companies["display"] = (
    companies["company_name"] +
    " (" +
    companies["id"] +
    ")"
)

search = st.text_input(
    "Search Company"
)

if search:

    options = [

        x for x in companies["display"]

        if search.lower() in x.lower()

    ]

else:

    options = companies["display"].tolist()


if len(options) == 0:

    st.warning(
        "Ticker not found."
    )

    st.stop()

selected = st.selectbox(
    "Company",
    options
)

company = companies[
    companies["display"] == selected
].iloc[0]

trend = load_trend_data(
    company["id"]
)

if trend.empty:

    st.error(
        "No historical data found."
    )

    st.stop()

metric_options = {

    "Revenue":"sales",

    "Net Profit":"net_profit",

    "ROE":"return_on_equity_pct",

    "ROCE":"roce_percentage",

    "Net Profit Margin":"net_profit_margin_pct",

    "Revenue CAGR":"revenue_cagr_5yr",

    "PAT CAGR":"pat_cagr_5yr",

    "Debt to Equity":"debt_to_equity",

    "Interest Coverage":"interest_coverage",

    "Free Cash Flow":"free_cash_flow_cr"

}

selected_metrics = st.multiselect(

    "Select up to 3 Metrics",

    list(metric_options.keys()),

    default=["Revenue"]

)

if len(selected_metrics) > 3:

    st.warning(
        "Maximum 3 metrics allowed."
    )

    st.stop()
    # --------------------------------------------------
# Multi Metric Trend Chart
# --------------------------------------------------

st.markdown("---")

st.subheader("10-Year Trend Analysis")

fig = go.Figure()

for metric_name in selected_metrics:

    column = metric_options[metric_name]

    fig.add_trace(

        go.Scatter(

            x=trend["year"],

            y=trend[column],

            mode="lines+markers",

            name=metric_name

        )

    )

    # -------------------------
    # YoY Annotation
    # -------------------------

    values = trend[column].tolist()

    years = trend["year"].tolist()

    for i in range(1, len(values)):

        prev = values[i - 1]
        curr = values[i]

        if (
            pd.notna(prev)
            and pd.notna(curr)
            and prev != 0
        ):

            yoy = ((curr - prev) / abs(prev)) * 100

            fig.add_annotation(

                x=years[i],

                y=curr,

                text=f"{yoy:.1f}%",

                showarrow=False,

                font=dict(size=9)

            )

fig.update_layout(

    height=600,

    xaxis_title="Year",

    yaxis_title="Value",

    hovermode="x unified",

    legend_title="Metrics"

)

st.plotly_chart(

    fig,

    width="stretch"

)

# --------------------------------------------------
# KPI Summary
# --------------------------------------------------

st.markdown("---")

st.subheader("Latest Year Summary")

latest = trend.iloc[-1]

c1, c2, c3 = st.columns(3)

c4, c5, c6 = st.columns(3)

c1.metric(

    "Revenue",

    f"₹ {latest.sales:,.0f} Cr"

)

c2.metric(

    "Net Profit",

    f"₹ {latest.net_profit:,.0f} Cr"

)

c3.metric(

    "ROE",

    f"{latest.return_on_equity_pct:.2f}%"

)

c4.metric(

    "ROCE",

    f"{latest.roce_percentage:.2f}%"

)

c5.metric(

    "Net Profit Margin",

    f"{latest.net_profit_margin_pct:.2f}%"

)

c6.metric(

    "Free Cash Flow",

    f"₹ {latest.free_cash_flow_cr:,.0f} Cr"

)

# --------------------------------------------------
# Historical Data
# --------------------------------------------------

st.markdown("---")

st.subheader("Historical Financial Data")

display_columns = [

    "year",

    "sales",

    "net_profit",

    "return_on_equity_pct",

    "roce_percentage",

    "net_profit_margin_pct",

    "revenue_cagr_5yr",

    "pat_cagr_5yr",

    "debt_to_equity",

    "interest_coverage",

    "free_cash_flow_cr"

]

st.dataframe(

    trend[display_columns],

    width="stretch",

    hide_index=True

)

st.success(
    "Trend analysis loaded successfully."
)