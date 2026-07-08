import os
import re
import sqlite3

import numpy as np
import pandas as pd


DB_PATH = "database/stock_analysis.db"
PEER_FILE = "data/peer_groups.xlsx"


# ============================================================
# METRIC CONFIGURATION
# ============================================================

METRICS = {
    "ROE": "return_on_equity_pct",
    "ROCE": "computed_roce_pct",
    "Net Profit Margin": "net_profit_margin_pct",
    "D/E": "debt_to_equity",
    "FCF": "free_cash_flow_cr",
    "PAT CAGR 5yr": "pat_cagr_5yr",
    "Revenue CAGR 5yr": "revenue_cagr_5yr",
    "EPS CAGR 5yr": "eps_cagr_5yr",
    "Interest Coverage": "interest_coverage",
    "Asset Turnover": "asset_turnover",
}


# ============================================================
# YEAR EXTRACTION
# ============================================================

def extract_year(value):
    """
    Extract year from:
    2024
    Mar 2024
    Dec 2023
    """

    if pd.isna(value):
        return None

    text = str(value)

    match = re.search(
        r"(19|20)\d{2}",
        text
    )

    if match:
        return int(match.group())

    try:
        return int(float(text))

    except (ValueError, TypeError):
        return None


# ============================================================
# LOAD PEER GROUPS
# ============================================================

def load_peer_groups(
    peer_file=PEER_FILE
):
    """
    Load peer group mapping.
    """

    if not os.path.exists(peer_file):
        raise FileNotFoundError(
            f"Peer group file not found: {peer_file}"
        )

    peers = pd.read_excel(
        peer_file,
        sheet_name="Sheet1"
    )

    required_columns = {
        "peer_group_name",
        "company_id"
    }

    missing = (
        required_columns
        -
        set(peers.columns)
    )

    if missing:
        raise ValueError(
            f"Missing peer group columns: {missing}"
        )

    peers = peers[
        [
            "peer_group_name",
            "company_id"
        ]
    ].copy()

    peers = peers.drop_duplicates()

    return peers


# ============================================================
# LOAD FINANCIAL DATA
# ============================================================

