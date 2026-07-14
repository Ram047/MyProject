import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(
    page_title="Annual Reports",
    layout="wide"
)

DB_PATH = "database/stock_analysis.db"


# --------------------------------------------------
# Database
# --------------------------------------------------

@st.cache_data(ttl=600)
def load_reports():

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT

        d.company_id,

        c.company_name,

        d.year,

        d.annual_report

    FROM documents d

    LEFT JOIN companies c
        ON d.company_id=c.id

    ORDER BY
        c.company_name,
        d.year DESC
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


reports = load_reports()

st.title("📄 Annual Reports")

reports["display"] = (

    reports["company_name"]

    + " ("

    + reports["company_id"]

    + ")"

)

search = st.text_input(
    "Search Company"
)

if search:

    matches = [

        x for x in reports["display"].unique()

        if search.lower() in x.lower()

    ]

else:

    matches = sorted(

        reports["display"].unique()

    )

if len(matches) == 0:

    st.warning(
        "Ticker not found."
    )

    st.stop()

selected = st.selectbox(

    "Company",

    matches

)

company_reports = reports[
    reports["display"] == selected
]

st.markdown("---")

st.subheader("Available Annual Reports")

for _, row in company_reports.iterrows():

    year = row["year"]

    url = row["annual_report"]

    col1, col2 = st.columns([1,5])

    with col1:

        st.write(year)

    with col2:

        if pd.isna(url) or str(url).strip() == "":

            st.markdown(

                "<span style='color:white;background:red;padding:4px;'>Report Unavailable</span>",

                unsafe_allow_html=True

            )

        else:

            st.markdown(

                f"[📥 Open Annual Report]({url})"

            )

st.success(
    "Annual reports loaded successfully."
)