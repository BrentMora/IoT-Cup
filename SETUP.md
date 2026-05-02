# Setup & Testing Guide
**Project:** IoT-Cup — MOSIP Auth + Voter Querying Service  
**Language:** Python (FastAPI + SQLite for local testing)

---

## Project Structure

```
project/
├── MOSIP_Auth.py     # FastAPI server — MOSIP check, then DB check
├── ID_Payload.py     # Pydantic request model (ScannedIDPayload)
├── database.py       # All database logic — hashing, query, and update
├── init_db.py        # One-time script to create and seed the local test DB
├── config.toml       # MOSIP SDK configuration
└── requirements.txt  # Python dependencies
```

---

## How the System Works

Every request goes through **two layers**:

```
ESP32 → /enterRequest or /exitRequest
           │
           ▼
    [1] MOSIP Auth
        Is this UIN registered in MOSIP and do the demographics match?
           │
     ┌─────┴─────┐
    NO           YES
     │             │
     ▼             ▼
  Return        [2] DB Check
  authStatus:   Is this voter eligible at this precinct?
  false,            │
  "not in       Return authStatus + status
   MOSIP"
```

---

## Response Format

All endpoints return:

```json
{ "authStatus": true/false, "status": "..." }
```

| `authStatus` | `status`                  | Meaning                                                      |
|--------------|---------------------------|--------------------------------------------------------------|
| `false`      | `"not in MOSIP"`          | MOSIP auth failed — wrong name, DOB, address, or UIN        |
| `true`       | `"eligible"`              | Both checks passed — allow entry/exit                        |
| `false`      | `"unregistered"`          | Not in the voter DB                                          |
| `false`      | `"mismatch or has voted"` | Wrong precinct, already voting, or already voted (entry)     |
| `false`      | `"mismatch"`              | Wrong precinct, not currently voting, or already voted (exit)|
| `false`      | `"missing fields"`        | `uin` or `precinctID` missing from payload                   |
| `false`      | `"error"`                 | Unexpected DB error                                          |

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

> Raw UINs are **never stored**. Incoming UINs are SHA-256 hashed in `database.py` before any DB query.

---

## 1. First-Time Setup

### Step 1 — Create and activate a virtual environment
```bash
python -m venv env

# Windows
.\env\Scripts\activate

# Mac / Linux
source env/bin/activate
```

### Step 2 — Install dependencies
```bash
pip install fastapi uvicorn mosip-auth-sdk dynaconf pydantic
```

### Step 3 — Configure MOSIP
Make sure `config.toml` is present and correctly pointed at your MOSIP environment. The SDK reads it automatically on startup.

### Step 4 — Create the local test database
Run this **once**. It creates `local_test.db` with the `voters` table and 4 seeded rows.
```bash
python init_db.py
```

You should see:
```
Seeded 4 sample rows.
Database ready: local_test.db

Seeded UINs (for testing):
  Name                 UIN          precinct_id     id_hash
  -------------------- ------------ --------------- ----------------------------------------------------------------
  Yuki Nakashima       5408602380   1               <hash>
  Haruka Kudou         7903740631   2               <hash>
  Aina Aiba            8541274095   3               <hash>
  Megu Sakuragawa      9406183480   4               <hash>
```

---

## 2. Running the Server

