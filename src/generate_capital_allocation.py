import sqlite3
import pandas as pd
from analytics.cashflow import capital_allocation_pattern, cfo_quality_score

conn = sqlite3.connect("database/stock_analysis.db")

cashflow = pd.read_sql("SELECT * FROM cashflow", conn)
profit = pd.read_sql(
    "SELECT company_id, year, net_profit FROM profitandloss",
    conn
)

df = cashflow.merge(
    profit,
    on=["company_id", "year"],
    how="left"
)

records = []

for _, row in df.iterrows():

    quality = cfo_quality_score(
        row["operating_activity"],
        row["net_profit"]
    )

    ratio = None

    if quality is not None:
        ratio = quality[0]

    label = capital_allocation_pattern(
        row["operating_activity"],
        row["investing_activity"],
        row["financing_activity"],
        ratio
    )

    records.append({
        "company_id": row["company_id"],
        "year": row["year"],
        "cfo_sign": "+" if row["operating_activity"] >= 0 else "-",
        "cfi_sign": "+" if row["investing_activity"] >= 0 else "-",
        "cff_sign": "+" if row["financing_activity"] >= 0 else "-",
        "pattern_label": label
    })

output = pd.DataFrame(records)

output.to_csv(
    "output/capital_allocation.csv",
    index=False
)

print("capital_allocation.csv generated successfully!")

conn.close()