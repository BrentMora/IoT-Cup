import hashlib
import os
import sqlite3

# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------

def hash_uin(uin: str) -> str:
    """
    SHA-256 hash the incoming UIN before querying the DB.
    The DB stores hashes, never raw UINs.
    """
    return hashlib.sha256(uin.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

def get_connection():
    """
    LOCAL TESTING: uses SQLite (no installation needed).
    PRODUCTION:    replace this with your real DB driver, e.g.:
                   - psycopg2.connect(os.getenv("DATABASE_URL"))  ← PostgreSQL (Supabase, Neon, RDS)
                   - pymysql.connect(...)                         ← MySQL
    """
    db_path = os.getenv("DATABASE_URL", "local_test.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # lets you access columns by name
    return conn


# ---------------------------------------------------------------------------
# Core logic - Entry
# ---------------------------------------------------------------------------

def process_entry(payload: dict) -> bool:
    """
    1. Hash the incoming UIN.
    2. Query the voters table for a matching id_hash.
    3. If found, not yet voting, not yet voted, and precinct matches — allow entry.
    4. Set is_voting to TRUE and update updated_at.
    5. Return True on success, False otherwise.
    """
    input_uin = payload.get("uin")
    curr_precinct = payload.get("precinct_id")

    if input_uin is None or curr_precinct is None:
        print("Payload missing necessary fields.")
        return False

    id_hash = hash_uin(input_uin)

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # --- Step 1: Query ---
        cursor.execute("SELECT * FROM voters WHERE id_hash = ?", (id_hash,))
        row = cursor.fetchone()

        # Deny voters not in the db
        if not row:
            print(f"No record found for given UIN.")
            conn.close()
            return False

        print(f"Found record.")

        # --- Step 2: Update [for gate entry] ---
        #
        # [Gate Entry]
        # If not voted and not voting and they are at the right precinct, let them enter.
        # Set is_voting to TRUE and update updated_at.

        if (row["is_voting"] == 0
                and row["has_voted"] == 0
                and str(curr_precinct) == str(row["precinct_id"])):
            cursor.execute(
                "UPDATE voters SET is_voting = ?, updated_at = CURRENT_TIMESTAMP WHERE id_hash = ?",
                (True, id_hash)
            )
            conn.commit()
            conn.close()
            return True
        else:
            print(f"Entry denied.")
            conn.close()
            return False

    except Exception as e:
        print(f"DB error: {e}")
        return False


# ---------------------------------------------------------------------------
# Core logic - Exit
# ---------------------------------------------------------------------------

def process_exit(payload: dict) -> bool:
    """
    1. Hash the incoming UIN.
    2. Query the voters table for a matching id_hash.
    3. If found, currently voting, not yet voted, and precinct matches — allow exit.
    4. Set has_voted to TRUE, is_voting to FALSE, and update updated_at.
    5. Return True on success, False otherwise.
    """
    input_uin = payload.get("uin")
    curr_precinct = payload.get("precinct_id")

    if input_uin is None or curr_precinct is None:
        print("Payload missing necessary fields.")
        return False

    id_hash = hash_uin(input_uin)

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # --- Step 1: Query ---
        cursor.execute("SELECT * FROM voters WHERE id_hash = ?", (id_hash,))
        row = cursor.fetchone()

        # Deny voters not in the db
        if not row:
            print(f"No record found for given UIN.")
            conn.close()
            return False

        print(f"Found record.")

        # --- Step 2: Update [for gate exit] ---
        #
        # [Gate Exit]
        # If currently voting and not yet voted and precinct matches — allow exit.
        # Set has_voted to TRUE, is_voting to FALSE, and update updated_at.

        if (row["is_voting"] == 1
                and row["has_voted"] == 0
                and str(curr_precinct) == str(row["precinct_id"])):
            cursor.execute(
                """UPDATE voters
                   SET has_voted = ?, is_voting = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE id_hash = ?""",
                (True, False, id_hash)
            )
            conn.commit()
            conn.close()
            return True
        else:
            print(f"Exit denied.")
            conn.close()
            return False

    except Exception as e:
        print(f"DB error: {e}")
        return False