```bash
uvicorn GATE_Auth:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

> Keep this terminal open while testing.  
> The interactive API docs are available at **http://localhost:8000/docs**.

---

## 3. Resetting the Database Between Tests

After a full entry → exit flow, rows are marked `has_voted = TRUE`. Reset to start fresh:
```bash
python init_db.py --reset
```

---

## 4. Test Data

### Voters in the DB

| Name            | UIN        | precinct_id |
|-----------------|------------|-------------|
| Yuki Nakashima  | 5408602380 | 1           |
| Haruka Kudou    | 7903740631 | 2           |
| Aina Aiba       | 8541274095 | 3           |
| Megu Sakuragawa | 9406183480 | 4           |

### Payloads that PASS MOSIP auth

```json
{"uin": "5408602380", "name": "Yuki Nakashima", "dob": "1997/09/12", "location1": "Quezon City", "location3": "Metropolitan Manila Second District", "zone": "U.P. Campus", "postal_code": "11101", "address_line1": "UP AECH", "address_line2": "Velasquez St.", "address_line3": "UP Diliman"}
```
```json
{"uin": "7903740631", "name": "Haruka Kudou", "dob": "1989/03/16", "location1": "Quezon City", "location3": "Metropolitan Manila Second District", "zone": "U.P. Campus", "postal_code": "11101", "address_line1": "Melchor Hall", "address_line2": "Osmena Avenue", "address_line3": "UP Diliman"}
```
```json
{"uin": "8541274095", "name": "Aina Aiba", "dob": "1988/10/17", "location1": "Quezon City", "location3": "Metropolitan Manila Second District", "zone": "Central", "postal_code": "11100", "address_line1": "Circle of Fun", "address_line2": "Quezon Memorial Circle", "address_line3": "Elliptical Road"}
```
```json
{"uin": "9406183480", "name": "Megu Sakuragawa", "dob": "2022/10/24", "location1": "Angeles City", "location3": "Pampanga", "zone": "Malabanñas", "postal_code": "12023", "address_line1": "SM Clark", "address_line2": "Manuel A Roxas Highway", "address_line3": "Clark"}
```

### Payloads that FAIL MOSIP auth

| Why it fails | Payload |
|---|---|
| Wrong name + DOB for that UIN | `{"uin": "8541274095", "name": "Kanon Shizaki", "dob": "1997/09/12"}` |
| Wrong address for that UIN | `{"uin": "7903740631", "name": "Yuki Nakashima", "dob": "1997/09/12", "location1": "Angeles City", "location3": "Pampanga", "zone": "Malabanñas", "postal_code": "12023", "address_line1": "Cityfront Mall", "address_line2": "Manuel A Roxas Highway", "address_line3": "Clark"}` |
| Wrong postal code for that UIN | `{"uin": "8541274095", "name": "Aina Aiba", "dob": "1988/10/17", "location1": "Quezon City", "location3": "Metropolitan Manila Second District", "zone": "Central", "postal_code": "12023", "address_line1": "Circle of Fun", "address_line2": "Quezon Memorial Circle", "address_line3": "Elliptical Road"}` |

---

## 5. Testing the API

Open a **second** terminal (keep the first one running the server).

A full voter flow is: **entry → exit**. Always run `python init_db.py --reset` between full test runs.

---

### On Windows (PowerShell)

> Look for the **`Content`** line in the response output — that's your actual result.

---

#### Passing MOSIP → Valid DB entry — expect `{"authStatus": true, "status": "eligible"}`
```powershell
Invoke-WebRequest -Uri http://localhost:8000/enterRequest -Method POST -ContentType "application/json" -Body '{"uin": "5408602380", "name": "Yuki Nakashima", "dob": "1997/09/12", "location1": "Quezon City", "location3": "Metropolitan Manila Second District", "zone": "U.P. Campus", "postal_code": "11101", "address_line1": "UP AECH", "address_line2": "Velasquez St.", "address_line3": "UP Diliman", "precinctID": "1"}'
```

#### Passing MOSIP → Already voting (run same request again) — expect `{"authStatus": false, "status": "mismatch or has voted"}`
```powershell
Invoke-WebRequest -Uri http://localhost:8000/enterRequest -Method POST -ContentType "application/json" -Body '{"uin": "5408602380", "name": "Yuki Nakashima", "dob": "1997/09/12", "location1": "Quezon City", "location3": "Metropolitan Manila Second District", "zone": "U.P. Campus", "postal_code": "11101", "address_line1": "UP AECH", "address_line2": "Velasquez St.", "address_line3": "UP Diliman", "precinctID": "1"}'
```

#### Passing MOSIP → Wrong precinct — expect `{"authStatus": false, "status": "mismatch or has voted"}`
```powershell
Invoke-WebRequest -Uri http://localhost:8000/enterRequest -Method POST -ContentType "application/json" -Body '{"uin": "7903740631", "name": "Haruka Kudou", "dob": "1989/03/16", "location1": "Quezon City", "location3": "Metropolitan Manila Second District", "zone": "U.P. Campus", "postal_code": "11101", "address_line1": "Melchor Hall", "address_line2": "Osmena Avenue", "address_line3": "UP Diliman", "precinctID": "99"}'
```

#### Passing MOSIP → UIN not in DB — expect `{"authStatus": false, "status": "unregistered"}`

*(This UIN passes MOSIP but was never seeded into the local DB)*
```powershell
Invoke-WebRequest -Uri http://localhost:8000/enterRequest -Method POST -ContentType "application/json" -Body '{"uin": "9406183480", "name": "Megu Sakuragawa", "dob": "2022/10/24", "location1": "Angeles City", "location3": "Pampanga", "zone": "Malabannas", "postal_code": "12023", "address_line1": "SM Clark", "address_line2": "Manuel A Roxas Highway", "address_line3": "Clark", "precinctID": "99"}'
```

#### Failing MOSIP — wrong name/DOB — expect `{"authStatus": false, "status": "not in MOSIP"}`
```powershell
Invoke-WebRequest -Uri http://localhost:8000/enterRequest -Method POST -ContentType "application/json" -Body '{"uin": "8541274095", "name": "Kanon Shizaki", "dob": "1997/09/12", "precinctID": "3"}'
```

#### Failing MOSIP — wrong address — expect `{"authStatus": false, "status": "not in MOSIP"}`
```powershell
Invoke-WebRequest -Uri http://localhost:8000/enterRequest -Method POST -ContentType "application/json" -Body '{"uin": "7903740631", "name": "Yuki Nakashima", "dob": "1997/09/12", "location1": "Angeles City", "location3": "Pampanga", "zone": "Malabannas", "postal_code": "12023", "address_line1": "Cityfront Mall", "address_line2": "Manuel A Roxas Highway", "address_line3": "Clark", "precinctID": "2"}'
```

#### Failing MOSIP — wrong postal code — expect `{"authStatus": false, "status": "not in MOSIP"}`
```powershell
Invoke-WebRequest -Uri http://localhost:8000/enterRequest -Method POST -ContentType "application/json" -Body '{"uin": "8541274095", "name": "Aina Aiba", "dob": "1988/10/17", "location1": "Quezon City", "location3": "Metropolitan Manila Second District", "zone": "Central", "postal_code": "12023", "address_line1": "Circle of Fun", "address_line2": "Quezon Memorial Circle", "address_line3": "Elliptical Road", "precinctID": "3"}'
```

---

#### `/exitRequest` flow

*(First, run a valid `/enterRequest` for Haruka Kudou)*
```powershell
Invoke-WebRequest -Uri http://localhost:8000/enterRequest -Method POST -ContentType "application/json" -Body '{"uin": "7903740631", "name": "Haruka Kudou", "dob": "1989/03/16", "location1": "Quezon City", "location3": "Metropolitan Manila Second District", "zone": "U.P. Campus", "postal_code": "11101", "address_line1": "Melchor Hall", "address_line2": "Osmena Avenue", "address_line3": "UP Diliman", "precinctID": "2"}'
```

**Valid exit — expect `{"authStatus": true, "status": "eligible"}`**
```powershell
Invoke-WebRequest -Uri http://localhost:8000/exitRequest -Method POST -ContentType "application/json" -Body '{"uin": "7903740631", "name": "Haruka Kudou", "dob": "1989/03/16", "location1": "Quezon City", "location3": "Metropolitan Manila Second District", "zone": "U.P. Campus", "postal_code": "11101", "address_line1": "Melchor Hall", "address_line2": "Osmena Avenue", "address_line3": "UP Diliman", "precinctID": "2"}'
```

**Not currently voting (never entered) — expect `{"authStatus": false, "status": "mismatch"}`**
```powershell
Invoke-WebRequest -Uri http://localhost:8000/exitRequest -Method POST -ContentType "application/json" -Body '{"uin": "8541274095", "name": "Aina Aiba", "dob": "1988/10/17", "location1": "Quezon City", "location3": "Metropolitan Manila Second District", "zone": "Central", "postal_code": "11100", "address_line1": "Circle of Fun", "address_line2": "Quezon Memorial Circle", "address_line3": "Elliptical Road", "precinctID": "3"}'
```

**Already voted (run exit for Haruka again) — expect `{"authStatus": false, "status": "mismatch"}`**
```powershell
Invoke-WebRequest -Uri http://localhost:8000/exitRequest -Method POST -ContentType "application/json" -Body '{"uin": "7903740631", "name": "Haruka Kudou", "dob": "1989/03/16", "location1": "Quezon City", "location3": "Metropolitan Manila Second District", "zone": "U.P. Campus", "postal_code": "11101", "address_line1": "Melchor Hall", "address_line2": "Osmena Avenue", "address_line3": "UP Diliman", "precinctID": "2"}'
```

---

### On Mac / Linux / Git Bash

#### Passing MOSIP → Valid DB entry — expect `{"authStatus": true, "status": "eligible"}`
```bash
curl -X POST http://localhost:8000/enterRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "5408602380", "name": "Yuki Nakashima", "dob": "1997/09/12", "location1": "Quezon City", "location3": "Metropolitan Manila Second District", "zone": "U.P. Campus", "postal_code": "11101", "address_line1": "UP AECH", "address_line2": "Velasquez St.", "address_line3": "UP Diliman", "precinctID": "1"}'
```

#### Passing MOSIP → Already voting (run same request again) — expect `{"authStatus": false, "status": "mismatch or has voted"}`
```bash
curl -X POST http://localhost:8000/enterRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "5408602380", "name": "Yuki Nakashima", "dob": "1997/09/12", "location1": "Quezon City", "location3": "Metropolitan Manila Second District", "zone": "U.P. Campus", "postal_code": "11101", "address_line1": "UP AECH", "address_line2": "Velasquez St.", "address_line3": "UP Diliman", "precinctID": "1"}'
```

#### Passing MOSIP → Wrong precinct — expect `{"authStatus": false, "status": "mismatch or has voted"}`
```bash
curl -X POST http://localhost:8000/enterRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "7903740631", "name": "Haruka Kudou", "dob": "1989/03/16", "location1": "Quezon City", "location3": "Metropolitan Manila Second District", "zone": "U.P. Campus", "postal_code": "11101", "address_line1": "Melchor Hall", "address_line2": "Osmena Avenue", "address_line3": "UP Diliman", "precinctID": "99"}'
```

#### Passing MOSIP → UIN not in DB — expect `{"authStatus": false, "status": "unregistered"}`
```bash
curl -X POST http://localhost:8000/enterRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "9406183480", "name": "Megu Sakuragawa", "dob": "2022/10/24", "location1": "Angeles City", "location3": "Pampanga", "zone": "Malabannas", "postal_code": "12023", "address_line1": "SM Clark", "address_line2": "Manuel A Roxas Highway", "address_line3": "Clark", "precinctID": "99"}'
```

#### Failing MOSIP — wrong name/DOB — expect `{"authStatus": false, "status": "not in MOSIP"}`
```bash
curl -X POST http://localhost:8000/enterRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "8541274095", "name": "Kanon Shizaki", "dob": "1997/09/12", "precinctID": "3"}'
```

#### Failing MOSIP — wrong address — expect `{"authStatus": false, "status": "not in MOSIP"}`
```bash
curl -X POST http://localhost:8000/enterRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "7903740631", "name": "Yuki Nakashima", "dob": "1997/09/12", "location1": "Angeles City", "location3": "Pampanga", "zone": "Malabannas", "postal_code": "12023", "address_line1": "Cityfront Mall", "address_line2": "Manuel A Roxas Highway", "address_line3": "Clark", "precinctID": "2"}'
```

#### Failing MOSIP — wrong postal code — expect `{"authStatus": false, "status": "not in MOSIP"}`
```bash
curl -X POST http://localhost:8000/enterRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "8541274095", "name": "Aina Aiba", "dob": "1988/10/17", "location1": "Quezon City", "location3": "Metropolitan Manila Second District", "zone": "Central", "postal_code": "12023", "address_line1": "Circle of Fun", "address_line2": "Quezon Memorial Circle", "address_line3": "Elliptical Road", "precinctID": "3"}'
```

---

#### `/exitRequest` flow

*(First, run a valid `/enterRequest` for Haruka Kudou)*
```bash
curl -X POST http://localhost:8000/enterRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "7903740631", "name": "Haruka Kudou", "dob": "1989/03/16", "location1": "Quezon City", "location3": "Metropolitan Manila Second District", "zone": "U.P. Campus", "postal_code": "11101", "address_line1": "Melchor Hall", "address_line2": "Osmena Avenue", "address_line3": "UP Diliman", "precinctID": "2"}'
```

**Valid exit — expect `{"authStatus": true, "status": "eligible"}`**
```bash
curl -X POST http://localhost:8000/exitRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "7903740631", "name": "Haruka Kudou", "dob": "1989/03/16", "location1": "Quezon City", "location3": "Metropolitan Manila Second District", "zone": "U.P. Campus", "postal_code": "11101", "address_line1": "Melchor Hall", "address_line2": "Osmena Avenue", "address_line3": "UP Diliman", "precinctID": "2"}'
```

**Not currently voting (never entered) — expect `{"authStatus": false, "status": "mismatch"}`**
```bash
curl -X POST http://localhost:8000/exitRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "8541274095", "name": "Aina Aiba", "dob": "1988/10/17", "location1": "Quezon City", "location3": "Metropolitan Manila Second District", "zone": "Central", "postal_code": "11100", "address_line1": "Circle of Fun", "address_line2": "Quezon Memorial Circle", "address_line3": "Elliptical Road", "precinctID": "3"}'
```

**Already voted (run exit for Haruka again) — expect `{"authStatus": false, "status": "mismatch"}`**
```bash
curl -X POST http://localhost:8000/exitRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "7903740631", "name": "Haruka Kudou", "dob": "1989/03/16", "location1": "Quezon City", "location3": "Metropolitan Manila Second District", "zone": "U.P. Campus", "postal_code": "11101", "address_line1": "Melchor Hall", "address_line2": "Osmena Avenue", "address_line3": "UP Diliman", "precinctID": "2"}'
```

---

## 6. Switching to the Real Database (Supabase / PostgreSQL)

### Step 1 — Install the PostgreSQL driver
```bash
pip install psycopg2-binary
```

### Step 2 — Update `get_connection()` in `database.py`
```python
import psycopg2