def load_financial_data(
    db_path=DB_PATH
):
    """
    Load ratio, P&L and balance-sheet data.
    ROCE is calculated because it is not stored in the
    current financial_ratios table.
    """

    conn = sqlite3.connect(
        db_path
    )

    try:

        ratios = pd.read_sql_query(
            """
            SELECT
                company_id,
                year,
                return_on_equity_pct,
                net_profit_margin_pct,
                debt_to_equity,
                free_cash_flow_cr,
                pat_cagr_5yr,
                revenue_cagr_5yr,
                eps_cagr_5yr,
                interest_coverage,
                asset_turnover
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


        balance = pd.read_sql_query(
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

    finally:

        conn.close()


    # ========================================================
    # NORMALIZE YEARS
    # ========================================================

    ratios["year_num"] = (
        ratios["year"]
        .apply(extract_year)
    )

    pnl["year_num"] = (
        pnl["year"]
        .apply(extract_year)
    )

    balance["year_num"] = (
        balance["year"]
        .apply(extract_year)
    )


    ratios = ratios.dropna(
        subset=["year_num"]
    )

    pnl = pnl.dropna(
        subset=["year_num"]
    )

    balance = balance.dropna(
        subset=["year_num"]
    )


    ratios["year_num"] = (
        ratios["year_num"]
        .astype(int)
    )

    pnl["year_num"] = (
        pnl["year_num"]
        .astype(int)
    )

    balance["year_num"] = (
        balance["year_num"]
        .astype(int)
    )


    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    ratios = ratios.drop_duplicates(
        subset=[
            "company_id",
            "year_num"
        ],
        keep="last"
    )

    pnl = pnl.drop_duplicates(
        subset=[
            "company_id",
            "year_num"
        ],
        keep="last"
    )

    balance = balance.drop_duplicates(
        subset=[
            "company_id",
            "year_num"
        ],
        keep="last"
    )


    # ========================================================
    # COMPUTE ROCE
    # ========================================================

    roce = pnl.merge(
        balance,
        on=[
            "company_id",
            "year_num"
        ],
        how="inner"
    )


    roce["ebit"] = (
        roce["operating_profit"].fillna(0)
        +
        roce["other_income"].fillna(0)
        -
        roce["interest"].fillna(0)
    )


    roce["capital_employed"] = (
        roce["equity_capital"].fillna(0)
        +
        roce["reserves"].fillna(0)
        +
        roce["borrowings"].fillna(0)
    )


    roce["computed_roce_pct"] = np.where(
        roce["capital_employed"] > 0,

        (
            roce["ebit"]
            /
            roce["capital_employed"]
            *
            100
        ),

        np.nan
    )


    roce = roce[
        [
            "company_id",
            "year_num",
            "computed_roce_pct"
        ]
    ]


    # ========================================================
    # MERGE ROCE WITH RATIOS
    # ========================================================

    financial_data = ratios.merge(
        roce,
        on=[
            "company_id",
            "year_num"
        ],
        how="left"
    )


    financial_data["year"] = (
        financial_data["year_num"]
    )


    return financial_data


# ============================================================
# PERCENT_RANK IMPLEMENTATION
# ============================================================

def percent_rank(series):
    """
    SQL-style PERCENT_RANK:

    (rank - 1) / (number of rows - 1)

    Higher metric value receives higher percentile.
    """

    numeric = pd.to_numeric(
        series,
        errors="coerce"
    )


    valid_count = numeric.notna().sum()


    if valid_count == 0:

        return pd.Series(
            np.nan,
            index=series.index
        )


    if valid_count == 1:

        result = pd.Series(
            np.nan,
            index=series.index
        )

        result.loc[
            numeric.notna()
        ] = 1.0

        return result


    ranks = numeric.rank(
        method="min",
        ascending=True
    )


    result = (
        ranks - 1
    ) / (
        valid_count - 1
    )


    return result


# ============================================================
# COMPUTE PEER PERCENTILES
# ============================================================

def compute_peer_percentiles(
    db_path=DB_PATH,
    peer_file=PEER_FILE
):
    """
    Compute percentile rankings for all 10 metrics
    inside each peer group and year.
    """

    peers = load_peer_groups(
        peer_file
    )


    financial_data = load_financial_data(
        db_path
    )


    data = financial_data.merge(
        peers,
        on="company_id",
        how="inner"
    )


    records = []


    for (
        peer_group_name,
        year
    ), group in data.groupby(
        [
            "peer_group_name",
            "year"
        ]
    ):


        group = group.copy()


        for metric_name, column_name in METRICS.items():


            group[
                "_percentile"
            ] = percent_rank(
                group[column_name]
            )


            # =================================================
            # D/E INVERSE RANKING
            # =================================================

            if metric_name == "D/E":

                group[
                    "_percentile"
                ] = (
                    1
                    -
                    group["_percentile"]
                )


            for _, row in group.iterrows():


                value = row[
                    column_name
                ]


                percentile = row[
                    "_percentile"
                ]


                records.append(
                    {
                        "company_id":
                            row["company_id"],

                        "peer_group_name":
                            peer_group_name,

                        "metric":
                            metric_name,

                        "value":
                            None
                            if pd.isna(value)
                            else float(value),

                        "percentile_rank":
                            None
                            if pd.isna(percentile)
                            else round(
                                float(percentile),
                                4
                            ),

                        "year":
                            int(year)
                    }
                )


    result = pd.DataFrame(
        records
    )


    return result


# ============================================================
# CREATE AND POPULATE SQLITE TABLE
# ============================================================

def populate_peer_percentiles(
    db_path=DB_PATH,
    peer_file=PEER_FILE
):

    print("=" * 70)

    print(
        "PEER PERCENTILE RANKING ENGINE"
    )

    print("=" * 70)


    peers = load_peer_groups(
        peer_file
    )


    print(
        f"\nPeer groups: "
        f"{peers['peer_group_name'].nunique()}"
    )


    print(
        f"Assigned companies: "
        f"{peers['company_id'].nunique()}"
    )


    print(
        "\nComputing percentile rankings..."
    )


    result = compute_peer_percentiles(
        db_path,
        peer_file
    )


    conn = sqlite3.connect(
        db_path
    )


    try:

        conn.execute(
            """
            DROP TABLE IF EXISTS peer_percentiles
            """
        )


        conn.execute(
            """
            CREATE TABLE peer_percentiles
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id TEXT NOT NULL,
                peer_group_name TEXT NOT NULL,
                metric TEXT NOT NULL,
                value REAL,
                percentile_rank REAL,
                year INTEGER NOT NULL
            )
            """
        )


        conn.commit()


        result.to_sql(
            "peer_percentiles",
            conn,
            if_exists="append",
            index=False
        )


        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_peer_percentiles_company
            ON peer_percentiles(company_id)
            """
        )


        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_peer_percentiles_group
            ON peer_percentiles(peer_group_name)
            """
        )


        conn.commit()


        row_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM peer_percentiles
            """
        ).fetchone()[0]


    finally:

        conn.close()


    print(
        f"Rows inserted: {row_count}"
    )


    print(
        "\nCreated table: peer_percentiles"
    )


    return result


# ============================================================
# COMPANY LOOKUP
# ============================================================

def get_company_peer_percentiles(
    company_id,
    db_path=DB_PATH,
    peer_file=PEER_FILE
):
    """
    Return peer percentile records for one company.

    Companies without peer-group assignment return the
    required message instead of raising an exception.
    """

    peers = load_peer_groups(
        peer_file
    )


    assigned = set(
        peers["company_id"]
        .astype(str)
        .str.upper()
    )


    company_id = str(
        company_id
    ).upper()


    if company_id not in assigned:

        return "No peer group assigned"


    conn = sqlite3.connect(
        db_path
    )


    try:

        result = pd.read_sql_query(
            """
            SELECT
                company_id,
                peer_group_name,
                metric,
                value,
                percentile_rank,
                year
            FROM peer_percentiles
            WHERE company_id = ?
            ORDER BY year DESC, metric
            """,
            conn,
            params=(company_id,)
        )


    finally:

        conn.close()


    return result


# ============================================================
# MAIN
# ============================================================

def main():

    result = populate_peer_percentiles()


    print("\nValidation Summary")

    print("-" * 70)


    print(
        "Metrics:",
        result["metric"].nunique()
    )


    print(
        "Peer Groups:",
        result["peer_group_name"].nunique()
    )


    print(
        "Companies:",
        result["company_id"].nunique()
    )


    print(
        "Percentile Minimum:",
        result["percentile_rank"].min()
    )


    print(
        "Percentile Maximum:",
        result["percentile_rank"].max()
    )


    print(
        "\nProcessing complete."
    )


if __name__ == "__main__":

    main()