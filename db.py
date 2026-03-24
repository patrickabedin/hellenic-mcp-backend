"""Database module for session token storage."""
import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Any
from contextlib import contextmanager

DB_PATH = "sessions.db"

def init_db():
    """Initialize the database schema."""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                access_token TEXT NOT NULL,
                refresh_token TEXT NOT NULL,
                expiry TEXT NOT NULL,
                customer_ids TEXT,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()

@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def store_tokens(
    session_id: str,
    access_token: str,
    refresh_token: str,
    expiry: str,
    customer_ids: Optional[list] = None
):
    """Store OAuth tokens for a session."""
    with get_db() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO sessions 
            (session_id, access_token, refresh_token, expiry, customer_ids, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                access_token,
                refresh_token,
                expiry,
                json.dumps(customer_ids) if customer_ids else None,
                datetime.utcnow().isoformat()
            )
        )
        conn.commit()

def get_tokens(session_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve tokens for a session."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM sessions WHERE session_id = ?",
            (session_id,)
        ).fetchone()
        
        if not row:
            return None
        
        return {
            "session_id": row["session_id"],
            "access_token": row["access_token"],
            "refresh_token": row["refresh_token"],
            "expiry": row["expiry"],
            "customer_ids": json.loads(row["customer_ids"]) if row["customer_ids"] else None,
            "created_at": row["created_at"]
        }

def update_tokens(session_id: str, access_token: str, expiry: str):
    """Update access token after refresh."""
    with get_db() as conn:
        conn.execute(
            "UPDATE sessions SET access_token = ?, expiry = ? WHERE session_id = ?",
            (access_token, expiry, session_id)
        )
        conn.commit()

def delete_session(session_id: str):
    """Delete a session."""
    with get_db() as conn:
        conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        conn.commit()