def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))
```

### Step 3 — Update placeholder syntax in `database.py`

SQLite uses `?`, PostgreSQL uses `%s`. Update all queries in `process_entry` and `process_exit`:

```python
cursor.execute("SELECT * FROM voters WHERE id_hash = %s", (id_hash,))

cursor.execute(
    "UPDATE voters SET is_voting = %s, updated_at = CURRENT_TIMESTAMP WHERE id_hash = %s",
    (True, id_hash)
)

cursor.execute(
    "UPDATE voters SET has_voted = %s, is_voting = %s, updated_at = CURRENT_TIMESTAMP WHERE id_hash = %s",
    (True, False, id_hash)
)
```

### Step 4 — Set the environment variable
```bash
export DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
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

## Quick Reference

| Task                        | Command                                                           |
|-----------------------------|-------------------------------------------------------------------|
| Activate virtual env (Win)  | `.\env\Scripts\activate`                                          |
| Activate virtual env (Mac)  | `source env/bin/activate`                                         |
| Install dependencies        | `pip install fastapi uvicorn mosip-auth-sdk dynaconf pydantic`    |
| Initialize local test DB    | `python init_db.py`                                               |
| Reset DB between tests      | `python init_db.py --reset`                                       |
| Start the server            | `uvicorn MOSIP_Auth:app --reload`                                 |
| View interactive API docs   | `http://localhost:8000/docs`                                      |
| Test (PowerShell)           | `Invoke-WebRequest ...` (see Section 5)                           |
| Test (Mac/Linux/Git Bash)   | `curl -X POST ...` (see Section 5)                                |