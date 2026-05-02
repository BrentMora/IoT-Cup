import hashlib
import os

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv("db.env")

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
    Connects to PostgreSQL via DATABASE_URL environment variable.
    Set this in your .env file:
        DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
    """
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    conn.cursor_factory = psycopg2.extras.RealDictCursor  # access columns by name
    return conn


# ---------------------------------------------------------------------------
# Core logic - Entry
# ---------------------------------------------------------------------------

def process_entry(payload: dict) -> tuple:
    """
    1. Hash the incoming UIN.
    2. Query the voters table for a matching id_hash.
    3. If found, not yet voting, not yet voted, and precinct matches — allow entry.
    4. Set is_voting to TRUE and update updated_at.
    5. Return (True, "eligible") on success, (False, <reason>) otherwise.
    """
    input_uin = payload.get("uin")
    curr_precinct = payload.get("precinctID")

    if input_uin is None or curr_precinct is None:
        return (False, "missing fields")

    id_hash = hash_uin(input_uin)

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # --- Step 1: Query ---
        cursor.execute("SELECT * FROM voters WHERE id_hash = %s", (id_hash,))
        row = cursor.fetchone()

        # Deny voters not in the db
        if not row:
            conn.close()
            return (False, "unregistered")

        print(f"Found record.")

        # --- Step 2: Update [for gate entry] ---
        #
        # [Gate Entry]
        # If not voted and not voting and they are at the right precinct, let them enter.
        # Set is_voting to TRUE and update updated_at.

        if (row["is_voting"] == False
                and row["has_voted"] == False
                and str(curr_precinct) == str(row["precinct_id"])):
            cursor.execute(
                "UPDATE voters SET is_voting = %s, updated_at = CURRENT_TIMESTAMP WHERE id_hash = %s",
                (True, id_hash)
            )
            conn.commit()
            conn.close()
            return (True, "eligible")
        else:
            print(f"Entry denied.")
            conn.close()
            return (False, "mismatch or has voted")

    except Exception as e:
        print(f"DB error: {e}")
        return (False, "error")


# ---------------------------------------------------------------------------
# Core logic - Exit
# ---------------------------------------------------------------------------

def process_exit(payload: dict) -> tuple:
    """
    1. Hash the incoming UIN.
    2. Query the voters table for a matching id_hash.
    3. If found, currently voting, not yet voted, and precinct matches — allow exit.
    4. Set has_voted to TRUE, is_voting to FALSE, and update updated_at.
    5. Return (True, "eligible") on success, (False, <reason>) otherwise.
    """
    input_uin = payload.get("uin")
    curr_precinct = payload.get("precinctID")

    if input_uin is None or curr_precinct is None:
        return (False, "missing fields")

    id_hash = hash_uin(input_uin)

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # --- Step 1: Query ---
        cursor.execute("SELECT * FROM voters WHERE id_hash = %s", (id_hash,))
        row = cursor.fetchone()

        # Deny voters not in the db
        if not row:
            conn.close()
            return (False, "unregistered")

        print(f"Found record.")

        # --- Step 2: Update [for gate exit] ---
        #
        # [Gate Exit]
        # If currently voting and not yet voted and precinct matches — allow exit.
        # Set has_voted to TRUE, is_voting to FALSE, and update updated_at.

        if (row["is_voting"] == True
                and row["has_voted"] == False
                and str(curr_precinct) == str(row["precinct_id"])):
            cursor.execute(
                """UPDATE voters
                   SET has_voted = %s, is_voting = %s, updated_at = CURRENT_TIMESTAMP
                   WHERE id_hash = %s""",
                (True, False, id_hash)
            )
            conn.commit()
            conn.close()
            return (True, "eligible")
        else:
            print(f"Exit denied.")
            conn.close()
            return (False, "mismatch")

    except Exception as e:
        print(f"DB error: {e}")
        return (False, "error")