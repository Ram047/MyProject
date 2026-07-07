import sqlite3
import re

import pandas as pd

from src.screener.engine import load_screener_dataframe


DB_PATH = "database/stock_analysis.db"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def extract_year(value):
    """
    Extract calendar year from values such as:
    Mar 2024
    Dec 2023
    2024
    """

    if pd.isna(value):
        return None

    text = str(value)

    match = re.search(r"(19|20)\d{2}", text)

    if match:
        return int(match.group())

    try:
        return int(float(text))

    except (ValueError, TypeError):
        return None


def calculate_normal_cagr(start_value, end_value, years):
    """
    Calculate CAGR only for positive start and end values.
    """

    if start_value is None or end_value is None:
        return None

    if start_value <= 0 or end_value <= 0:
        return None

    return round(
        (
            (end_value / start_value)
            ** (1 / years)
            - 1
        )
        * 100,
        2
    )


def sort_results(df):
    """
    Sort results by composite quality score.
    """

    if df.empty:
        return df.reset_index(drop=True)

    return (
        df
        .sort_values(
            "composite_quality_score",
            ascending=False,
            na_position="last"
        )
        .reset_index(drop=True)
    )


# ============================================================
# PRESET 1 — QUALITY COMPOUNDER
# ============================================================

def quality_compounder(df):
    """
    ROE > 15%
    D/E < 1
    FCF > 0
    Revenue CAGR 5yr > 10%

    Financials companies are exempt from D/E threshold,
    consistent with the Day 15 engine rule.
    """

    financials = (
        df["broad_sector"]
        .fillna("")
        .str.lower()
        .eq("financials")
    )

    result = df[
        (df["return_on_equity_pct"] > 15)
        &
        (
            financials
            |
            (df["debt_to_equity"] < 1.0)
        )
        &
        (df["free_cash_flow_cr"] > 0)
        &
        (df["revenue_cagr_5yr"] > 10)
    ].copy()

    return sort_results(result)


# ============================================================
# PRESET 2 — VALUE PICK
# ============================================================

def value_pick(df):
    """
    P/E < 20
    P/B < 3
    D/E < 2
    Dividend Yield > 1%

    Financials companies are exempt from D/E threshold.
    """

    financials = (
        df["broad_sector"]
        .fillna("")
        .str.lower()
        .eq("financials")
    )

    result = df[
        (df["pe_ratio"] < 20)
        &
        (df["pb_ratio"] < 3.0)
        &
        (
            financials
            |
            (df["debt_to_equity"] < 2.0)
        )
        &
        (df["dividend_yield_pct"] > 1)
    ].copy()

    return sort_results(result)


# ============================================================
# PRESET 3 — GROWTH ACCELERATOR
# ============================================================

def growth_accelerator(df):
    """
    PAT CAGR 5yr > 20%
    Revenue CAGR 5yr > 15%
    D/E < 2

    Financials companies are exempt from D/E threshold.
    """

    financials = (
        df["broad_sector"]
        .fillna("")
        .str.lower()
        .eq("financials")
    )

    result = df[
        (df["pat_cagr_5yr"] > 20)
        &
        (df["revenue_cagr_5yr"] > 15)
        &
        (
            financials
            |
            (df["debt_to_equity"] < 2.0)
        )
    ].copy()

    return sort_results(result)


# ============================================================
# PRESET 4 — DIVIDEND CHAMPION
# ============================================================

def dividend_champion(df):
    """
    Dividend Yield > 2%
    Dividend Payout < 80%
    FCF > 0
    """

    result = df[
        (df["dividend_yield_pct"] > 2)
        &
        (df["dividend_payout_ratio_pct"] < 80)
        &
        (df["free_cash_flow_cr"] > 0)
    ].copy()

    return sort_results(result)


# ============================================================
# PRESET 5 — DEBT-FREE BLUE CHIP
# ============================================================

def debt_free_blue_chip(df):
    """
    D/E = 0
    ROE > 12%
    Revenue > 5000 Crore
    """

    result = df[
        (df["debt_to_equity"] == 0)
        &
        (df["return_on_equity_pct"] > 12)
        &
        (df["sales"] > 5000)
    ].copy()

    return sort_results(result)


# ============================================================
# TURNAROUND HISTORICAL DATA
# ============================================================

