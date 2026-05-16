/**
 * logs-endpoint.js
 *
 * Drop this into your existing Express server to expose a GET /logs endpoint
 * that the Live Monitor dashboard can poll every 500 ms.
 *
 * USAGE — add two lines to your existing server file:
 *
 *   const { attachLogCapture, logsRouter } = require('./logs-endpoint');
 *   attachLogCapture();                    // start capturing stdout / stderr
 *   app.use(logsRouter);                  // mount GET /logs
 *
 * Then in the dashboard config, set your AWS Log Endpoint to:
 *   http://<your-server-ip-or-domain>/logs
 */

const { Router } = require('express');

// ─── Configuration ────────────────────────────────────────────────────────────

const MAX_LINES   = 1000;   // rolling buffer size
const CORS_ORIGIN = '*';    // restrict to your dashboard's origin in production
                            // e.g. 'https://mycompany.com'

// ─── Ring buffer ──────────────────────────────────────────────────────────────

const logBuffer = [];   // [{ ts: ISO string, level: string, msg: string }]

function pushLine(level, text) {
  const lines = text.toString().split('\n');
  for (const line of lines) {
    const trimmed = line.trimEnd();
    if (!trimmed) continue;
    logBuffer.push({ ts: new Date().toISOString(), level, msg: trimmed });
    if (logBuffer.length > MAX_LINES) logBuffer.shift();
  }
}

// ─── Stdout / stderr interception ─────────────────────────────────────────────

let captureAttached = false;

function attachLogCapture() {
  if (captureAttached) return;
  captureAttached = true;

  const origOut = process.stdout.write.bind(process.stdout);
  const origErr = process.stderr.write.bind(process.stderr);

  process.stdout.write = (chunk, encoding, cb) => {
    pushLine('INFO', chunk);
    return origOut(chunk, encoding, cb);
  };

  process.stderr.write = (chunk, encoding, cb) => {
    pushLine('ERROR', chunk);
    return origErr(chunk, encoding, cb);
  };

  // Also catch unhandled exceptions so they appear in the dashboard
  process.on('uncaughtException', (err) => {
    pushLine('FATAL', `Uncaught exception: ${err.stack || err.message}`);
  });
  process.on('unhandledRejection', (reason) => {
    pushLine('FATAL', `Unhandled rejection: ${reason}`);
  });

  pushLine('SYS', `Log capture started. Buffer size: ${MAX_LINES} lines.`);
}

// ─── Express router ───────────────────────────────────────────────────────────

const logsRouter = Router();

// CORS pre-flight
logsRouter.options('/logs', (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', CORS_ORIGIN);
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Since');
  res.sendStatus(204);
});

/**
 * GET /logs
 *
 * Query params:
 *   ?since=<ISO timestamp>   Return only lines newer than this timestamp.
 *                            The dashboard sends this automatically when using
 *                            "Append" mode, so each response is just the delta.
 *
 *   ?n=<number>              Return only the last N lines (default: all buffered).
 *
 * Response: plain text, one line per log entry:
 *   [2025-01-15T10:23:01.042Z] [INFO] Server started on port 3000
 */
logsRouter.get('/logs', (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', CORS_ORIGIN);
  res.setHeader('Content-Type', 'text/plain; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store');

  let entries = logBuffer;

  // Filter by timestamp if provided
  if (req.query.since) {
    const since = new Date(req.query.since);
    if (!isNaN(since)) {
      entries = entries.filter(e => new Date(e.ts) > since);
    }
  }

  // Limit by line count if provided
  if (req.query.n) {
    const n = parseInt(req.query.n, 10);
    if (!isNaN(n) && n > 0) entries = entries.slice(-n);
  }

  const body = entries
    .map(e => `[${e.ts}] [${e.level.padEnd(5)}] ${e.msg}`)
    .join('\n');

  res.send(body);
});

// ─── Exports ──────────────────────────────────────────────────────────────────

module.exports = { attachLogCapture, logsRouter, logBuffer, pushLine };


// ─── Standalone test server ───────────────────────────────────────────────────
// Run `node logs-endpoint.js` by itself to verify the endpoint works.

if (require.main === module) {
  const express = require('express');
  const app = express();

  attachLogCapture();
  app.use(logsRouter);

  app.listen(3000, () => {
    console.log('Test server running → http://localhost:3000/logs');
    setInterval(() => {
      const levels = ['INFO', 'INFO', 'INFO', 'WARN', 'ERROR'];
      const msgs   = [
        'Payload received, matching to database…',
        'Match found — record updated.',
        'Lambda invocation complete. Duration: 42ms',
        'Retry attempt 2/3 for record id=8821',
        'Timeout waiting for Supabase response',
      ];
      const i = Math.floor(Math.random() * msgs.length);
      process[levels[i] === 'ERROR' ? 'stderr' : 'stdout'].write(
        `[${levels[i]}] ${msgs[i]}\n`
      );
    }, 1200);
  });
}
