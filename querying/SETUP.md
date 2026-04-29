# Setup & Testing Guide
**Project:** IoT-Cup Querying Service  
**Language:** Python (Flask + SQLite for local testing)

---

## Project Structure

```
querying/
├── app.py            # Flask server — handles incoming HTTP requests
├── database.py       # All database logic — hashing, query, and update
├── init_db.py        # One-time script to create and seed the local test DB
├── requirements.txt  # Python dependencies
└── .env.example      # Template for environment variables
```

---

## Database Schema

```sql
CREATE TABLE voters (
    id_hash     CHAR(64)    PRIMARY KEY,  -- SHA-256 hash of the voter's UIN
    precinct_id VARCHAR(20) NOT NULL,
    is_voting   BOOLEAN     DEFAULT FALSE,
    has_voted   BOOLEAN     DEFAULT FALSE,
    updated_at  TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
);
```

> Raw UINs are **never stored**. Incoming UINs are hashed with SHA-256 in `database.py` before any DB query.

---

## How Hashing Works

The payload sends a raw UIN. Before touching the database, `database.py` hashes it:

```python
import hashlib
id_hash = hashlib.sha256(uin.encode()).hexdigest()
```

That hash is then used in all `SELECT` and `UPDATE` queries against `id_hash`.

---

## 1. First-Time Setup

### Step 1 — Install dependencies
Open a terminal in your project folder and run:
```bash
pip install -r requirements.txt
```

### Step 2 — Create the local test database
Run this **once**. It creates `local_test.db` with the `voters` table and 3 seeded rows.
```bash
python init_db.py
```

You should see:
```
Seeded 3 sample rows.
Database ready: local_test.db

Seeded UINs (for testing):
  UIN    precinct_id     id_hash
  ------ --------------- ----------------------------------------------------------------
  67     67              49d180ecf56132819571bf39d9b7b342522a2ac6d23c1418d3338251bfe469c8
  68     68              a21855da08cb102d1d217c53dc5824a3a795c1c1a44e971bf01ab9da3a2acbbf
  69     69              c75cb66ae28d8ebc6eded002c28a8ba0d06d3a78c6b5cbf9b2ade051f0775ac4
```

---

## 2. Running the Server

Open a terminal in your project folder and run:
```bash
python app.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

> Keep this terminal open while testing. The server must be running to accept requests.

---

## 3. Resetting the Database Between Tests

After a full entry → exit flow, rows are marked `has_voted = TRUE`. Reset to start fresh:
```bash
python init_db.py --reset
```

---

## 4. Testing the API

Open a **second** terminal window (keep the first one running the server).

The payload always sends the **raw UIN** — the server handles hashing internally.

A full voter flow is: **entry → exit**.

### Test Data

| UIN | precinct_id | is_voting | has_voted |
|-----|-------------|-----------|-----------|
| 67  | 67          | FALSE     | FALSE     |
| 68  | 68          | FALSE     | FALSE     |
| 69  | 69          | FALSE     | FALSE     |

---

### On Windows (PowerShell)

> Look for the **`Content`** line in the response output — that's your actual result.

#### `/enterRequest`

**Valid entry — expect `{"success": true}`**
```powershell
Invoke-WebRequest -Uri http://localhost:5000/enterRequest -Method POST -ContentType "application/json" -Body '{"uin": "67", "precinctID": "67"}'
```

**Already voting or voted — expect `{"success": false}`**
```powershell
Invoke-WebRequest -Uri http://localhost:5000/enterRequest -Method POST -ContentType "application/json" -Body '{"uin": "67", "precinctID": "67"}'
```
*(Run immediately after the valid entry above — uin 67 is now is_voting=TRUE)*

**Wrong precinct — expect `{"success": false}`**
```powershell
Invoke-WebRequest -Uri http://localhost:5000/enterRequest -Method POST -ContentType "application/json" -Body '{"uin": "68", "precinctID": "99"}'
```

**UIN not in DB — expect `{"success": false}`**
```powershell
Invoke-WebRequest -Uri http://localhost:5000/enterRequest -Method POST -ContentType "application/json" -Body '{"uin": "999", "precinctID": "67"}'
```

**Missing field — expect `{"success": false}`**
```powershell
Invoke-WebRequest -Uri http://localhost:5000/enterRequest -Method POST -ContentType "application/json" -Body '{"uin": "68"}'
```

---

#### `/exitRequest`

*(First run a valid `/enterRequest` for uin 68 so it is in is_voting=TRUE state)*
```powershell
Invoke-WebRequest -Uri http://localhost:5000/enterRequest -Method POST -ContentType "application/json" -Body '{"uin": "68", "precinctID": "68"}'
```

**Valid exit — expect `{"success": true}`**
```powershell
Invoke-WebRequest -Uri http://localhost:5000/exitRequest -Method POST -ContentType "application/json" -Body '{"uin": "68", "precinctID": "68"}'
```

**Not currently voting (never entered) — expect `{"success": false}`**
```powershell
Invoke-WebRequest -Uri http://localhost:5000/exitRequest -Method POST -ContentType "application/json" -Body '{"uin": "69", "precinctID": "69"}'
```

**Already voted — expect `{"success": false}`**
```powershell
Invoke-WebRequest -Uri http://localhost:5000/exitRequest -Method POST -ContentType "application/json" -Body '{"uin": "68", "precinctID": "68"}'
```
*(Run immediately after the valid exit above — uin 68 is now has_voted=TRUE)*

---

### On Mac / Linux / Git Bash

#### `/enterRequest`

**Valid entry — expect `{"success": true}`**
```bash
curl -X POST http://localhost:5000/enterRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "67", "precinctID": "67"}'
```

**Already voting or voted — expect `{"success": false}`**
```bash
curl -X POST http://localhost:5000/enterRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "67", "precinctID": "67"}'
```
*(Run immediately after the valid entry above)*

**Wrong precinct — expect `{"success": false}`**
```bash
curl -X POST http://localhost:5000/enterRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "68", "precinctID": "99"}'
```

**UIN not in DB — expect `{"success": false}`**
```bash
curl -X POST http://localhost:5000/enterRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "999", "precinctID": "67"}'
```

**Missing field — expect `{"success": false}`**
```bash
curl -X POST http://localhost:5000/enterRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "68"}'
```

---

#### `/exitRequest`

*(First run a valid `/enterRequest` for uin 68)*
```bash
curl -X POST http://localhost:5000/enterRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "68", "precinctID": "68"}'
```

**Valid exit — expect `{"success": true}`**
```bash
curl -X POST http://localhost:5000/exitRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "68", "precinctID": "68"}'
```

**Not currently voting (never entered) — expect `{"success": false}`**
```bash
curl -X POST http://localhost:5000/exitRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "69", "precinctID": "69"}'
```

**Already voted — expect `{"success": false}`**
```bash
curl -X POST http://localhost:5000/exitRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "68", "precinctID": "68"}'
```
*(Run immediately after the valid exit above)*

---

## 5. Switching to the Real Database (Supabase / PostgreSQL)

### Step 1 — Install the correct driver

Uncomment in `requirements.txt`, then run `pip install -r requirements.txt`:
```
psycopg2-binary
```

### Step 2 — Update `get_connection()` in `database.py`
```python
import psycopg2

