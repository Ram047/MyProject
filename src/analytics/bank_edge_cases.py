import os
import sqlite3
import pandas as pd


DB_PATH = "database/stock_analysis.db"
LOG_PATH = "output/ratio_edge_cases.log"


def safe_float(value):
    if value is None or pd.isna(value):
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def classify_anomaly(metric, company_id, computed, source, difference):
    """
    Categorise anomaly as:
    - data source issue
    - version difference
    - formula discrepancy
    """

    # Very small or implausible source values compared with computed values
    if source is not None and abs(source) < 1 and abs(computed) > 10:
        return "data source issue"

    # Moderate differences may result from different reporting periods
    if difference <= 15:
        return "version difference"

    return "formula discrepancy"


def main():
    print("=" * 65)
    print("DAY 13 - BANK CARVE-OUT & RATIO EDGE CASE REVIEW")
    print("=" * 65)

    os.makedirs("output", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    companies = pd.read_sql_query(
        """
        SELECT
            id AS company_id,
            roce_percentage AS source_roce,
            roe_percentage AS source_roe
        FROM companies
        """,
        conn
    )

    sectors = pd.read_sql_query(
        """
        SELECT
            company_id,
            broad_sector
        FROM sectors
        """,
        conn
    )

    ratios = pd.read_sql_query(
        """
        SELECT
            company_id,
            year,
            return_on_equity_pct,
            debt_to_equity
        FROM financial_ratios
        """,
        conn
    )

    pnl = pd.read_sql_query(
        """
        SELECT
            company_id,
            year,
            operating_profit,
            other_income,
            interest
        FROM profitandloss
        """,
        conn
    )

    bs = pd.read_sql_query(
        """
        SELECT
            company_id,
            year,
            equity_capital,
            reserves,
            borrowings
        FROM balancesheet
        """,
        conn
    )

    # ---------------------------------------------------------
    # FINANCIALS SECTOR CARVE-OUT
    # ---------------------------------------------------------

    financial_companies = sectors[
        sectors["broad_sector"].str.lower() == "financials"
    ]["company_id"].dropna().unique()

    print(
        f"\nFinancials companies found: {len(financial_companies)}"
    )

    print(
        "Standard D/E warning suppressed for Financials sector."
    )

    # Demonstrate suppression logic
    ratios = ratios.merge(
        sectors,
        on="company_id",
        how="left"
    )

    ratios["high_leverage_flag"] = (
        (ratios["debt_to_equity"] > 5)
        &
        (
            ratios["broad_sector"]
            .fillna("")
            .str.lower()
            != "financials"
        )
    )

    # ---------------------------------------------------------
    # PREPARE ROCE COMPUTATION
    # ---------------------------------------------------------

    pnl["year_key"] = (
        pnl["year"]
        .astype(str)
        .str.extract(r"((?:19|20)\d{2})")[0]
    )

    bs["year_key"] = (
        bs["year"]
        .astype(str)
        .str.extract(r"((?:19|20)\d{2})")[0]
    )

    pnl = pnl.dropna(subset=["year_key"])
    bs = bs.dropna(subset=["year_key"])

    pnl = pnl.drop_duplicates(
        subset=["company_id", "year_key"],
        keep="last"
    )

    bs = bs.drop_duplicates(
        subset=["company_id", "year_key"],
        keep="last"
    )

    roce_data = pnl.merge(
        bs,
        on=["company_id", "year_key"],
        how="inner",
        suffixes=("_pnl", "_bs")
    )

    # Use latest available year for each company
    roce_data["year_key"] = roce_data["year_key"].astype(int)

    roce_data = (
        roce_data
        .sort_values(["company_id", "year_key"])
        .groupby("company_id")
        .tail(1)
    )

    # EBIT proxy
    roce_data["ebit"] = (
        roce_data["operating_profit"].fillna(0)
        + roce_data["other_income"].fillna(0)
        - roce_data["interest"].fillna(0)
    )

    roce_data["capital_employed"] = (
        roce_data["equity_capital"].fillna(0)
        + roce_data["reserves"].fillna(0)
        + roce_data["borrowings"].fillna(0)
    )

    roce_data["computed_roce"] = roce_data.apply(
        lambda row:
        (
            row["ebit"] / row["capital_employed"] * 100
            if row["capital_employed"] > 0
            else None
        ),
        axis=1
    )

    # ---------------------------------------------------------
    # GET LATEST ROE FROM RATIO ENGINE
    # ---------------------------------------------------------

    ratios["year_num"] = pd.to_numeric(
        ratios["year"],
        errors="coerce"
    )

    latest_roe = (
        ratios
        .dropna(subset=["year_num"])
        .sort_values(["company_id", "year_num"])
        .groupby("company_id")
        .tail(1)
    )

    # ---------------------------------------------------------
    # BUILD COMPARISON DATA
    # ---------------------------------------------------------

    comparison = companies.merge(
        roce_data[
            [
                "company_id",
                "year_key",
                "computed_roce"
            ]
        ],
        on="company_id",
        how="left"
    )

    comparison = comparison.merge(
        latest_roe[
            [
                "company_id",
                "return_on_equity_pct"
            ]
        ],
        on="company_id",
        how="left"
    )

    anomalies = []

    # ---------------------------------------------------------
    # ROCE CROSS-CHECK
    # ---------------------------------------------------------

    for _, row in comparison.iterrows():
        company = row["company_id"]

        computed = safe_float(row["computed_roce"])
        source = safe_float(row["source_roce"])

        if computed is not None and source is not None:
            difference = abs(computed - source)

            if difference > 5:
                category = classify_anomaly(
                    "ROCE",
                    company,
                    computed,
                    source,
                    difference
                )

                anomalies.append(
                    {
                        "company_id": company,
                        "metric": "ROCE",
                        "computed_value": round(computed, 2),
                        "source_value": round(source, 2),
                        "difference": round(difference, 2),
                        "category": category
                    }
                )

    # ---------------------------------------------------------
    # ROE CROSS-CHECK
    # ---------------------------------------------------------

    for _, row in comparison.iterrows():
        company = row["company_id"]

        computed = safe_float(
            row["return_on_equity_pct"]
        )

        source = safe_float(
            row["source_roe"]
        )

        if computed is not None and source is not None:
            difference = abs(computed - source)

            if difference > 5:
                category = classify_anomaly(
                    "ROE",
                    company,
                    computed,
                    source,
                    difference
                )

                anomalies.append(
                    {
                        "company_id": company,
                        "metric": "ROE",
                        "computed_value": round(computed, 2),
                        "source_value": round(source, 2),
                        "difference": round(difference, 2),
                        "category": category
                    }
                )

    # ---------------------------------------------------------
    # WRITE LOG FILE
    # ---------------------------------------------------------

    with open(LOG_PATH, "w", encoding="utf-8") as log:
        log.write(
            "DAY 13 - RATIO EDGE CASE REVIEW\n"
        )

        log.write("=" * 70 + "\n\n")

        log.write(
            f"Financials companies: {len(financial_companies)}\n"
        )

        log.write(
            "D/E warning policy: Suppressed for Financials sector\n\n"
        )

        log.write(
            "ROE analytics policy: Ratio engine value is used for analytics.\n"
        )

        log.write(
            "Source ROE is retained for display/reference only.\n\n"
        )

        log.write("=" * 70 + "\n")

        for item in anomalies:
            log.write(
                f"Company: {item['company_id']}\n"
            )

            log.write(
                f"Metric: {item['metric']}\n"
            )

            log.write(
                f"Computed: {item['computed_value']}\n"
            )

            log.write(
                f"Source: {item['source_value']}\n"
            )

            log.write(
                f"Difference: {item['difference']}\n"
            )

            log.write(
                f"Category: {item['category']}\n"
            )

            log.write("-" * 70 + "\n")

    print(
        f"\nAnomalies logged: {len(anomalies)}"
    )

    print(
        f"Log generated: {LOG_PATH}"
    )

    print("\nDay 13 processing complete.")

    conn.close()


if __name__ == "__main__":
    main()