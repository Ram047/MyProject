import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


DB_PATH = "database/stock_analysis.db"
CONFIG_PATH = "screener_config.yaml"


# ============================================================
# 15 SUPPORTED FILTERS
# ============================================================

FILTER_MAP = {
    "roe_min": ("return_on_equity_pct", ">="),
    "debt_to_equity_max": ("debt_to_equity", "<="),
    "fcf_min": ("free_cash_flow_cr", ">="),
    "revenue_cagr_5yr_min": ("revenue_cagr_5yr", ">="),
    "pat_cagr_5yr_min": ("pat_cagr_5yr", ">="),
    "opm_min": ("operating_profit_margin_pct", ">="),
    "pe_max": ("pe_ratio", "<="),
    "pb_max": ("pb_ratio", "<="),
    "dividend_yield_min": ("dividend_yield_pct", ">="),
    "icr_min": ("effective_icr", ">="),
    "market_cap_min": ("market_cap_crore", ">="),
    "net_profit_min": ("net_profit", ">="),
    "eps_cagr_min": ("eps_cagr_5yr", ">="),
    "asset_turnover_min": ("asset_turnover", ">="),
    "sales_min": ("sales", ">="),
}


# ============================================================
# LOAD YAML CONFIGURATION
# ============================================================

def load_config(config_path=CONFIG_PATH):

    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        config = yaml.safe_load(file)

    if config is None:
        config = {}

    config.setdefault(
        "filters",
        {}
    )

    config.setdefault(
        "sort_by",
        "composite_quality_score"
    )

    config.setdefault(
        "sort_ascending",
        False
    )

    return config


# ============================================================
# LOAD SCREENER DATAFRAME
# ============================================================

def load_screener_dataframe(
    db_path=DB_PATH
):

    conn = sqlite3.connect(
        db_path
    )

    try:

        # ----------------------------------------------------
        # OFFICIAL COMPANY UNIVERSE
        # ----------------------------------------------------

        companies = pd.read_sql_query(
            """
            SELECT
                id AS company_id
            FROM companies
            """,
            conn
        )

        # ----------------------------------------------------
        # FINANCIAL RATIOS
        # ----------------------------------------------------

        ratios = pd.read_sql_query(
            """
            SELECT *
            FROM financial_ratios
            """,
            conn
        )

        # ----------------------------------------------------
        # SECTOR DATA
        # ----------------------------------------------------

        sectors = pd.read_sql_query(
            """
            SELECT
                company_id,
                broad_sector
            FROM sectors
            """,
            conn
        )

        # ----------------------------------------------------
        # PROFIT & LOSS DATA
        # ----------------------------------------------------

        pnl = pd.read_sql_query(
            """
            SELECT
                company_id,
                year,
                sales,
                net_profit
            FROM profitandloss
            """,
            conn
        )

        # ----------------------------------------------------
        # MARKET DATA
        # ----------------------------------------------------

        market = pd.read_sql_query(
            """
            SELECT
                company_id,
                year,
                market_cap_crore,
                pe_ratio,
                pb_ratio,
                dividend_yield_pct
            FROM market_cap
            """,
            conn
        )

    finally:

        conn.close()


    # ========================================================
    # RESTRICT TO OFFICIAL COMPANY UNIVERSE
    # ========================================================

    companies = companies.drop_duplicates(
        subset=["company_id"]
    )

    ratios = ratios.merge(
        companies,
        on="company_id",
        how="inner"
    )


    # ========================================================
    # NORMALIZE YEARS
    # ========================================================

    ratios["year_num"] = pd.to_numeric(
        ratios["year"],
        errors="coerce"
    )


    pnl["year_num"] = pd.to_numeric(
        pnl["year"]
        .astype(str)
        .str.extract(
            r"((?:19|20)\d{2})"
        )[0],
        errors="coerce"
    )


    market["year_num"] = pd.to_numeric(
        market["year"],
        errors="coerce"
    )


    # ========================================================
    # REMOVE DUPLICATE SOURCE RECORDS
    # ========================================================

    pnl = pnl.drop_duplicates(
        subset=[
            "company_id",
            "year_num"
        ],
        keep="last"
    )


    market = market.drop_duplicates(
        subset=[
            "company_id",
            "year_num"
        ],
        keep="last"
    )


    sectors = sectors.drop_duplicates(
        subset=["company_id"],
        keep="last"
    )


    # ========================================================
    # KEEP LATEST RATIO RECORD FOR EACH COMPANY
    # ========================================================

    ratios = (
        ratios
        .dropna(
            subset=["year_num"]
        )
        .sort_values(
            [
                "company_id",
                "year_num"
            ]
        )
        .groupby(
            "company_id",
            as_index=False
        )
        .tail(1)
    )


    # ========================================================
    # MERGE SECTOR DATA
    # ========================================================

    df = ratios.merge(
        sectors,
        on="company_id",
        how="left"
    )


    # ========================================================
    # MERGE PROFIT & LOSS DATA
    # ========================================================

    df = df.merge(
        pnl[
            [
                "company_id",
                "year_num",
                "sales",
                "net_profit"
            ]
        ],
        on=[
            "company_id",
            "year_num"
        ],
        how="left"
    )


    # ========================================================
    # MERGE MARKET DATA
    # ========================================================

    df = df.merge(
        market[
            [
                "company_id",
                "year_num",
                "market_cap_crore",
                "pe_ratio",
                "pb_ratio",
                "dividend_yield_pct"
            ]
        ],
        on=[
            "company_id",
            "year_num"
        ],
        how="left"
    )


    # ========================================================
    # DEBT-FREE ICR HANDLING
    # ========================================================

    df["effective_icr"] = df[
        "interest_coverage"
    ]


    debt_free_mask = (
        df["total_debt_cr"]
        .fillna(0)
        == 0
    )


    df.loc[
        debt_free_mask,
        "effective_icr"
    ] = np.inf


    return df


