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
        CREATE TABLE IF NOT EXISTS db (
            uin      TEXT    PRIMARY KEY,
            precinct INTEGER NOT NULL,
            voting   INTEGER NOT NULL DEFAULT 0,
            voted    INTEGER NOT NULL DEFAULT 0
        )
    """)

    # Seed with sample rows (skip if already populated)
    cursor.execute("SELECT COUNT(*) FROM db")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            ("67", 67, 0, 0),
            ("68", 68, 0, 0),
            ("69", 69, 0, 0),
        ]
        cursor.executemany(
            "INSERT INTO db (uin, precinct, voting, voted) VALUES (?, ?, ?, ?)",
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