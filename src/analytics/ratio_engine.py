import sqlite3
import re

import pandas as pd

from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    debt_to_equity,
    interest_coverage_ratio,
    asset_turnover,
)

from src.analytics.cashflow import free_cash_flow
from src.analytics.cagr import calculate_cagr


DB_PATH = "database/stock_analysis.db"


# ============================================================
# YEAR NORMALIZATION
# ============================================================

def extract_year(value):
    """
    Convert different year formats to integer year.

    Examples:
    Mar 2024 -> 2024
    Dec 2023 -> 2023
    Mar-24   -> 2024
    2024     -> 2024
    """

    if pd.isna(value):
        return None

    text = str(value).strip()

    # Four-digit year
    match4 = re.search(r"(19|20)\d{2}", text)

    if match4:
        return int(match4.group())

    # Two-digit year
    match2 = re.search(r"(\d{2})$", text)

    if match2:
        year = int(match2.group(1))

        if year < 70:
            return 2000 + year

        return 1900 + year

    try:
        return int(float(text))

    except (ValueError, TypeError):
        return None


# ============================================================
# SAFE VALUE
# ============================================================

def safe_value(value, default=0):
    """
    Replace NaN values with a default value.
    """

    if pd.isna(value):
        return default

    return value


# ============================================================
# HISTORICAL VALUE FOR CAGR
# ============================================================

def get_historical_value(
    dataframe,
    company_id,
    current_year,
    column,
    window=5
):
    """
    Return the exact historical value required for CAGR.

    Example:
    Current year = 2024
    Window = 5
    Target year = 2019
    """

    target_year = current_year - window

    history = dataframe[
        (dataframe["company_id"] == company_id)
        & (dataframe["year_num"] == target_year)
    ]

    if history.empty:
        return None

    value = history.iloc[0][column]

    if pd.isna(value):
        return None

    return value


# ============================================================
# COMPOSITE QUALITY SCORE
# ============================================================

def calculate_quality_score(
    roe,
    npm,
    debt_equity,
    icr,
    turnover
):
    """
    Calculate composite quality score from 0 to 100.
    """

    score = 0

    # ROE: maximum 25 points
    if roe is not None:
        score += min(max(roe, 0), 25) / 25 * 25

    # Net Profit Margin: maximum 20 points
    if npm is not None:
        score += min(max(npm, 0), 20) / 20 * 20

    # Debt-to-Equity: maximum 20 points
    if debt_equity is not None:

        if debt_equity <= 1:
            score += 20

        elif debt_equity <= 2:
            score += 10

    # Interest Coverage: maximum 20 points
    if icr is not None:
        score += min(max(icr, 0), 5) / 5 * 20

    # Asset Turnover: maximum 15 points
    if turnover is not None:
        score += min(max(turnover, 0), 2) / 2 * 15

    return round(score, 2)


# ============================================================
# MAIN RATIO ENGINE
# ============================================================