# ============================================================
# APPLY ONE FILTER
# ============================================================

def apply_filter(
    df,
    filter_name,
    threshold
):

    if filter_name not in FILTER_MAP:

        raise ValueError(
            f"Unsupported filter: {filter_name}"
        )


    column, operator = FILTER_MAP[
        filter_name
    ]


    if column not in df.columns:

        raise KeyError(
            f"Required column not found: {column}"
        )


    # ========================================================
    # FINANCIALS D/E CARVE-OUT
    # ========================================================

    if filter_name == "debt_to_equity_max":

        financials_mask = (
            df["broad_sector"]
            .fillna("")
            .str.strip()
            .str.lower()
            == "financials"
        )


        normal_pass_mask = (

            df[column].notna()

            &

            (
                df[column]
                <= threshold
            )

        )


        return df[
            financials_mask
            |
            normal_pass_mask
        ].copy()


    # ========================================================
    # MINIMUM FILTER
    # ========================================================

    if operator == ">=":

        mask = (

            df[column].notna()

            &

            (
                df[column]
                >= threshold
            )

        )


    # ========================================================
    # MAXIMUM FILTER
    # ========================================================

    elif operator == "<=":

        mask = (

            df[column].notna()

            &

            (
                df[column]
                <= threshold
            )

        )


    else:

        raise ValueError(
            f"Unknown operator: {operator}"
        )


    return df[
        mask
    ].copy()


# ============================================================
# RUN SCREENER
# ============================================================

def run_screener(
    db_path=DB_PATH,
    config_path=CONFIG_PATH
):

    config = load_config(
        config_path
    )


    df = load_screener_dataframe(
        db_path
    )


    print(
        "=" * 65
    )

    print(
        "DAY 15 - SCREENER FILTER ENGINE"
    )

    print(
        "=" * 65
    )


    print(
        f"\nStarting companies: {len(df)}"
    )


    filters = config.get(
        "filters",
        {}
    )


    # ========================================================
    # APPLY ACTIVE FILTERS
    # ========================================================

    for (
        filter_name,
        threshold
    ) in filters.items():


        if threshold is None:

            continue


        before = len(df)


        df = apply_filter(
            df,
            filter_name,
            threshold
        )


        after = len(df)


        print(

            f"{filter_name}: "
            f"{before} -> {after}"

        )


    # ========================================================
    # SORT RESULTS
    # ========================================================

    sort_by = config.get(
        "sort_by",
        "composite_quality_score"
    )


    ascending = config.get(
        "sort_ascending",
        False
    )


    if sort_by not in df.columns:

        raise KeyError(
            f"Sort column not found: {sort_by}"
        )


    df = df.sort_values(

        by=sort_by,

        ascending=ascending,

        na_position="last"

    )


    df = df.reset_index(
        drop=True
    )


    print(
        f"\nFinal result count: {len(df)}"
    )


    return df


# ============================================================
# MAIN
# ============================================================

def main():

    result = run_screener()


    display_columns = [

        "company_id",

        "year",

        "broad_sector",

        "return_on_equity_pct",

        "debt_to_equity",

        "free_cash_flow_cr",

        "revenue_cagr_5yr",

        "pat_cagr_5yr",

        "composite_quality_score",

    ]


    display_columns = [

        column

        for column in display_columns

        if column in result.columns

    ]


    print(
        "\nTop Screener Results:\n"
    )


    if result.empty:

        print(
            "No companies matched the active filters."
        )


    else:

        print(

            result[
                display_columns
            ]

            .head(20)

            .to_string(
                index=False
            )

        )


if __name__ == "__main__":

    main()