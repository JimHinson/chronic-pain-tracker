"""
database.py – SQLite persistence layer for the Chronic Pain Tracker.

The schema is intentionally forward-compatible: columns for weather, activity,
and diet are present from the start but default to NULL so the app keeps
working before those features are enabled.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path("pain_tracker.db")

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS pain_entries (
    id              INTEGER  PRIMARY KEY AUTOINCREMENT,
    timestamp       DATETIME NOT NULL,
    pain_location   TEXT     NOT NULL,
    pain_level      INTEGER  NOT NULL CHECK(pain_level >= 0 AND pain_level <= 10),
    notes           TEXT,
    -- Future: weather integration
    weather_temp_f  REAL,
    weather_humidity_pct REAL,
    weather_condition    TEXT,
    -- Future: activity log
    activity_type       TEXT,
    activity_intensity  TEXT,
    -- Future: diet log
    diet_notes          TEXT
)
"""


@contextmanager
def _get_conn():
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    """Create the database and tables if they do not exist."""
    with _get_conn() as conn:
        conn.execute(CREATE_TABLE_SQL)


def add_entry(
    timestamp: str,
    pain_location: str,
    pain_level: int,
    notes: str = "",
) -> int:
    """Insert a new pain entry and return the new row id."""
    sql = """
        INSERT INTO pain_entries (timestamp, pain_location, pain_level, notes)
        VALUES (?, ?, ?, ?)
    """
    with _get_conn() as conn:
        cur = conn.execute(sql, (timestamp, pain_location, pain_level, notes))
        return cur.lastrowid


def get_recent_entries(limit: int = 10) -> list[dict]:
    """Return the *limit* most recent entries, newest first."""
    sql = """
        SELECT id, timestamp, pain_location, pain_level, notes
        FROM pain_entries
        ORDER BY timestamp DESC
        LIMIT ?
    """
    with _get_conn() as conn:
        rows = conn.execute(sql, (limit,)).fetchall()
    return [dict(r) for r in rows]


def get_all_entries() -> list[dict]:
    """Return every entry ordered from oldest to newest (for trend charts)."""
    sql = """
        SELECT id, timestamp, pain_location, pain_level, notes
        FROM pain_entries
        ORDER BY timestamp ASC
    """
    with _get_conn() as conn:
        rows = conn.execute(sql).fetchall()
    return [dict(r) for r in rows]


def delete_entry(entry_id: int) -> None:
    """Remove a single entry by its primary key."""
    with _get_conn() as conn:
        conn.execute("DELETE FROM pain_entries WHERE id = ?", (entry_id,))
