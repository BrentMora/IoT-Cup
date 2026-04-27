# Setup & Testing Guide
**Project:** IoT-Cup Querying Service  
**Language:** Python (Flask + SQLite for local testing)

---

## Project Structure

```
querying/
├── app.py            # Flask server — handles incoming HTTP requests
├── database.py       # All database logic — query and update
├── init_db.py        # One-time script to create and seed the local test DB
├── requirements.txt  # Python dependencies
└── .env.example      # Template for environment variables
```

---

## 1. First-Time Setup

### Step 1 — Install dependencies
Open a terminal in your project folder and run:
```bash
pip install -r requirements.txt
```

### Step 2 — Create the local test database
Run this **once**. It creates `local_test.db` with a sample `db` table.
```bash
python init_db.py
```

You should see:
```
Seeded 3 sample rows.
Database ready: local_test.db
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

## 3. Testing the API

Open a **second** terminal window (keep the first one running the server).

There are two endpoints to test. A full voter flow is: **entry → exit**.

### Test Data (Seeded by `init_db.py`)

| uin | precinct | voting | voted |
|-----|----------|--------|-------|
| 67  | 67       | 0      | 0     |
| 68  | 68       | 0      | 0     |
| 69  | 69       | 0      | 0     |

---

### On Windows (PowerShell)

> Look for the **`Content`** line in the response output — that's your actual result.

#### `/enterRequest`

**Valid entry (uin exists, right precinct, not yet voting/voted) — expect `{"success": true}`**
```powershell
Invoke-WebRequest -Uri http://localhost:5000/enterRequest -Method POST -ContentType "application/json" -Body '{"uin": "67", "precinct": 67}'
```

**Already voting or voted — expect `{"success": false}`**
```powershell
Invoke-WebRequest -Uri http://localhost:5000/enterRequest -Method POST -ContentType "application/json" -Body '{"uin": "67", "precinct": 67}'
```
*(Run this immediately after the valid entry above — uin 67 is now voting=1)*

**Wrong precinct — expect `{"success": false}`**
```powershell
Invoke-WebRequest -Uri http://localhost:5000/enterRequest -Method POST -ContentType "application/json" -Body '{"uin": "68", "precinct": 99}'
```

**UIN not in DB — expect `{"success": false}`**
```powershell
Invoke-WebRequest -Uri http://localhost:5000/enterRequest -Method POST -ContentType "application/json" -Body '{"uin": "999", "precinct": 67}'
```

**Missing uin field — expect `{"success": false}`**
```powershell
Invoke-WebRequest -Uri http://localhost:5000/enterRequest -Method POST -ContentType "application/json" -Body '{"precinct": 67}'
```

---

#### `/exitRequest`

*(First run a valid `/enterRequest` for uin 68 so it is in voting=1 state)*
```powershell
Invoke-WebRequest -Uri http://localhost:5000/enterRequest -Method POST -ContentType "application/json" -Body '{"uin": "68", "precinct": 68}'
```

**Valid exit (currently voting, not yet voted, right precinct) — expect `{"success": true}`**
```powershell
Invoke-WebRequest -Uri http://localhost:5000/exitRequest -Method POST -ContentType "application/json" -Body '{"uin": "68", "precinct": 68}'
```

**Not currently voting (never entered) — expect `{"success": false}`**
```powershell
Invoke-WebRequest -Uri http://localhost:5000/exitRequest -Method POST -ContentType "application/json" -Body '{"uin": "69", "precinct": 69}'
```

**Already voted (voted=1) — expect `{"success": false}`**
```powershell
Invoke-WebRequest -Uri http://localhost:5000/exitRequest -Method POST -ContentType "application/json" -Body '{"uin": "68", "precinct": 68}'
```
*(Run immediately after the valid exit above — uin 68 is now voted=1)*

---

### On Mac / Linux / Git Bash

#### `/enterRequest`

**Valid entry — expect `{"success": true}`**
```bash
curl -X POST http://localhost:5000/enterRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "67", "precinct": 67}'
```

**Already voting or voted — expect `{"success": false}`**
```bash
curl -X POST http://localhost:5000/enterRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "67", "precinct": 67}'
```
*(Run immediately after the valid entry above)*

**Wrong precinct — expect `{"success": false}`**
```bash
curl -X POST http://localhost:5000/enterRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "68", "precinct": 99}'
```

**UIN not in DB — expect `{"success": false}`**
```bash
curl -X POST http://localhost:5000/enterRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "999", "precinct": 67}'
```

**Missing uin field — expect `{"success": false}`**
```bash
curl -X POST http://localhost:5000/enterRequest \
  -H "Content-Type: application/json" \
  -d '{"precinct": 67}'
