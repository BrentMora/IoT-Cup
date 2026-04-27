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
# Core logic - Entry
# ---------------------------------------------------------------------------

def process_entry(payload: dict) -> bool:
    """
    1. Query the DB using data from payload.
    2. Update the DB.
    3. Return True on success, False otherwise.
    """
    input_uin = payload.get("uin")
    curr_precinct = payload.get("precinct")

    if input_uin is None:
        print("Payload missing necessary fields.")
        return False

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # --- Step 1: Query ---
        cursor.execute("SELECT * FROM db WHERE uin = ?", (input_uin,))
        row = cursor.fetchone()

        # deny voters not in the db

        if not row:
            print(f"No record found with uin={input_uin}")
            conn.close()
            return False

        print(f"Found record.")

        # --- Step 2: Update [for gate entry] ---
        
        '''
            [Gate Entry]
            If not voted and not voting and they are at the right precinct, let them enter the gate.
            Set voting to True.

        '''

        if row["voting"] == 0 and row["voted"] == 0 and curr_precinct == row["precinct"]:
            cursor.execute(
                "UPDATE db SET voting = ? WHERE uin = ?",
                (1, input_uin)
            )
            conn.commit()
            conn.close()
            return True
        else:
            print(f"uin={input_uin} has already voted.")
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
    1. Query the DB using data from payload.
    2. Update the DB.
    3. Return True on success, False otherwise.
    """
    input_uin = payload.get("uin")
    curr_precinct = payload.get("precinct")

    if input_uin is None:
        print("Payload missing necessary fields.")
        return False

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # --- Step 1: Query ---
        cursor.execute("SELECT * FROM db WHERE uin = ?", (input_uin,))
        row = cursor.fetchone()

        # deny voters not in the db

        if not row:
            print(f"No record found with uin={input_uin}")
            conn.close()
            return False

        print(f"Found record.")

        # --- Step 2: Update [for gate entry] ---
        
        '''
            [Gate Exit]
            If voting and not voted and they are at the right precinct, let them exit the gate.
            Set voted to True.
            Set voting to False.

        '''

        if row["voting"] == 1 and row["voted"] == 0 and curr_precinct == row["precinct"]:
            cursor.execute("UPDATE db SET voted = ?, voting = ? WHERE uin = ?", (1, 0, input_uin))
            conn.commit()
            conn.close()
            return True
        else:
            print(f"uin={input_uin} has already voted.")
            conn.close()
            return False

    except Exception as e:
        print(f"DB error: {e}")
        return False