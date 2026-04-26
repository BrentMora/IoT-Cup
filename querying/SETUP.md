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
Run this **once**. It creates `local_test.db` with a sample `items` table.
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

### On Windows (PowerShell)

**Test with a valid ID — expect `{"success": true}`**
```powershell
Invoke-WebRequest -Uri http://localhost:5000/process -Method POST -ContentType "application/json" -Body '{"uin": "67", "precinct": 67}'
```

**Test with an invalid ID — expect `{"success": false}`**
```powershell
Invoke-WebRequest -Uri http://localhost:5000/process -Method POST -ContentType "application/json" -Body '{"uin": "70", "precinct": 69}'
```

**Test an invalid precinct — expect `{"success": false}`**
```powershell
Invoke-WebRequest -Uri http://localhost:5000/process -Method POST -ContentType "application/json" -Body '{"uin": "68", "precinct": 69}'
```

> In PowerShell, look for the **`Content`** line in the response output — that's your actual result.

---

### On Mac / Linux / Git Bash

**Test with a valid ID — expect `{"success": true}`**
```bash
curl -X POST http://localhost:5000/process \
  -H "Content-Type: application/json" \
  -d '{"uin": "67", "precinct": 67}'
```

**Test with an invalid ID — expect `{"success": false}`**
```bash
curl -X POST http://localhost:5000/process \
  -H "Content-Type: application/json" \
  -d '{"uin": "70", "precinct": 69}'
```

**Test an invalid precinct — expect `{"success": false}`**
```bash
curl -X POST http://localhost:5000/process \
  -H "Content-Type: application/json" \
  -d '{"uin": "68", "precinct": 69}'
```

---

## 4. Switching to the Real Database

Once database is done only **`database.py`** needs to change. Everything else (`app.py`, `requirements.txt`, etc.) stays the same.

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

### Step 3 — Update the SQL in `query_and_update()`

SQLite uses `?` as a placeholder. Most other databases use `%s`. Update accordingly:

**SQLite (current):**
```python
cursor.execute("SELECT * FROM items WHERE id = ?", (record_id,))
cursor.execute("UPDATE items SET status = ? WHERE id = ?", (new_status, record_id))
```

**PostgreSQL / MySQL:**
```python
cursor.execute("SELECT * FROM items WHERE id = %s", (record_id,))
cursor.execute("UPDATE items SET status = %s WHERE id = %s", (new_status, record_id))
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

## 5. Handing Off

- **Start the server:** `python app.py` (or `gunicorn -w 4 app:app` for production)
- **Endpoint:** `POST /process`
- **Request format:** JSON body with `id` (int) and `status` (string)
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
