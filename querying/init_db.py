"""
Run this once before testing to create and seed the local SQLite database.

    python init_db.py

To wipe all data and start fresh during testing:

    python init_db.py --reset

It creates a file called `local_test.db` in the same directory.
When you switch to a real DB, you can delete this file and this script.
"""

import hashlib
import sqlite3
import sys

DB_PATH = "local_test.db"

def hash_uin(uin: str) -> str:
    return hashlib.sha256(uin.encode()).hexdigest()

# Test UINs — hashed before storing, just like the real system
RAW_UINS = [
    ("67", "67"),
    ("68", "68"),
    ("69", "69"),
]

SAMPLE_DATA = [
    (hash_uin(uin), precinct, False, False)
    for uin, precinct in RAW_UINS
]

def init(reset=False):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create table — mirrors the real production schema as closely as SQLite allows
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS voters (
            id_hash     CHAR(64)     PRIMARY KEY,
            precinct_id VARCHAR(20)  NOT NULL,
            is_voting   BOOLEAN      DEFAULT FALSE,
            has_voted   BOOLEAN      DEFAULT FALSE,
            updated_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
        )
    """)

    if reset:
        cursor.execute("DELETE FROM voters")
        cursor.executemany(
            "INSERT INTO voters (id_hash, precinct_id, is_voting, has_voted) VALUES (?, ?, ?, ?)",
            SAMPLE_DATA
        )
        print("Database reset. Seeded 3 sample rows.")
    else:
        cursor.execute("SELECT COUNT(*) FROM voters")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO voters (id_hash, precinct_id, is_voting, has_voted) VALUES (?, ?, ?, ?)",
                SAMPLE_DATA
            )
            print("Seeded 3 sample rows.")
        else:
            print("Table already has data, skipping seed. Use --reset to wipe and re-seed.")

    conn.commit()
    conn.close()
    print(f"Database ready: {DB_PATH}")

    # Print hashes so you know what's in the DB
    print("\nSeeded UINs (for testing):")
    print(f"  {'UIN':<6} {'precinct_id':<15} {'id_hash'}")
    print(f"  {'-'*6} {'-'*15} {'-'*64}")
    for uin, precinct in RAW_UINS:
        print(f"  {uin:<6} {precinct:<15} {hash_uin(uin)}")

if __name__ == "__main__":
    reset = "--reset" in sys.argv
    init(reset)