def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))
```

### Step 3 — Update placeholder syntax in `database.py`

SQLite uses `?`, PostgreSQL uses `%s`. Update all four queries in `process_entry` and `process_exit`:

```python
# SELECT
cursor.execute("SELECT * FROM voters WHERE id_hash = %s", (id_hash,))

# Entry UPDATE
cursor.execute(
    "UPDATE voters SET is_voting = %s, updated_at = CURRENT_TIMESTAMP WHERE id_hash = %s",
    (True, id_hash)
)

# Exit UPDATE
cursor.execute(
    "UPDATE voters SET has_voted = %s, is_voting = %s, updated_at = CURRENT_TIMESTAMP WHERE id_hash = %s",
    (True, False, id_hash)
)
```

### Step 4 — Set environment variable on the EC2 server
```
DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
```

### Step 5 — Create the table in Supabase

Run this in the **Supabase SQL editor**:
```sql
CREATE TABLE voters (
    id_hash     CHAR(64)    PRIMARY KEY,
    precinct_id VARCHAR(20) NOT NULL,
    is_voting   BOOLEAN     DEFAULT FALSE,
    has_voted   BOOLEAN     DEFAULT FALSE,
    updated_at  TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
);
```

> `init_db.py` is for local testing only — your teammate handles the real DB setup.

---

## 6. Handing Off to Your Teammate

- **Start the server:** `python app.py` (or `gunicorn -w 4 app:app` for production)
- **Endpoints:** `POST /enterRequest` and `POST /exitRequest`
- **Request format:** JSON body with `uin` (string) and `precinct_id` (string)
- **Response format:** `{"success": true}` or `{"success": false}`
- **Required env variable:** `DATABASE_URL` must be set on the server

---

## Quick Reference

| Task                        | Command                                        |
|-----------------------------|------------------------------------------------|
| Install dependencies        | `pip install -r requirements.txt`              |
| Initialize local test DB    | `python init_db.py`                            |
| Reset DB between tests      | `python init_db.py --reset`                    |
| Start the server            | `python app.py`                                |
| Test (PowerShell)           | `Invoke-WebRequest ...` (see Section 4)        |
| Test (Mac/Linux/Git Bash)   | `curl -X POST ...` (see Section 4)             |