```

---

#### `/exitRequest`

*(First run a valid `/enterRequest` for uin 68 so it is in voting=1 state)*
```bash
curl -X POST http://localhost:5000/enterRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "68", "precinct": 68}'
```

**Valid exit — expect `{"success": true}`**
```bash
curl -X POST http://localhost:5000/exitRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "68", "precinct": 68}'
```

**Not currently voting (never entered) — expect `{"success": false}`**
```bash
curl -X POST http://localhost:5000/exitRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "69", "precinct": 69}'
```

**Already voted — expect `{"success": false}`**
```bash
curl -X POST http://localhost:5000/exitRequest \
  -H "Content-Type: application/json" \
  -d '{"uin": "68", "precinct": 68}'
```
*(Run immediately after the valid exit above)*

---

## 4. Switching to the Real Database

Once your teammate provides the database details, only **`database.py`** needs to change. Everything else (`app.py`, `requirements.txt`, etc.) stays the same.

### Step 1 — Install the correct driver

Uncomment the relevant line in `requirements.txt`, then run `pip install -r requirements.txt`:

| Database   | Driver              |
|------------|---------------------|
| PostgreSQL | `psycopg2-binary`   |
| MySQL      | `pymysql`           |
| DynamoDB   | `boto3`             |
| MongoDB    | `pymongo`           |

---

### Step 2 — Update `get_connection()` in `database.py`

Replace the SQLite block with the appropriate driver connection.

**PostgreSQL example:**
```python
import psycopg2

def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))
```

**MySQL example:**
```python
import pymysql

def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
```

---

### Step 3 — Update the SQL in `process_entry()` and `process_exit()`

SQLite uses `?` as a placeholder. Most other databases use `%s`. Update accordingly in both functions:

**SQLite (current):**
```python
cursor.execute("SELECT * FROM db WHERE uin = ?", (input_uin,))
cursor.execute("UPDATE db SET voting = ?, voted = ? WHERE uin = ?", (1, 0, input_uin))
```

**PostgreSQL / MySQL:**
```python
cursor.execute("SELECT * FROM db WHERE uin = %s", (input_uin,))
cursor.execute("UPDATE db SET voting = %s, voted = %s WHERE uin = %s", (1, 0, input_uin))
```

Also update the table name and column names to match the real database schema.

---

### Step 4 — Set environment variables

Copy `.env.example` to `.env` and fill in the real credentials:
```
DATABASE_URL=your_real_connection_string_here
```

> Never commit `.env` to version control. Add it to `.gitignore`.

---

## 5. Handing Off to Your Teammate

Tell your teammate the following:

- **Start the server:** `python app.py` (or `gunicorn -w 4 app:app` for production)
- **Endpoints:** `POST /enterRequest` and `POST /exitRequest`
- **Request format:** JSON body with `uin` (string) and `precinct` (int)
- **Response format:** `{"success": true}` or `{"success": false}`
- **Required env variable:** `DATABASE_URL` must be set on the server

---

## Quick Reference

| Task                        | Command                                |
|-----------------------------|----------------------------------------|
| Install dependencies        | `pip install -r requirements.txt`      |
| Initialize local test DB    | `python init_db.py`                    |
| Start the server            | `python app.py`                        |
| Test (PowerShell)           | `Invoke-WebRequest ...` (see Section 3)|
| Test (Mac/Linux/Git Bash)   | `curl -X POST ...` (see Section 3)     |