def build_turnaround_metrics(db_path=DB_PATH):
    """
    Build:
    - Revenue CAGR 3yr
    - Previous-year D/E
    - D/E declining YoY
    """

    conn = sqlite3.connect(db_path)

    try:

        pnl = pd.read_sql_query(
            """
            SELECT
                company_id,
                year,
                sales
            FROM profitandloss
            """,
            conn
        )

        ratios = pd.read_sql_query(
            """
            SELECT
                company_id,
                year,
                debt_to_equity
            FROM financial_ratios
            """,
            conn
        )

    finally:
        conn.close()

    # --------------------------------------------------------
    # NORMALIZE P&L YEARS
    # --------------------------------------------------------

    pnl["year_num"] = pnl["year"].apply(
        extract_year
    )

    pnl = (
        pnl
        .dropna(subset=["year_num"])
        .drop_duplicates(
            subset=["company_id", "year_num"],
            keep="last"
        )
    )

    pnl["year_num"] = pnl[
        "year_num"
    ].astype(int)

    # --------------------------------------------------------
    # NORMALIZE RATIO YEARS
    # --------------------------------------------------------

    ratios["year_num"] = pd.to_numeric(
        ratios["year"],
        errors="coerce"
    )

    ratios = (
        ratios
        .dropna(subset=["year_num"])
        .drop_duplicates(
            subset=["company_id", "year_num"],
            keep="last"
        )
    )

    ratios["year_num"] = ratios[
        "year_num"
    ].astype(int)

    # --------------------------------------------------------
    # CALCULATE 3-YEAR REVENUE CAGR
    # --------------------------------------------------------

    revenue_records = []

    for company_id, group in pnl.groupby(
        "company_id"
    ):

        group = group.sort_values(
            "year_num"
        )

        latest = group.iloc[-1]

        latest_year = int(
            latest["year_num"]
        )

        target_year = latest_year - 3

        old = group[
            group["year_num"] == target_year
        ]

        if old.empty:
            cagr_3yr = None

        else:
            cagr_3yr = calculate_normal_cagr(
                old.iloc[-1]["sales"],
                latest["sales"],
                3
            )

        revenue_records.append(
            {
                "company_id": company_id,
                "revenue_cagr_3yr": cagr_3yr
            }
        )

    revenue_df = pd.DataFrame(
        revenue_records
    )

    # --------------------------------------------------------
    # CALCULATE D/E YOY DECLINE
    # --------------------------------------------------------

    de_records = []

    for company_id, group in ratios.groupby(
        "company_id"
    ):

        group = group.sort_values(
            "year_num"
        )

        if len(group) < 2:
            continue

        latest = group.iloc[-1]
        previous = group.iloc[-2]

        latest_de = latest[
            "debt_to_equity"
        ]

        previous_de = previous[
            "debt_to_equity"
        ]

        if (
            pd.isna(latest_de)
            or
            pd.isna(previous_de)
        ):
            declining = False

        else:
            declining = (
                latest_de < previous_de
            )

        de_records.append(
            {
                "company_id": company_id,
                "previous_debt_to_equity":
                    previous_de,

                "debt_to_equity_declining":
                    declining
            }
        )

    de_df = pd.DataFrame(
        de_records
    )

    historical = revenue_df.merge(
        de_df,
        on="company_id",
        how="left"
    )

    return historical


# ============================================================
# PRESET 6 — TURNAROUND WATCH
# ============================================================

def turnaround_watch(df, db_path=DB_PATH):
    """
    Revenue CAGR 3yr > 10%
    Latest FCF > 0
    D/E declining YoY
    """

    historical = build_turnaround_metrics(
        db_path
    )

    temp = df.merge(
        historical,
        on="company_id",
        how="left"
    )

    result = temp[
        (temp["revenue_cagr_3yr"] > 10)
        &
        (temp["free_cash_flow_cr"] > 0)
        &
        (
            temp["debt_to_equity_declining"]
            == True
        )
    ].copy()

    return sort_results(result)


# ============================================================
# RUN ALL PRESETS
# ============================================================

PRESETS = {
    "Quality Compounder":
        quality_compounder,

    "Value Pick":
        value_pick,

    "Growth Accelerator":
        growth_accelerator,

    "Dividend Champion":
        dividend_champion,

    "Debt-Free Blue Chip":
        debt_free_blue_chip,

    "Turnaround Watch":
        turnaround_watch,
}


def run_all_presets(db_path=DB_PATH):

    print("=" * 70)
    print("DAY 16 - SIX PRESET SCREENERS")
    print("=" * 70)

    df = load_screener_dataframe(
        db_path
    )

    print(
        f"\nFull universe: {len(df)} companies"
    )

    results = {}

    for name, preset_function in PRESETS.items():

        if name == "Turnaround Watch":

            result = preset_function(
                df,
                db_path
            )

        else:

            result = preset_function(df)

        results[name] = result

        count = len(result)

        if 5 <= count <= 50:
            status = "PASS"
        else:
            status = "REVIEW"

        print(
            f"{name:<25} "
            f"{count:>3} companies  "
            f"[{status}]"
        )

    return results


def main():

    results = run_all_presets()

    print("\n" + "=" * 70)
    print("PRESET RESULT PREVIEW")
    print("=" * 70)

    for name, result in results.items():

        print(f"\n{name}")
        print("-" * 70)

        if result.empty:

            print(
                "No companies matched."
            )

            continue

        columns = [
            "company_id",
            "return_on_equity_pct",
            "debt_to_equity",
            "revenue_cagr_5yr",
            "pat_cagr_5yr",
            "free_cash_flow_cr",
            "composite_quality_score",
        ]

        if name == "Turnaround Watch":
            columns.append(
                "revenue_cagr_3yr"
            )

        columns = [
            column
            for column in columns
            if column in result.columns
        ]

        print(
            result[
                columns
            ]
            .head(10)
            .to_string(index=False)
        )


if __name__ == "__main__":
    main()