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

# Test UINs — these must match UINs registered in the MOSIP environment.
# precinct_id is what must be sent as "precinctID" in the request payload.
RAW_UINS = [
    ("5408602380", "1"),   # Yuki Nakashima   — UP Campus
    ("7903740631", "2"),   # Haruka Kudou     — UP Campus
    ("8541274095", "3"),   # Aina Aiba        — Quezon City Central
    ("9406183480", "4"),   # Megu Sakuragawa  — Angeles City
]

SAMPLE_DATA = [
    (hash_uin(uin), precinct, False, False)
    for uin, precinct in RAW_UINS
]

def init(reset=False):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

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
        print("Database reset. Seeded 4 sample rows.")
    else:
        cursor.execute("SELECT COUNT(*) FROM voters")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO voters (id_hash, precinct_id, is_voting, has_voted) VALUES (?, ?, ?, ?)",
                SAMPLE_DATA
            )
            print("Seeded 4 sample rows.")
        else:
            print("Table already has data, skipping seed. Use --reset to wipe and re-seed.")

    conn.commit()
    conn.close()
    print(f"Database ready: {DB_PATH}")

    print("\nSeeded UINs (for testing):")
    print(f"  {'Name':<20} {'UIN':<12} {'precinct_id':<15} {'id_hash'}")
    print(f"  {'-'*20} {'-'*12} {'-'*15} {'-'*64}")
    names = ["Yuki Nakashima", "Haruka Kudou", "Aina Aiba", "Megu Sakuragawa"]
    for (uin, precinct), name in zip(RAW_UINS, names):
        print(f"  {name:<20} {uin:<12} {precinct:<15} {hash_uin(uin)}")

if __name__ == "__main__":
    reset = "--reset" in sys.argv
    init(reset)