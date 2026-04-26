"""
Run this once before testing to create and seed the local SQLite database.

    python init_db.py

It creates a file called `local_test.db` in the same directory.
When you switch to a real DB, you can delete this file and this script.
"""

import sqlite3

DB_PATH = "local_test.db"

def init():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id      INTEGER PRIMARY KEY,
            name    TEXT    NOT NULL,
            status  TEXT    NOT NULL DEFAULT 'pending'
        )
    """)

    # Seed with sample rows (skip if already populated)
    cursor.execute("SELECT COUNT(*) FROM items")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            (1, "Alpha",   "pending"),
            (2, "Beta",    "pending"),
            (3, "Gamma",   "pending"),
        ]
        cursor.executemany(
            "INSERT INTO items (id, name, status) VALUES (?, ?, ?)",
            sample_data
        )
        print("Seeded 3 sample rows.")
    else:
        print("Table already has data, skipping seed.")

    conn.commit()
    conn.close()
    print(f"Database ready: {DB_PATH}")

if __name__ == "__main__":
    init()
