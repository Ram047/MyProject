import sqlite3
import pandas as pd
import csv
import os

DB = "database/stock_analysis.db"

conn = sqlite3.connect(DB)
conn.execute("PRAGMA foreign_keys = OFF")

audit = []

def clear_tables():
    tables = [
        "prosandcons",
        "peer_groups",
        "sectors",
        "market_cap",
        "stock_prices",
        "documents",
        "analysis",
        "profitandloss",
        "cashflow",
        "balancesheet",
        "companies"
    ]

    cursor = conn.cursor()

    for table in tables:
        cursor.execute(f"DELETE FROM {table}")

    conn.commit()

    print("Existing data cleared.\n")
    
def load_table(file_name, table_name, header):
    try:
        df = pd.read_excel(
            f"data/{file_name}",
            header=header
        )

        df.to_sql(
            table_name,
            conn,
            if_exists="append",
            index=False
        )

        conn.commit()

        audit.append([
            table_name,
            len(df),
            "SUCCESS"
        ])

        print(f"✓ {table_name}: {len(df)} rows")

    except Exception as e:

        conn.rollback()

        audit.append([
            table_name,
            0,
            str(e)
        ])

        print(f"✗ {table_name}")
        print(e)

clear_tables()

print("\nLoading Data...\n")

# Parent table FIRST
load_table("companies.xlsx", "companies", 1)

# Commit parent
conn.commit()

# Child tables
load_table("balancesheet.xlsx", "balancesheet", 1)
load_table("cashflow.xlsx", "cashflow", 1)
load_table("profitandloss.xlsx", "profitandloss", 1)
load_table("analysis.xlsx", "analysis", 1)
load_table("documents.xlsx", "documents", 1)

# Other datasets
load_table("stock_prices.xlsx", "stock_prices", 0)
load_table("market_cap.xlsx", "market_cap", 0)
load_table("sectors.xlsx", "sectors", 0)
load_table("peer_groups.xlsx", "peer_groups", 0)

# Optional
try:
    load_table("prosandcons.xlsx", "prosandcons", 1)
except:
    pass


os.makedirs("output", exist_ok=True)

with open(
    "output/load_audit.csv",
    "w",
    newline=""
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "Table",
        "Rows Loaded",
        "Status"
    ])

    writer.writerows(audit)

print("\nAudit report generated.")

fk = conn.execute(
    "PRAGMA foreign_key_check"
).fetchall()

print("\nForeign Key Errors:", len(fk))

conn.close()