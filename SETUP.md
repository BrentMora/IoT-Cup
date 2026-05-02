# Setup & Testing Guide
**Project:** IoT-Cup Querying Service  
**Language:** Python (FastAPI + Supabase PostgreSQL)

---

## Project Structure

```
querying/
├── GATE_Auth.py      # FastAPI server — handles incoming HTTP requests
├── database.py       # All database logic — hashing, query, and update
├── ID_Payload.py     # Pydantic model for incoming request validation
├── init_db.py        # Local testing only — creates a local SQLite DB
├── requirements.txt  # Python dependencies
└── db.env            # Database credentials (never commit this)
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

## Response Format

All endpoints return:
```json
{ "authStatus": <true|false>, "status": "<status string>" }
```

| status | authStatus | meaning |
|---|---|---|
| `"eligible"` | true | voter cleared, gate should open |
| `"unregistered"` | false | UIN hash not found in DB |
| `"mismatch or has voted"` | false | wrong precinct, already voting, or already voted (entry) |
| `"mismatch"` | false | wrong precinct, not currently voting, or already voted (exit) |
| `"missing fields"` | false | `uin` or `precinctID` not in payload |
| `"not in MOSIP"` | false | MOSIP authentication failed |
| `"error"` | false | unexpected DB error |
| `"unhandled error"` | false | uncaught exception in the server |
| `"no data received"` | false | empty or non-JSON request body |

---

## 1. First-Time Setup

### Step 1 — Install dependencies
Open a terminal in your project folder and run:
```powershell
pip install -r requirements.txt
```

### Step 2 — Configure database credentials
Create a `db.env` file in your project root:
```
DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
```
Get the connection string from: **Supabase → Project Settings → Database → Connection string → URI**

> Make sure `db.env` is in your `.gitignore` — never commit credentials.

---

## 2. Running the Server

```powershell
uvicorn GATE_Auth:app --host 0.0.0.0 --port 5000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
```

> Keep this terminal open while testing.

---

## 3. Resetting Test Data Between Tests

Since you're using the live Supabase database, reset voter states directly in the **Supabase SQL editor**:

```sql
UPDATE voters SET is_voting = FALSE, has_voted = FALSE
WHERE uin IN (
    'c8c5dd8ce3b91870275d53773838eabbbc081a84df3e2154d473fe5c64398e50',
    'c7d7d0a81a210838f91a6e63f0f3273a064d020a26cbf5bb1b925a3da5cedaaa',
    'b05b305b3bcfe15a69485f5f6c259efcb1df77fc1c841a44f87c278d910a5f36',
    '98adb66a165abc7893ec33214f13d92968add9b9fa1a1fd81a522e5ed45a5f74'
);
```

Or reset a single voter by UIN hash.

---

## 4. Testing the API

Open a **second** terminal window (keep the first one running the server).

The payload always sends the **raw UIN** — the server handles hashing internally.

A full voter flow is: **entry → exit**.

### Test Data (Supabase)

| UIN | precinctID | id_hash |
|-----|------------|---------|
| 5408602380 | 0001A | `c8c5dd8ce3b91870275d53773838eabbbc081a84df3e2154d473fe5c64398e50` |
| 7903740631 | 0001A | `c7d7d0a81a210838f91a6e63f0f3273a064d020a26cbf5bb1b925a3da5cedaaa` |
| 8541274095 | 0067C | `b05b305b3bcfe15a69485f5f6c259efcb1df77fc1c841a44f87c278d910a5f36` |
| 9406183480 | 0002B | `98adb66a165abc7893ec33214f13d92968add9b9fa1a1fd81a522e5ed45a5f74` |

---

### On Windows (PowerShell)

> Look for the **`Content`** line in the response output — that's your actual result.

#### `/enterRequest`

**Valid entry — expect `{"authStatus": true, "status": "eligible"}`**
```powershell
Invoke-WebRequest -Uri http://localhost:5000/enterRequest -Method POST -ContentType "application/json" -Body '{"uin": "5408602380", "precinctID": "0001A"}'
```

**Already voting (run immediately after the one above) — expect `{"authStatus": false, "status": "mismatch or has voted"}`**
```powershell
Invoke-WebRequest -Uri http://localhost:5000/enterRequest -Method POST -ContentType "application/json" -Body '{"uin": "5408602380", "precinctID": "0001A"}'
```

**Wrong precinct — expect `{"authStatus": false, "status": "mismatch or has voted"}`**
```powershell
Invoke-WebRequest -Uri http://localhost:5000/enterRequest -Method POST -ContentType "application/json" -Body '{"uin": "8541274095", "precinctID": "0001A"}'
```

**UIN not in DB — expect `{"authStatus": false, "status": "unregistered"}`**
```powershell
Invoke-WebRequest -Uri http://localhost:5000/enterRequest -Method POST -ContentType "application/json" -Body '{"uin": "0000000000", "precinctID": "0001A"}'
```

**Missing field — expect `{"authStatus": false, "status": "missing fields"}`**
```powershell
Invoke-WebRequest -Uri http://localhost:5000/enterRequest -Method POST -ContentType "application/json" -Body '{"uin": "7903740631"}'
```

---

#### `/exitRequest`

*(First run a valid `/enterRequest` for UIN 7903740631)*
```powershell
Invoke-WebRequest -Uri http://localhost:5000/enterRequest -Method POST -ContentType "application/json" -Body '{"uin": "7903740631", "precinctID": "0001A"}'
```

**Valid exit — expect `{"authStatus": true, "status": "eligible"}`**
```powershell
Invoke-WebRequest -Uri http://localhost:5000/exitRequest -Method POST -ContentType "application/json" -Body '{"uin": "7903740631", "precinctID": "0001A"}'
```

**Not currently voting (never entered) — expect `{"authStatus": false, "status": "mismatch"}`**
```powershell
Invoke-WebRequest -Uri http://localhost:5000/exitRequest -Method POST -ContentType "application/json" -Body '{"uin": "9406183480", "precinctID": "0002B"}'
```

**Already voted (run immediately after valid exit above) — expect `{"authStatus": false, "status": "mismatch"}`**
```powershell
Invoke-WebRequest -Uri http://localhost:5000/exitRequest -Method POST -ContentType "application/json" -Body '{"uin": "7903740631", "precinctID": "0001A"}'
```

**Missing field — expect `{"authStatus": false, "status": "missing fields"}`**
```powershell
Invoke-WebRequest -Uri http://localhost:5000/exitRequest -Method POST -ContentType "application/json" -Body '{"uin": "7903740631"}'
```

---

### On Mac / Linux / Git Bash

#### `/enterRequest`

**Valid entry — expect `{"authStatus": true, "status": "eligible"}`**
```bash
curl -X POST http://localhost:5000/enterRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "5408602380", "precinctID": "0001A"}'
```

**Already voting (run immediately after the one above) — expect `{"authStatus": false, "status": "mismatch or has voted"}`**
```bash
curl -X POST http://localhost:5000/enterRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "5408602380", "precinctID": "0001A"}'
```

**Wrong precinct — expect `{"authStatus": false, "status": "mismatch or has voted"}`**
```bash
curl -X POST http://localhost:5000/enterRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "8541274095", "precinctID": "0001A"}'
```

**UIN not in DB — expect `{"authStatus": false, "status": "unregistered"}`**
```bash
curl -X POST http://localhost:5000/enterRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "0000000000", "precinctID": "0001A"}'
```

**Missing field — expect `{"authStatus": false, "status": "missing fields"}`**
```bash
curl -X POST http://localhost:5000/enterRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "7903740631"}'
```

---

#### `/exitRequest`

*(First run a valid `/enterRequest` for UIN 7903740631)*
```bash
curl -X POST http://localhost:5000/enterRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "7903740631", "precinctID": "0001A"}'
```

**Valid exit — expect `{"authStatus": true, "status": "eligible"}`**
```bash
curl -X POST http://localhost:5000/exitRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "7903740631", "precinctID": "0001A"}'
```

**Not currently voting (never entered) — expect `{"authStatus": false, "status": "mismatch"}`**
```bash
curl -X POST http://localhost:5000/exitRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "9406183480", "precinctID": "0002B"}'
```

**Already voted (run immediately after valid exit above) — expect `{"authStatus": false, "status": "mismatch"}`**
```bash
curl -X POST http://localhost:5000/exitRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "7903740631", "precinctID": "0001A"}'
```

**Missing field — expect `{"authStatus": false, "status": "missing fields"}`**
```bash
curl -X POST http://localhost:5000/exitRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "7903740631"}'
```

---

## 5. Handing Off to Your Teammate

- **Start the server:** `uvicorn GATE_Auth:app --host 0.0.0.0 --port 5000`
- **Endpoints:** `POST /enterRequest` and `POST /exitRequest`
- **Request format:** JSON body with `uin` (string) and `precinctID` (string)
- **Response format:** `{"authStatus": true/false, "status": "<status string>"}`
- **Required env variable:** `DATABASE_URL` must be set in `db.env` on the server

---

## Quick Reference

| Task                        | Command                                        |
|-----------------------------|------------------------------------------------|
| Install dependencies        | `pip install -r requirements.txt`              |
| Start the server            | `uvicorn GATE_Auth:app --host 0.0.0.0 --port 5000` |
| Reset test data             | Run the UPDATE query in Supabase SQL editor    |
| Test (PowerShell)           | `Invoke-WebRequest ...` (see Section 4)        |
| Test (Mac/Linux/Git Bash)   | `curl -X POST ...` (see Section 4)             |