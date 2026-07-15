import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go

st.set_page_config(
    page_title="Company Profile",
    layout="wide"
)

DB_PATH = "database/stock_analysis.db"


# --------------------------------------------------
# Database Helpers
# --------------------------------------------------

@st.cache_data(ttl=600)
def load_company_master():

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT

        c.id,
        c.company_name,
        c.about_company,
        c.website,
        c.roce_percentage,
        c.roe_percentage,

        s.broad_sector,
        s.sub_sector

    FROM companies c

    LEFT JOIN sectors s
        ON c.id=s.company_id

    ORDER BY c.company_name
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


@st.cache_data(ttl=600)
def load_latest_ratios(company):

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT

        fr.*,
        c.roce_percentage

    FROM financial_ratios fr

    LEFT JOIN companies c
        ON fr.company_id=c.id

    WHERE fr.company_id=?

    ORDER BY CAST(fr.year AS INTEGER) DESC

    LIMIT 1
    """

    df = pd.read_sql(
        query,
        conn,
        params=[company]
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def load_profit_history(company):

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT

        year,
        sales,
        net_profit

    FROM profitandloss

    WHERE company_id=?

    ORDER BY CAST(year AS INTEGER)
    """

    df = pd.read_sql(
        query,
        conn,
        params=[company]
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def load_ratio_history(company):

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT

        year,
        return_on_equity_pct

    FROM financial_ratios

    WHERE company_id=?

    ORDER BY CAST(year AS INTEGER)
    """

    df = pd.read_sql(
        query,
        conn,
        params=[company]
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def load_pros_cons(company):

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        pros,
        cons

    FROM prosandcons

    WHERE company_id=?
    """

    df = pd.read_sql(
        query,
        conn,
        params=[company]
    )

    conn.close()

    return df


# --------------------------------------------------
# Company Search
# --------------------------------------------------

companies = load_company_master()

st.title("🏢 Company Profile")

search = st.text_input(
    "Search by Company Name or Ticker"
)

companies["search_text"] = (
    companies["company_name"] + " (" + companies["id"] + ")"
)

company_names = companies["search_text"].tolist()

if search:

    matches = [

        c for c in company_names

        if search.lower() in c.lower()

    ]

else:

    matches = company_names


if len(matches) == 0:

    st.warning(
        "Ticker not found — please try another."
    )

    st.stop()


selected_company = st.selectbox(

    "Company",

    matches

)

company = companies[
    companies["search_text"] == selected_company
].iloc[0]

ticker = company["id"]

latest = load_latest_ratios(ticker)

if latest.empty:

    st.error(
        "Financial data unavailable."
    )

    st.stop()

latest = latest.iloc[0]

# --------------------------------------------------
# Company Card
# --------------------------------------------------

st.markdown("---")

left, right = st.columns([3, 1])

with left:

    st.subheader(company.company_name)

    st.write(f"**Ticker:** {ticker}")

    st.write(f"**Sector:** {company.broad_sector}")

    st.write(f"**Sub-sector:** {company.sub_sector}")

    if pd.notna(company.website):
        st.write(f"**Website:** {company.website}")

    st.markdown("### About")

    if pd.notna(company.about_company):
        st.write(company.about_company)
    else:
        st.info("Company description not available.")

with right:

    st.metric(
        "Latest Year",
        latest.year
    )

    st.metric(
        "Composite Score",
        round(
            latest.composite_quality_score,
            2
        )
    )

st.markdown("---")

# --------------------------------------------------
# KPI Tiles
# --------------------------------------------------

st.subheader("Key Financial Metrics")

k1, k2, k3 = st.columns(3)
k4, k5, k6 = st.columns(3)

k1.metric(
    "ROE",
    f"{latest.return_on_equity_pct:.2f}%"
)

k2.metric(
    "ROCE",
    f"{company.roce_percentage:.2f}%"
)

k3.metric(
    "Net Profit Margin",
    f"{latest.net_profit_margin_pct:.2f}%"
)

k4.metric(
    "Debt / Equity",
    round(
        latest.debt_to_equity,
        2
    )
)

k5.metric(
    "Revenue CAGR (5Y)",
    f"{latest.revenue_cagr_5yr:.2f}%"
)

k6.metric(
    "Free Cash Flow",
    f"₹ {latest.free_cash_flow_cr:,.0f} Cr"
)

st.markdown("---")

# --------------------------------------------------
# Revenue & Net Profit Chart
# --------------------------------------------------

st.subheader("Revenue & Net Profit (10 Years)")

history = load_profit_history(ticker)

if history.empty:

    st.info(
        "Historical financial data not available."
    )

else:

    fig = go.Figure()

    fig.add_bar(
        x=history["year"],
        y=history["sales"],
        name="Revenue"
    )

    fig.add_bar(
        x=history["year"],
        y=history["net_profit"],
        name="Net Profit"
    )

    fig.update_layout(

        barmode="group",

        height=500,

        xaxis_title="Year",

        yaxis_title="₹ Crore",

        legend_title="Metric"

    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

st.markdown("---")

# --------------------------------------------------
# ROE & ROCE Trend
# --------------------------------------------------

st.subheader("ROE & ROCE Trend")

ratio_history = load_ratio_history(ticker)

if ratio_history.empty:

    st.info(
        "Historical ratio data not available."
    )

else:

    roce_series = [company.roce_percentage] * len(ratio_history)

    fig = go.Figure()

    fig.add_trace(

        go.Scatter(

            x=ratio_history["year"],

            y=ratio_history["return_on_equity_pct"],

            mode="lines+markers",

            name="ROE",

            line=dict(width=3)

        )

    )

    fig.add_trace(

        go.Scatter(

            x=ratio_history["year"],

            y=roce_series,

            mode="lines+markers",

            name="ROCE",

            line=dict(dash="dash", width=3),

            yaxis="y2"

        )

    )

    fig.update_layout(

        height=500,

        xaxis_title="Year",

        yaxis=dict(

            title="ROE (%)"

        ),

        yaxis2=dict(

            title="ROCE (%)",

            overlaying="y",

            side="right"

        ),

        legend=dict(

            orientation="h"

        )

    )

    st.plotly_chart(

        fig,

        width="stretch"

    )

st.markdown("---")


# --------------------------------------------------
# Pros & Cons
# --------------------------------------------------

st.subheader("Pros & Cons")

pc = load_pros_cons(ticker)

left, right = st.columns(2)

with left:

    st.success("Pros")

    if pc.empty:

        st.write("No pros available.")

    else:

        pros = str(pc.iloc[0]["pros"])

        if pros.strip():

            for item in pros.split(";"):

                item = item.strip()

                if item:

                    st.markdown(f"✅ {item}")

        else:

            st.write("No pros available.")

with right:

    st.error("Cons")

    if pc.empty:

        st.write("No cons available.")

    else:

        cons = str(pc.iloc[0]["cons"])

        if cons.strip():

            for item in cons.split(";"):

                item = item.strip()

                if item:

                    st.markdown(f"❌ {item}")

        else:

            st.write("No cons available.")


st.markdown("---")

st.success("Company profile loaded successfully.")