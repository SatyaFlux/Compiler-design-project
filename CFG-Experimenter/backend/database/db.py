"""
SQLite database connection and schema management.
"""
import os
import sqlite3
import tempfile
from pathlib import Path


def _resolve_db_path() -> Path:
    local_dir = Path(__file__).resolve().parent
    if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME") or not os.access(local_dir, os.W_OK):
        return Path(tempfile.gettempdir()) / "cfg_experimenter.db"
    return local_dir / "cfg_experimenter.db"


DB_PATH = _resolve_db_path()


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path = DB_PATH) -> None:
    conn = get_connection(db_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS experiments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            source_code TEXT NOT NULL,
            grammar_text TEXT NOT NULL,
            status TEXT DEFAULT 'ready',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS grammars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            start_symbol TEXT NOT NULL,
            productions_text TEXT NOT NULL,
            sample_input TEXT DEFAULT '',
            is_preset INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS quiz_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            difficulty TEXT DEFAULT 'Medium',
            question TEXT NOT NULL,
            options_json TEXT NOT NULL,
            correct_index INTEGER NOT NULL,
            explanation TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            answers_json TEXT NOT NULL,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS learning_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_key TEXT UNIQUE NOT NULL,
            completed INTEGER DEFAULT 0,
            last_visited TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
