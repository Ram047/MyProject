import os
import re
import sqlite3
import pandas as pd

# --------------------------------------------------
# Paths
# --------------------------------------------------

DB_PATH = "database/stock_analysis.db"
DATA_PATH = "data/analysis.xlsx"
OUTPUT_DIR = "output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

PATTERN = re.compile(r"(\d+)\s*Years?:?\s*([\d.]+)%")

TARGET_FIELDS = [
    "compounded_sales_growth",
    "compounded_profit_growth",
    "stock_price_cagr",
    "roe"
]


# --------------------------------------------------
# Load Analysis Data
# --------------------------------------------------

def load_analysis():

    if os.path.exists(DATA_PATH):

        return pd.read_excel(
            DATA_PATH,
            header=1
        )

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        "SELECT * FROM analysis",
        conn
    )

    conn.close()

    return df
# --------------------------------------------------
# Parse Text Fields
# --------------------------------------------------

def parse_analysis(df):

    parsed = []
    failures = []

    for _, row in df.iterrows():

        company = row["company_id"]

        for metric in TARGET_FIELDS:

            value = row.get(metric)

            if pd.isna(value):
                continue

            value = str(value)

            match = PATTERN.search(value)

            if match:

                parsed.append({

                    "company_id": company,

                    "metric_type": metric,

                    "period_years": int(match.group(1)),

                    "value_pct": float(match.group(2))

                })

            else:

                failures.append({

                    "company_id": company,

                    "metric_type": metric,

                    "original_text": value

                })

    parsed_df = pd.DataFrame(parsed)

    failures_df = pd.DataFrame(failures)

    return parsed_df, failures_df


# --------------------------------------------------
# Export Results
# --------------------------------------------------

def export_results(parsed_df, failures_df):

    parsed_df.to_csv(
        os.path.join(
            OUTPUT_DIR,
            "analysis_parsed.csv"
        ),
        index=False
    )

    failures_df.to_csv(
        os.path.join(
            OUTPUT_DIR,
            "parse_failures.csv"
        ),
        index=False
    )


# --------------------------------------------------
# Cross Validation
# --------------------------------------------------

def cross_validate(parsed_df):

    conn = sqlite3.connect(DB_PATH)

    ratios = pd.read_sql(
        """
        SELECT
            company_id,
            revenue_cagr_5yr,
            pat_cagr_5yr,
            return_on_equity_pct
        FROM financial_ratios
        """,
        conn
    )

    conn.close()

    metric_map = {

        "compounded_sales_growth":
            "revenue_cagr_5yr",

        "compounded_profit_growth":
            "pat_cagr_5yr",

        "roe":
            "return_on_equity_pct"

    }

    review = []

    for _, row in parsed_df.iterrows():

        metric = row["metric_type"]

        if metric not in metric_map:
            continue

        company = row["company_id"]

        db = ratios[
            ratios.company_id == company
        ]

        if db.empty:
            continue

        actual = db.iloc[0][metric_map[metric]]

        if pd.isna(actual):
            continue

        diff = abs(actual - row["value_pct"])

        if diff > 5:

            review.append({

                "company_id": company,

                "metric_type": metric,

                "parsed_value": row["value_pct"],

                "computed_value": actual,

                "difference": diff

            })

    review_df = pd.DataFrame(review)

    review_df.to_csv(

        os.path.join(
            OUTPUT_DIR,
            "manual_review.csv"
        ),

        index=False

    )

    return review_df


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    print("=" * 70)
    print("NLP ANALYSIS PARSER")
    print("=" * 70)

    df = load_analysis()

    print("Rows Loaded :", len(df))

    parsed_df, failures_df = parse_analysis(df)

    export_results(
        parsed_df,
        failures_df
    )

    review_df = cross_validate(parsed_df)

    print()

    print("Parsed Records :", len(parsed_df))
    print("Failed Records :", len(failures_df))
    print("Manual Review  :", len(review_df))

    print()

    print("Generated Files")

    print("output/analysis_parsed.csv")
    print("output/parse_failures.csv")
    print("output/manual_review.csv")


if __name__ == "__main__":
    main()