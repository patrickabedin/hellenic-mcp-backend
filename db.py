"""Database module for session token storage and OAuth broker state."""
import sqlite3
import json
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from contextlib import contextmanager

DB_PATH = "sessions.db"


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def _utcnow_iso() -> str:
    return datetime.utcnow().isoformat()


def _iso_after(minutes: int = 0, days: int = 0) -> str:
    return (datetime.utcnow() + timedelta(minutes=minutes, days=days)).isoformat()


def init_db():
    """Initialize the database schema."""
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                access_token TEXT NOT NULL,
                refresh_token TEXT NOT NULL,
                expiry TEXT NOT NULL,
                customer_ids TEXT,
                created_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS oauth_auth_requests (
                request_id TEXT PRIMARY KEY,
                client_id TEXT,
                redirect_uri TEXT NOT NULL,
                state TEXT,
                code_challenge TEXT NOT NULL,
                code_challenge_method TEXT NOT NULL,
                session_id TEXT NOT NULL,
                google_state TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                completed_at TEXT
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS oauth_codes (
                code TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                client_id TEXT,
                redirect_uri TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                used INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS connector_tokens (
                access_token TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                client_id TEXT,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS google_pkce_states (
                state TEXT PRIMARY KEY,
                code_verifier TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS oauth_clients (
                client_id TEXT PRIMARY KEY,
                client_name TEXT,
                redirect_uris TEXT NOT NULL,
                grant_types TEXT,
                response_types TEXT,
                token_endpoint_auth_method TEXT,
                scope TEXT,
                created_at TEXT NOT NULL
            )
            """
        )

        conn.commit()


def store_tokens(
    session_id: str,
    access_token: str,
    refresh_token: str,
    expiry: str,
    customer_ids: Optional[list] = None,
):
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
                _utcnow_iso(),
            ),
        )
        conn.commit()


def get_tokens(session_id: str) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
        ).fetchone()

        if not row:
            return None

        return {
            "session_id": row["session_id"],
            "access_token": row["access_token"],
            "refresh_token": row["refresh_token"],
            "expiry": row["expiry"],
            "customer_ids": json.loads(row["customer_ids"]) if row["customer_ids"] else None,
            "created_at": row["created_at"],
        }


def update_tokens(session_id: str, access_token: str, expiry: str):
    with get_db() as conn:
        conn.execute(
            "UPDATE sessions SET access_token = ?, expiry = ? WHERE session_id = ?",
            (access_token, expiry, session_id),
        )
        conn.commit()


def delete_session(session_id: str):
    with get_db() as conn:
        conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        conn.commit()


def create_auth_request(
    client_id: Optional[str],
    redirect_uri: str,
    state: Optional[str],
    code_challenge: str,
    code_challenge_method: str,
) -> Dict[str, str]:
    request_id = secrets.token_urlsafe(24)
    session_id = secrets.token_urlsafe(24)
    google_state = secrets.token_urlsafe(24)

    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO oauth_auth_requests
            (request_id, client_id, redirect_uri, state, code_challenge, code_challenge_method, session_id, google_state, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request_id,
                client_id,
                redirect_uri,
                state,
                code_challenge,
                code_challenge_method,
                session_id,
                google_state,
                _utcnow_iso(),
            ),
        )
        conn.commit()

    return {
        "request_id": request_id,
        "session_id": session_id,
        "google_state": google_state,
    }


def get_auth_request_by_google_state(google_state: str) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM oauth_auth_requests WHERE google_state = ?", (google_state,)
        ).fetchone()
        return dict(row) if row else None


def mark_auth_request_completed(request_id: str):
    with get_db() as conn:
        conn.execute(
            "UPDATE oauth_auth_requests SET completed_at = ? WHERE request_id = ?",
            (_utcnow_iso(), request_id),
        )
        conn.commit()


def issue_oauth_code(
    request_id: str,
    session_id: str,
    client_id: Optional[str],
    redirect_uri: str,
    ttl_minutes: int = 10,
) -> str:
    code = secrets.token_urlsafe(32)
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO oauth_codes
            (code, request_id, session_id, client_id, redirect_uri, created_at, expires_at, used)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (code, request_id, session_id, client_id, redirect_uri, _utcnow_iso(), _iso_after(minutes=ttl_minutes)),
        )
        conn.commit()
    return code


def get_oauth_code(code: str) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM oauth_codes WHERE code = ?", (code,)).fetchone()
        return dict(row) if row else None


def mark_oauth_code_used(code: str):
    with get_db() as conn:
        conn.execute("UPDATE oauth_codes SET used = 1 WHERE code = ?", (code,))
        conn.commit()


def get_auth_request_by_id(request_id: str) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM oauth_auth_requests WHERE request_id = ?", (request_id,)
        ).fetchone()
        return dict(row) if row else None


def issue_connector_token(
    session_id: str,
    client_id: Optional[str],
    ttl_days: int = 30,
) -> Dict[str, Any]:
    access_token = secrets.token_urlsafe(48)
    created_at = _utcnow_iso()
    expires_at = _iso_after(days=ttl_days)

    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO connector_tokens
            (access_token, session_id, client_id, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (access_token, session_id, client_id, created_at, expires_at),
        )
        conn.commit()

    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": ttl_days * 24 * 3600,
        "expires_at": expires_at,
    }


def get_connector_token(access_token: str) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM connector_tokens WHERE access_token = ?", (access_token,)
        ).fetchone()
        return dict(row) if row else None


def register_oauth_client(
    client_name: Optional[str],
    redirect_uris: list,
    grant_types: Optional[list] = None,
    response_types: Optional[list] = None,
    token_endpoint_auth_method: Optional[str] = None,
    scope: Optional[str] = None,
) -> Dict[str, Any]:
    client_id = secrets.token_urlsafe(24)
    created_at = _utcnow_iso()
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO oauth_clients
            (client_id, client_name, redirect_uris, grant_types, response_types,
             token_endpoint_auth_method, scope, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                client_id,
                client_name,
                json.dumps(redirect_uris or []),
                json.dumps(grant_types or ["authorization_code", "refresh_token"]),
                json.dumps(response_types or ["code"]),
                token_endpoint_auth_method or "none",
                scope or "google_ads",
                created_at,
            ),
        )
        conn.commit()
    return {
        "client_id": client_id,
        "client_name": client_name,
        "redirect_uris": redirect_uris or [],
        "grant_types": grant_types or ["authorization_code", "refresh_token"],
        "response_types": response_types or ["code"],
        "token_endpoint_auth_method": token_endpoint_auth_method or "none",
        "scope": scope or "google_ads",
        "created_at": created_at,
    }


def get_oauth_client(client_id: str) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM oauth_clients WHERE client_id = ?", (client_id,)
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        d["redirect_uris"] = json.loads(d.get("redirect_uris") or "[]")
        d["grant_types"] = json.loads(d.get("grant_types") or "[]")
        d["response_types"] = json.loads(d.get("response_types") or "[]")
        return d


def store_google_pkce_state(state: str, code_verifier: str):
    with get_db() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO google_pkce_states (state, code_verifier, created_at)
            VALUES (?, ?, ?)
            """,
            (state, code_verifier, _utcnow_iso()),
        )
        conn.commit()


def get_google_pkce_state(state: str) -> Optional[str]:
    with get_db() as conn:
        row = conn.execute(
            "SELECT code_verifier FROM google_pkce_states WHERE state = ?", (state,)
        ).fetchone()
        return row["code_verifier"] if row else None


def delete_google_pkce_state(state: str):
    with get_db() as conn:
        conn.execute("DELETE FROM google_pkce_states WHERE state = ?", (state,))
        conn.commit()
