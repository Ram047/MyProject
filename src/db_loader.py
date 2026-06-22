import sqlite3
import os

DB_PATH = "database/stock_analysis.db"
SCHEMA_PATH = "sql/schema.sql"


def create_database():
    # Create database folder if it doesn't exist
    os.makedirs("database", exist_ok=True)

    # Connect to SQLite database
    conn = sqlite3.connect(DB_PATH)

    # Enable Foreign Keys
    conn.execute("PRAGMA foreign_keys = ON;")

    # Read schema.sql
    with open(SCHEMA_PATH, "r") as file:
        schema = file.read()

    # Execute SQL script
    conn.executescript(schema)

    print("Database created successfully!")

    # Show all tables
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        ORDER BY name;
    """)

    print("\nTables Created:")
    for table in cursor.fetchall():
        print("-", table[0])

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_database()