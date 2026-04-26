import os
import sqlite3

# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

def get_connection():
    """
    LOCAL TESTING: uses SQLite (no installation needed).
    PRODUCTION:    replace this with your real DB driver, e.g.:
                   - psycopg2.connect(os.getenv("DATABASE_URL"))  ← PostgreSQL
                   - pymysql.connect(...)                         ← MySQL
                   - boto3.resource("dynamodb")                   ← DynamoDB
    """
    db_path = os.getenv("DATABASE_URL", "local_test.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # lets you access columns by name
    return conn


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def query_and_update(payload: dict) -> bool:
    """
    1. Query the DB using data from payload.
    2. Update the DB.
    3. Return True on success, False otherwise.

    """
    record_uin = payload.get("uin")

    if record_id is None or new_status is None:
        print("Payload missing necesary fields.")
        return False

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # --- Step 1: Query ---
        cursor.execute("SELECT * FROM items WHERE uin = ?", (record_uin,))
        row = cursor.fetchone()

        if not row:
            print(f"No record found with id={record_uin}")
            conn.close()
            return False

        print(f"Found record.")

        # --- Step 2: Update [for gate entry] ---
        cursor.execute(
            "UPDATE items SET status = ? WHERE id = ?",
            (new_status, record_id)
        )
        conn.commit()
        print(f"Updated id={record_id} → status='{new_status}'")

        conn.close()
        return True

    except Exception as e:
        print(f"DB error: {e}")
        return False
