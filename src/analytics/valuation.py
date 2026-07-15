import os
import sqlite3
import pandas as pd

DB_PATH = "database/stock_analysis.db"
OUTPUT_DIR = "output"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# --------------------------------------------------
# Load Valuation Data
# --------------------------------------------------

def load_valuation_data():

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT

        mc.company_id,

        c.company_name,

        s.broad_sector,

        mc.year,

        mc.market_cap_crore,

        mc.enterprise_value_crore,

        mc.pe_ratio,

        mc.pb_ratio,

        mc.ev_ebitda,

        fr.free_cash_flow_cr

    FROM market_cap mc

    LEFT JOIN companies c
        ON mc.company_id = c.id

    LEFT JOIN sectors s
        ON mc.company_id = s.company_id

    LEFT JOIN financial_ratios fr
        ON mc.company_id = fr.company_id
        AND mc.year = fr.year
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


# --------------------------------------------------
# Calculate FCF Yield
# --------------------------------------------------

def calculate_fcf_yield(df):

    df = df.copy()

    df["fcf_yield_pct"] = (
        df["free_cash_flow_cr"]
        / df["market_cap_crore"]
    ) * 100

    return df


# --------------------------------------------------
# Sector Median PE
# --------------------------------------------------

def calculate_sector_pe(df):

    latest_year = df["year"].max()

    latest = df[
        df["year"] == latest_year
    ].copy()

    sector_pe = (

        latest

        .groupby("broad_sector")["pe_ratio"]

        .median()

        .reset_index()

        .rename(
            columns={
                "pe_ratio": "sector_median_pe"
            }
        )

    )

    latest = latest.merge(
        sector_pe,
        on="broad_sector",
        how="left"
    )

    latest["pe_vs_sector_median_pct"] = (

        latest["pe_ratio"]

        /

        latest["sector_median_pe"]

    ) * 100

    return latest


# --------------------------------------------------
# Apply Flags
# --------------------------------------------------

def apply_flags(df):

    df = df.copy()

    df["flag"] = "Fair"

    df.loc[
        df["pe_ratio"] >
        df["sector_median_pe"] * 1.5,
        "flag"
    ] = "Caution"

    df.loc[
        df["pe_ratio"] <
        df["sector_median_pe"] * 0.7,
        "flag"
    ] = "Discount"

    return df


# --------------------------------------------------
# Export Files
# --------------------------------------------------

def export_outputs(df):

    summary = df[
        [
            "company_id",
            "company_name",
            "broad_sector",
            "pe_ratio",
            "pb_ratio",
            "ev_ebitda",
            "fcf_yield_pct",
            "sector_median_pe",
            "pe_vs_sector_median_pct",
            "flag"
        ]
    ].rename(
        columns={
            "broad_sector": "sector",
            "pe_ratio": "P/E",
            "pb_ratio": "P/B",
            "ev_ebitda": "EV/EBITDA",
            "fcf_yield_pct": "FCF_yield_pct",
            "sector_median_pe": "5yr_median_PE",
            "pe_vs_sector_median_pct": "PE_vs_sector_median_pct"
        }
    )

    summary.to_excel(
        os.path.join(
            OUTPUT_DIR,
            "valuation_summary.xlsx"
        ),
        index=False
    )

    flags = summary[
        summary["flag"] != "Fair"
    ]

    flags.to_csv(
        os.path.join(
            OUTPUT_DIR,
            "valuation_flags.csv"
        ),
        index=False
    )

    return summary, flags


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    print("=" * 70)
    print("VALUATION MODULE")
    print("=" * 70)

    print("\nLoading valuation data...")
    df = load_valuation_data()

    print("Companies loaded:", len(df))

    print("\nCalculating FCF Yield...")
    df = calculate_fcf_yield(df)

    print("Calculating Sector Median PE...")
    df = calculate_sector_pe(df)

    print("Applying Valuation Flags...")
    df = apply_flags(df)

    print("\nExporting files...")
    summary, flags = export_outputs(df)

    print("\nCreated:")
    print("output/valuation_summary.xlsx")
    print("output/valuation_flags.csv")

    print("\nFlag Summary")
    print(summary["flag"].value_counts())

    print("\nCompleted Successfully.")


if __name__ == "__main__":
    main()