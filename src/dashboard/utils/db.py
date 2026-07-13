import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = "database/stock_analysis.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


@st.cache_data(ttl=600)
def get_companies():
    conn = get_connection()

    df = pd.read_sql("""
        SELECT *
        FROM companies
        ORDER BY company_name
    """, conn)

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_ratios(ticker, year=None):

    conn = get_connection()

    query = """
        SELECT *
        FROM financial_ratios
        WHERE company_id=?
    """

    params = [ticker]

    if year is not None:
        query += " AND year=?"
        params.append(year)

    query += " ORDER BY year DESC"

    df = pd.read_sql(
        query,
        conn,
        params=params
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_pl(ticker):

    conn = get_connection()

    df = pd.read_sql("""
        SELECT *
        FROM profitandloss
        WHERE company_id=?
        ORDER BY year DESC
    """,
    conn,
    params=[ticker])

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_bs(ticker):

    conn = get_connection()

    df = pd.read_sql("""
        SELECT *
        FROM balancesheet
        WHERE company_id=?
        ORDER BY year DESC
    """,
    conn,
    params=[ticker])

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_cf(ticker):

    conn = get_connection()

    df = pd.read_sql("""
        SELECT *
        FROM cashflow
        WHERE company_id=?
        ORDER BY year DESC
    """,
    conn,
    params=[ticker])

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_sectors():

    conn = get_connection()

    df = pd.read_sql("""
        SELECT *
        FROM sectors
        ORDER BY broad_sector, sub_sector
    """, conn)

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_peers(group_name):

    conn = get_connection()

    df = pd.read_sql("""
        SELECT *
        FROM peer_groups
        WHERE peer_group_name=?
    """,
    conn,
    params=[group_name])

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_valuation(ticker):

    conn = get_connection()

    df = pd.read_sql("""
        SELECT *
        FROM market_cap
        WHERE company_id=?
        ORDER BY year DESC
    """,
    conn,
    params=[ticker])

    conn.close()

    return df