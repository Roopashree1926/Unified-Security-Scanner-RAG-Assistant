import sqlite3
from pathlib import Path
from datetime import datetime, timezone
import json

# Database file: backend/database/scans.db
DATABASE_PATH = Path(__file__).resolve().parent / "scans.db"


def get_connection():
    """Create a connection to the SQLite database."""
    connection = sqlite3.connect(
        str(DATABASE_PATH),
        timeout=30
    )
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """Create the scan history table if it does not exist."""
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT UNIQUE NOT NULL,
                scanner TEXT NOT NULL,
                target TEXT NOT NULL,
                status TEXT NOT NULL,
                findings TEXT NOT NULL DEFAULT '[]',
                error TEXT,
                created_at TEXT NOT NULL,
                started_at TEXT,
                finished_at TEXT
            )
        """)
        connection.commit()


def save_scan(scan):
    """Insert a new scan or update an existing scan."""
    with get_connection() as connection:
        connection.execute("""
            INSERT INTO scan_history (
                job_id, scanner, target, status, findings,
                error, created_at, started_at, finished_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(job_id) DO UPDATE SET
                scanner = excluded.scanner,
                target = excluded.target,
                status = excluded.status,
                findings = excluded.findings,
                error = excluded.error,
                started_at = excluded.started_at,
                finished_at = excluded.finished_at
        """, (
            scan["job_id"],
            scan["scanner"],
            scan["target"],
            scan["status"],
            json.dumps(scan.get("findings", [])),
            scan.get("error"),
            scan["created_at"],
            scan.get("started_at"),
            scan.get("finished_at")
        ))
        connection.commit()


def get_scan_history(limit=100):
    """Return the most recent scan records."""
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT *
            FROM scan_history
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

    history = []

    for row in rows:
        item = dict(row)
        try:
            item["findings"] = json.loads(item["findings"])
        except (TypeError, json.JSONDecodeError):
            item["findings"] = []

        history.append(item)

    return history


def get_scan_by_job_id(job_id):
    """Retrieve one scan using its job ID."""
    with get_connection() as connection:
        row = connection.execute("""
            SELECT *
            FROM scan_history
            WHERE job_id = ?
        """, (job_id,)).fetchone()

    if row is None:
        return None

    item = dict(row)

    try:
        item["findings"] = json.loads(item["findings"])
    except (TypeError, json.JSONDecodeError):
        item["findings"] = []

    return item


# Ensure the database and table exist when this module is imported.
init_db()
