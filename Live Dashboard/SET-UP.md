# Live Monitor — Setup Guide

A real-time dashboard that displays live Supabase table data and streams server logs from an Express backend. No build step required — it's a single HTML file.

---

## Prerequisites

| Requirement | Details |
|---|---|
| Supabase project | Free tier is fine. Realtime must be enabled for your table. |
| Node.js server | Any Express app (v4+) you want to monitor. |
| A browser | Any modern browser (Chrome, Firefox, Edge, Safari). |

---

## Part 1 — Open the Dashboard

The dashboard is a self-contained HTML file with no build step.

**Option A — Open directly in your browser**

```
double-click dashboard.html
```

This works for local use. Because the file makes fetch requests to your Express server, both must run on the same machine or you must allow CORS from your file's origin.

**Option B — Serve it with a static file server (recommended)**

```bash
npx serve .
# or
python3 -m http.server 8080
```

Then visit `http://localhost:8080/dashboard.html`.

---

## Part 2 — Add the Log Endpoint to your Express Server

Copy `logs-endpoint.js` into your project, then add **two lines** to your existing server file:

```js
// At the top of your server entry point:
const { attachLogCapture, logsRouter } = require('./logs-endpoint');

// After you create your Express app:
attachLogCapture();   // intercepts stdout / stderr into a rolling buffer
app.use(logsRouter);  // mounts GET /logs
```

**Full minimal example:**

```js
const express = require('express');
const { attachLogCapture, logsRouter } = require('./logs-endpoint');

const app = express();
attachLogCapture();
app.use(logsRouter);

app.listen(3000, () => console.log('Server running on port 3000'));
```

Start your server:

```bash
node server.js
```

Verify the endpoint works by visiting `http://localhost:3000/logs` in your browser — you should see plain-text log output.

**Test without your own server:**

```bash
node logs-endpoint.js
```

This spins up a standalone test server on port 3000 that emits simulated log lines every 1.2 seconds.

---

## Part 3 — Configure the Dashboard

1. Open the dashboard and click **⚙ Config**.
2. Fill in the fields:

| Field | What to enter |
|---|---|
| **Supabase Project URL** | e.g. `https://abcdefgh.supabase.co` |
| **Supabase Anon Key** | Found in Supabase → Project Settings → API |
| **Table Name** | The table you want to monitor, e.g. `my_table` |
| **AWS Log Endpoint URL** | `http://localhost:3000/logs` (or your server's address) |
| **Log Format** | Leave as *Plain text* unless your endpoint returns JSON |

3. Click **Connect →**.

Your settings are saved to `localStorage` and restored automatically on next open.

---

## Part 4 — Enable Supabase Realtime

In the **Supabase dashboard**, go to your project → **Database** → **Replication** and toggle Realtime on for your table.

Then run this SQL once in the Supabase SQL Editor:

```sql
ALTER TABLE your_table REPLICA IDENTITY FULL;
```

This is required for `UPDATE` and `DELETE` events to include the old row data.

---

## How the Log Polling Works

The dashboard polls `GET /logs` every **500 ms**. After the first fetch it appends `?since=<ISO timestamp>` so each response only includes new lines — no duplication, minimal bandwidth.

The endpoint keeps a rolling in-memory buffer of the last **1,000 lines**. Lines from `stdout` are tagged `INFO`; lines from `stderr` are tagged `ERROR`. Unhandled exceptions and promise rejections are captured automatically as `FATAL`.

---

## Troubleshooting

**"poll failed" in the log status indicator**
→ Check that your Express server is running and the Log Endpoint URL matches exactly (including `http://` and the correct port).

**CORS errors in the browser console**
→ By default `logs-endpoint.js` allows all origins (`*`). If you're still seeing CORS errors, confirm `app.use(logsRouter)` is called *after* any other middleware that might be blocking OPTIONS requests.

**Supabase shows "channel error"**
→ Verify Realtime is enabled for the table in the Supabase dashboard and that your Anon Key has `SELECT` permissions.

**No rows appear in the table**
→ Confirm the Table Name field matches exactly (case-sensitive). Click **↺ refresh** to force a manual fetch.
