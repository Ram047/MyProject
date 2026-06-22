import sqlite3
import pandas as pd

conn = sqlite3.connect("database/stock_analysis.db")

print("=" * 60)
print("5 RANDOM COMPANIES")
print("=" * 60)

query = """
SELECT id, company_name
FROM companies
ORDER BY RANDOM()
LIMIT 5;
"""

companies = pd.read_sql(query, conn)

print(companies)

print("\n" + "=" * 60)
print("YEAR COVERAGE")
print("=" * 60)

for company in companies["id"]:
    q = f"""
    SELECT
        MIN(year) AS first_year,
        MAX(year) AS last_year,
        COUNT(*) AS total_years
    FROM balancesheet
    WHERE company_id='{company}'
    """

    result = pd.read_sql(q, conn)

    print("\nCompany:", company)
    print(result)

print("\n" + "=" * 60)
print("COMPANIES WITH LESS THAN 5 YEARS OF DATA")
print("=" * 60)

query = """
SELECT
company_id,
COUNT(*) AS years
FROM balancesheet
GROUP BY company_id
HAVING COUNT(*) < 5
ORDER BY years;
"""

print(pd.read_sql(query, conn))

conn.close()