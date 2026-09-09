import os
import sqlite3
from pathlib import Path

# Repo root (parent of this package). Local dev keeps arxiv.db and the
# pipeline's pending.json / results.json here; on the server both are
# redirected via env so the checkout stays read-only for the deploy script.
ROOT = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.environ.get("ARXIV_DB", ROOT / "arxiv.db"))
WORK_DIR = Path(os.environ.get("ARXIV_WORK", ROOT))


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS papers (
                arxiv_id      TEXT PRIMARY KEY,
                title         TEXT NOT NULL,
                authors       TEXT NOT NULL,
                abstract      TEXT,
                submitted_date TEXT,
                fetched_date  TEXT,
                summary       TEXT,
                kept          INTEGER DEFAULT 1,
                read_at       TEXT,
                starred       INTEGER DEFAULT 0,
                rating        INTEGER,
                collaboration TEXT,
                journal_ref   TEXT,
                document_type TEXT,
                inspire_id    TEXT,
                created_at    TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS paper_tags (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                arxiv_id TEXT NOT NULL REFERENCES papers(arxiv_id),
                tag      TEXT NOT NULL,
                UNIQUE(arxiv_id, tag)
            );

            CREATE TABLE IF NOT EXISTS fetched_dates (
                date       TEXT PRIMARY KEY,
                fetched_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS excluded_papers (
                arxiv_id    TEXT PRIMARY KEY,
                excluded_at TEXT DEFAULT (datetime('now'))
            );
        """)
