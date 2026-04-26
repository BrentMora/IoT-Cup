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

    Expected payload keys:
        - "id"     (int)  : record to look up
        - "status" (str)  : new status value to write
    """
    record_id = payload.get("id")
    new_status = payload.get("status")

    if record_id is None or new_status is None:
        print("Payload missing 'id' or 'status'")
        return False

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # --- Step 1: Query ---
        cursor.execute("SELECT * FROM items WHERE id = ?", (record_id,))
        row = cursor.fetchone()

        if not row:
            print(f"No record found with id={record_id}")
            conn.close()
            return False

        print(f"Found record: id={row['id']}, name={row['name']}, status={row['status']}")

        # --- Step 2: Update ---
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
