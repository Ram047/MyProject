import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(
    page_title="Stock Screener",
    layout="wide"
)

DB_PATH = "database/stock_analysis.db"


# --------------------------------------------------
# Database
# --------------------------------------------------

@st.cache_data(ttl=600)
def load_screener():

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT

        fr.company_id,

        c.company_name,

        s.broad_sector,

        fr.return_on_equity_pct,

        fr.debt_to_equity,

        fr.free_cash_flow_cr,

        fr.revenue_cagr_5yr,

        fr.pat_cagr_5yr,

        fr.operating_profit_margin_pct,

        fr.interest_coverage,

        fr.composite_quality_score,

        mc.pe_ratio,

        mc.pb_ratio,

        mc.dividend_yield_pct

    FROM financial_ratios fr

    LEFT JOIN companies c
        ON fr.company_id=c.id

    LEFT JOIN sectors s
        ON fr.company_id=s.company_id

    LEFT JOIN market_cap mc
        ON fr.company_id=mc.company_id
        AND fr.year=mc.year

    WHERE fr.year=2024
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


df = load_screener()

st.title("📊 Stock Screener")

# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.header("Filters")

PRESETS = {

    "Custom": None,

    "Quality": {
        "roe": 15,
        "de": 1,
        "fcf": 0,
        "rev": 10,
        "pat": 0,
        "opm": 0,
        "pe": 1000,
        "pb": 1000,
        "div": 0,
        "icr": 0
    },

    "Value": {
        "roe": 0,
        "de": 2,
        "fcf": -100000,
        "rev": 0,
        "pat": 0,
        "opm": 0,
        "pe": 20,
        "pb": 3,
        "div": 1,
        "icr": 0
    },

    "Growth": {
        "roe": 0,
        "de": 2,
        "fcf": -100000,
        "rev": 15,
        "pat": 20,
        "opm": 0,
        "pe": 1000,
        "pb": 1000,
        "div": 0,
        "icr": 0
    },

    "Dividend": {
        "roe": 0,
        "de": 100,
        "fcf": 0,
        "rev": 0,
        "pat": 0,
        "opm": 0,
        "pe": 1000,
        "pb": 1000,
        "div": 2,
        "icr": 0
    },

    "Debt-Free": {
        "roe": 12,
        "de": 0,
        "fcf": -100000,
        "rev": 0,
        "pat": 0,
        "opm": 0,
        "pe": 1000,
        "pb": 1000,
        "div": 0,
        "icr": 0
    },

    "Turnaround": {
        "roe": 0,
        "de": 100,
        "fcf": 0,
        "rev": 10,
        "pat": 0,
        "opm": 0,
        "pe": 1000,
        "pb": 1000,
        "div": 0,
        "icr": 0
    }

}

preset = st.sidebar.radio(

    "Preset",

    list(PRESETS.keys())

)

values = PRESETS[preset]

if values is None:

    values = {

        "roe":0,
        "de":10,
        "fcf":-100000,
        "rev":0,
        "pat":0,
        "opm":0,
        "pe":1000,
        "pb":1000,
        "div":0,
        "icr":0

    }

roe = st.sidebar.slider(

    "ROE Minimum",

    0.0,

    100.0,

    float(values["roe"])

)

de = st.sidebar.slider(

    "Debt / Equity Maximum",

    0.0,

    10.0,

    float(values["de"])

)

fcf = st.sidebar.slider(

    "Free Cash Flow Minimum",

    -100000,

    100000,

    int(values["fcf"])

)

rev = st.sidebar.slider(

    "Revenue CAGR Minimum",

    0.0,

    50.0,

    float(values["rev"])

)

pat = st.sidebar.slider(

    "PAT CAGR Minimum",

    0.0,

    50.0,

    float(values["pat"])

)

opm = st.sidebar.slider(

    "Operating Margin Minimum",

    0.0,

    80.0,

    float(values["opm"])

)

pe = st.sidebar.slider(

    "P/E Maximum",

    0.0,

    100.0,

    float(min(values["pe"],100))

)

pb = st.sidebar.slider(

    "P/B Maximum",

    0.0,

    20.0,

    float(min(values["pb"],20))

)

dividend = st.sidebar.slider(

    "Dividend Yield Minimum",

    0.0,

    10.0,

    float(values["div"])

)

icr = st.sidebar.slider(

    "Interest Coverage Minimum",

    0.0,

    100.0,

    float(values["icr"])

)
# --------------------------------------------------
# Apply Filters
# --------------------------------------------------

filtered = df.copy()

filtered = filtered[
    (filtered["return_on_equity_pct"] >= roe)
]

filtered = filtered[
    (filtered["debt_to_equity"] <= de)
]

filtered = filtered[
    (filtered["free_cash_flow_cr"] >= fcf)
]

filtered = filtered[
    (filtered["revenue_cagr_5yr"] >= rev)
]

filtered = filtered[
    (filtered["pat_cagr_5yr"] >= pat)
]

filtered = filtered[
    (filtered["operating_profit_margin_pct"] >= opm)
]

filtered = filtered[
    (filtered["pe_ratio"] <= pe)
]

filtered = filtered[
    (filtered["pb_ratio"] <= pb)
]

filtered = filtered[
    (filtered["dividend_yield_pct"] >= dividend)
]

filtered = filtered[
    (filtered["interest_coverage"] >= icr)
]

filtered = filtered.sort_values(
    "composite_quality_score",
    ascending=False
)

# --------------------------------------------------
# Result Count
# --------------------------------------------------

st.markdown("---")

st.subheader(
    f"{len(filtered)} companies match your filters"
)

# --------------------------------------------------
# Results Table
# --------------------------------------------------

columns = [

    "company_id",

    "company_name",

    "broad_sector",

    "composite_quality_score",

    "return_on_equity_pct",

    "debt_to_equity",

    "free_cash_flow_cr",

    "revenue_cagr_5yr",

    "pat_cagr_5yr",

    "operating_profit_margin_pct",

    "pe_ratio",

    "pb_ratio",

    "dividend_yield_pct",

    "interest_coverage"

]

st.dataframe(

    filtered[columns],

    width="stretch",

    hide_index=True

)

# --------------------------------------------------
# CSV Download
# --------------------------------------------------

csv = filtered[columns].to_csv(
    index=False
).encode("utf-8")

st.download_button(

    label="📥 Download CSV",

    data=csv,

    file_name="screener_results.csv",

    mime="text/csv"

)

# --------------------------------------------------
# Summary Metrics
# --------------------------------------------------

st.markdown("---")

c1, c2, c3 = st.columns(3)

c1.metric(
    "Average ROE",
    round(
        filtered["return_on_equity_pct"].mean(),
        2
    ) if len(filtered) else 0
)

c2.metric(
    "Average Composite Score",
    round(
        filtered["composite_quality_score"].mean(),
        2
    ) if len(filtered) else 0
)

c3.metric(
    "Average Revenue CAGR",
    round(
        filtered["revenue_cagr_5yr"].mean(),
        2
    ) if len(filtered) else 0
)

# --------------------------------------------------
# Footer
# --------------------------------------------------

st.caption(
    "Filters update automatically as slider values change."
)