def main():

    print("=" * 60)
    print("DAY 12 - FINANCIAL RATIO ENGINE")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)

    try:

        # ----------------------------------------------------
        # READ DATABASE TABLES
        # ----------------------------------------------------

        print("\nReading database tables...")

        pnl = pd.read_sql_query(
            "SELECT * FROM profitandloss",
            conn
        )

        bs = pd.read_sql_query(
            "SELECT * FROM balancesheet",
            conn
        )

        cf = pd.read_sql_query(
            "SELECT * FROM cashflow",
            conn
        )

        print(f"Profit & Loss rows : {len(pnl)}")
        print(f"Balance Sheet rows : {len(bs)}")
        print(f"Cash Flow rows      : {len(cf)}")

        # ----------------------------------------------------
        # NORMALIZE YEARS
        # ----------------------------------------------------

        pnl["year_num"] = pnl["year"].apply(extract_year)
        bs["year_num"] = bs["year"].apply(extract_year)
        cf["year_num"] = cf["year"].apply(extract_year)

        # Remove exact duplicate company-year records
        # before merging to prevent many-to-many row expansion.

        pnl = pnl.drop_duplicates(
            subset=["company_id", "year_num"],
            keep="last"
        )

        bs = bs.drop_duplicates(
            subset=["company_id", "year_num"],
            keep="last"
        )

        cf = cf.drop_duplicates(
            subset=["company_id", "year_num"],
            keep="last"
        )

        print("\nAfter company-year deduplication:")
        print(f"Profit & Loss rows : {len(pnl)}")
        print(f"Balance Sheet rows : {len(bs)}")
        print(f"Cash Flow rows      : {len(cf)}")

        # ----------------------------------------------------
        # MERGE P&L + BALANCE SHEET
        # ----------------------------------------------------

        merged = pnl.merge(
            bs,
            on=[
                "company_id",
                "year_num"
            ],
            how="left",
            suffixes=(
                "_pnl",
                "_bs"
            )
        )

        # ----------------------------------------------------
        # MERGE CASH FLOW
        # ----------------------------------------------------

        merged = merged.merge(
            cf[
                [
                    "company_id",
                    "year_num",
                    "operating_activity",
                    "investing_activity",
                    "financing_activity"
                ]
            ],
            on=[
                "company_id",
                "year_num"
            ],
            how="left"
        )

        print(f"\nMerged rows: {len(merged)}")

        # ----------------------------------------------------
        # CLEAR OLD RATIO DATA
        # ----------------------------------------------------

        conn.execute(
            "DELETE FROM financial_ratios"
        )

        conn.commit()

        output_rows = []

        print("\nCalculating KPIs...")

        # ----------------------------------------------------
        # CALCULATE RATIOS
        # ----------------------------------------------------

        for _, row in merged.iterrows():

            company = row["company_id"]

            if pd.isna(row["year_num"]):
                continue

            year = int(row["year_num"])

            # =================================================
            # P&L VALUES
            # =================================================

            sales = safe_value(
                row.get("sales"),
                0
            )

            net_profit = safe_value(
                row.get("net_profit"),
                0
            )

            operating_profit = safe_value(
                row.get("operating_profit"),
                0
            )

            other_income = safe_value(
                row.get("other_income"),
                0
            )

            interest = safe_value(
                row.get("interest"),
                0
            )

            eps = safe_value(
                row.get("eps"),
                None
            )

            dividend_payout = safe_value(
                row.get("dividend_payout"),
                None
            )

            # =================================================
            # BALANCE SHEET VALUES
            # =================================================

            equity_capital = safe_value(
                row.get("equity_capital"),
                0
            )

            reserves = safe_value(
                row.get("reserves"),
                0
            )

            borrowings = safe_value(
                row.get("borrowings"),
                0
            )

            total_assets = safe_value(
                row.get("total_assets"),
                0
            )

            # =================================================
            # CASH FLOW VALUES
            # =================================================

            cfo = safe_value(
                row.get("operating_activity"),
                0
            )

            cfi = safe_value(
                row.get("investing_activity"),
                0
            )

            # =================================================
            # PROFITABILITY RATIOS
            # =================================================

            npm = net_profit_margin(
                net_profit,
                sales
            )

            opm = operating_profit_margin(
                operating_profit,
                sales
            )

            roe = return_on_equity(
                net_profit,
                equity_capital,
                reserves
            )

            # =================================================
            # LEVERAGE RATIOS
            # =================================================

            de_ratio = debt_to_equity(
                borrowings,
                equity_capital,
                reserves
            )

            icr = interest_coverage_ratio(
                operating_profit,
                other_income,
                interest
            )

            # =================================================
            # EFFICIENCY RATIO
            # =================================================

            turnover = asset_turnover(
                sales,
                total_assets
            )

            # =================================================
            # CASH FLOW KPIs
            # =================================================

            fcf = free_cash_flow(
                cfo,
                cfi
            )

            capex = abs(cfi)

            # =================================================
            # BOOK VALUE PER SHARE
            # =================================================

            if equity_capital > 0:

                book_value_per_share = round(
                    (
                        equity_capital
                        + reserves
                    )
                    / equity_capital,
                    2
                )

            else:

                book_value_per_share = None

            # =================================================
            # GET 5-YEAR HISTORICAL VALUES
            # =================================================

            old_sales = get_historical_value(
                pnl,
                company,
                year,
                "sales",
                5
            )

            old_pat = get_historical_value(
                pnl,
                company,
                year,
                "net_profit",
                5
            )

            old_eps = get_historical_value(
                pnl,
                company,
                year,
                "eps",
                5
            )

            # =================================================
            # REVENUE CAGR
            # =================================================

            if old_sales is None:

                revenue_cagr = None
                revenue_flag = "INSUFFICIENT"

            else:

                revenue_cagr, revenue_flag = calculate_cagr(
                    old_sales,
                    sales,
                    5
                )

            # =================================================
            # PAT CAGR
            # =================================================

            if old_pat is None:

                pat_cagr = None
                pat_flag = "INSUFFICIENT"

            else:

                pat_cagr, pat_flag = calculate_cagr(
                    old_pat,
                    net_profit,
                    5
                )

            # =================================================
            # EPS CAGR
            # =================================================

            if old_eps is None:

                eps_cagr = None
                eps_flag = "INSUFFICIENT"

            else:

                eps_cagr, eps_flag = calculate_cagr(
                    old_eps,
                    eps,
                    5
                )

            # =================================================
            # COMPOSITE QUALITY SCORE
            # =================================================

            quality_score = calculate_quality_score(
                roe,
                npm,
                de_ratio,
                icr,
                turnover
            )

            # =================================================
            # OUTPUT ROW
            # =================================================

            output_rows.append({

                "company_id":
                    company,

                "year":
                    str(year),

                "net_profit_margin_pct":
                    npm,

                "operating_profit_margin_pct":
                    opm,

                "return_on_equity_pct":
                    roe,

                "debt_to_equity":
                    de_ratio,

                "interest_coverage":
                    icr,

                "asset_turnover":
                    turnover,

                "free_cash_flow_cr":
                    fcf,

                "capex_cr":
                    capex,

                "earnings_per_share":
                    eps,

                "book_value_per_share":
                    book_value_per_share,

                "dividend_payout_ratio_pct":
                    dividend_payout,

                "total_debt_cr":
                    borrowings,

                "cash_from_operations_cr":
                    cfo,

                "revenue_cagr_5yr":
                    revenue_cagr,

                "revenue_cagr_5yr_flag":
                    revenue_flag,

                "pat_cagr_5yr":
                    pat_cagr,

                "pat_cagr_5yr_flag":
                    pat_flag,

                "eps_cagr_5yr":
                    eps_cagr,

                "eps_cagr_5yr_flag":
                    eps_flag,

                "composite_quality_score":
                    quality_score
            })

        # =====================================================
        # CREATE RESULT DATAFRAME
        # =====================================================

        result = pd.DataFrame(output_rows)

        print(
            f"\nCalculated rows before final deduplication: {len(result)}"
        )

        # =====================================================
        # FINAL DUPLICATE CHECK
        # =====================================================

        duplicate_count = result.duplicated(
            subset=[
                "company_id",
                "year"
            ]
        ).sum()

        print(
            f"Duplicate company-year rows: {duplicate_count}"
        )

        result = result.drop_duplicates(
            subset=[
                "company_id",
                "year"
            ],
            keep="last"
        )

        print(
            f"Rows after deduplication: {len(result)}"
        )

        # =====================================================
        # INSERT INTO SQLITE
        # =====================================================

        result.to_sql(
            "financial_ratios",
            conn,
            if_exists="append",
            index=False
        )

        conn.commit()

        # =====================================================
        # VERIFY ROW COUNT
        # =====================================================

        count = conn.execute(
            """
            SELECT COUNT(*)
            FROM financial_ratios
            """
        ).fetchone()[0]

        # =====================================================
        # VERIFY DATABASE DUPLICATES
        # =====================================================

        db_duplicates = conn.execute(
            """
            SELECT COUNT(*)
            FROM (
                SELECT
                    company_id,
                    year,
                    COUNT(*) AS row_count
                FROM financial_ratios
                GROUP BY
                    company_id,
                    year
                HAVING COUNT(*) > 1
            )
            """
        ).fetchone()[0]

        print("\n" + "=" * 60)

        print(
            "FINANCIAL RATIO ENGINE COMPLETE"
        )

        print("=" * 60)

        print(
            f"Rows inserted: {count}"
        )

        print(
            f"Duplicate company-year groups: {db_duplicates}"
        )

        if count >= 1100:

            print(
                "Day 12 row-count requirement: PASSED"
            )

        else:

            print(
                "Day 12 row-count requirement: FAILED"
            )

    except Exception as error:

        conn.rollback()

        print("\nRATIO ENGINE ERROR:")
        print(error)

        raise

    finally:

        conn.close()


# ============================================================
# RUN ENGINE
# ============================================================

if __name__ == "__main__":
    main()