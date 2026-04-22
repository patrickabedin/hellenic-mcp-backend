"""OAuth2 authentication flow for Google Ads + MCP connector broker support."""
import os
import hashlib
import base64
import secrets
import json
import hmac

# Google may include identity scopes (openid/userinfo) in token response even when
# adwords is requested; do not fail token exchange on broader returned scopes.
os.environ.setdefault("OAUTHLIB_RELAX_TOKEN_SCOPE", "1")
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlencode
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import db

# OAuth2 scopes for Google Ads
SCOPES = ["https://www.googleapis.com/auth/adwords"]

# Secret for signing state tokens (stateless OAuth for ephemeral environments).
# Use GOOGLE_ADS_CLIENT_SECRET as stable fallback so signatures survive restarts.
_state_secret_env = os.getenv("STATE_SECRET") or os.getenv("GOOGLE_ADS_CLIENT_SECRET")
if not _state_secret_env:
    raise RuntimeError(
        "STATE_SECRET or GOOGLE_ADS_CLIENT_SECRET must be set in the environment."
    )
STATE_SECRET = _state_secret_env


def _sign_state(payload: dict) -> str:
    """Sign a state payload with HMAC-SHA256 for tamper-proof state tokens."""
    data = base64.urlsafe_b64encode(json.dumps(payload, sort_keys=True).encode()).decode().rstrip("=")
    sig = base64.urlsafe_b64encode(
        hmac.new(STATE_SECRET.encode(), data.encode(), hashlib.sha256).digest()
    ).decode().rstrip("=")
    return f"{data}.{sig}"


def _verify_state(state: str) -> Optional[dict]:
    """Verify and decode a signed state token."""
    try:
        parts = state.split(".")
        if len(parts) != 2:
            return None
        data, sig = parts
        expected_sig = base64.urlsafe_b64encode(
            hmac.new(STATE_SECRET.encode(), data.encode(), hashlib.sha256).digest()
        ).decode().rstrip("=")
        if not hmac.compare_digest(sig, expected_sig):
            return None
        # Fix base64 padding dynamically
        padding = 4 - (len(data) % 4)
        if padding != 4:
            data += "=" * padding
        payload = json.loads(base64.urlsafe_b64decode(data).decode())
        if payload.get("exp") and payload["exp"] < datetime.utcnow().timestamp():
            return None
        return payload
    except Exception:
        return None


def sign_auth_code(payload: dict) -> str:
    """Sign an auth code payload as a compact JWT-like token."""
    data = base64.urlsafe_b64encode(json.dumps(payload, sort_keys=True).encode()).decode().rstrip("=")
    sig = base64.urlsafe_b64encode(
        hmac.new(STATE_SECRET.encode(), data.encode(), hashlib.sha256).digest()
    ).decode().rstrip("=")
    return f"{data}.{sig}"


def verify_auth_code(code: str) -> Optional[dict]:
    """Verify and decode a signed auth code."""
    try:
        parts = code.split(".")
        if len(parts) != 2:
            return None
        data, sig = parts
        expected_sig = base64.urlsafe_b64encode(
            hmac.new(STATE_SECRET.encode(), data.encode(), hashlib.sha256).digest()
        ).decode().rstrip("=")
        if not hmac.compare_digest(sig, expected_sig):
            return None
        # Fix base64 padding dynamically
        padding = 4 - (len(data) % 4)
        if padding != 4:
            data += "=" * padding
        payload = json.loads(base64.urlsafe_b64decode(data).decode())
        if payload.get("exp") and payload["exp"] < datetime.utcnow().timestamp():
            return None
        return payload
    except Exception:
        return None


def _b64url_sha256(value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")


def verify_pkce(code_verifier: str, code_challenge: str, method: str) -> bool:
    if method != "S256":
        return False
    return _b64url_sha256(code_verifier) == code_challenge


def get_oauth_flow() -> Flow:
    """Create OAuth2 flow instance."""
    client_config = {
        "web": {
            "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [os.getenv("GOOGLE_ADS_REDIRECT_URI")],
        }
    }

    # Keep server-side flow without PKCE to avoid stateless verifier persistence
    # issues with Google callback handling. PKCE is implemented for connector
    # broker token exchange (our own /oauth/authorize + /oauth/token).
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=os.getenv("GOOGLE_ADS_REDIRECT_URI"),
    )
    return flow


def get_auth_url(session_id: str) -> str:
    """Generate Google OAuth URL with persisted PKCE verifier bound to state."""
    client_id = os.getenv("GOOGLE_ADS_CLIENT_ID")
    redirect_uri = os.getenv("GOOGLE_ADS_REDIRECT_URI")
    if not client_id or not redirect_uri:
        raise RuntimeError("Missing GOOGLE_ADS_CLIENT_ID or GOOGLE_ADS_REDIRECT_URI")

    code_verifier = secrets.token_urlsafe(64)
    code_challenge = _b64url_sha256(code_verifier)
    db.store_google_pkce_state(session_id, code_verifier)

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "include_granted_scopes": "true",
        "state": session_id,
        "prompt": "consent",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"


def get_auth_url_for_connector(signed_state: str, code_verifier: str) -> str:
    """Generate Google OAuth URL for connector flow with signed state."""
    client_id = os.getenv("GOOGLE_ADS_CLIENT_ID")
    redirect_uri = os.getenv("GOOGLE_ADS_REDIRECT_URI")
    if not client_id or not redirect_uri:
        raise RuntimeError("Missing GOOGLE_ADS_CLIENT_ID or GOOGLE_ADS_REDIRECT_URI")

    code_challenge = _b64url_sha256(code_verifier)

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "include_granted_scopes": "true",
        "state": signed_state,
        "prompt": "consent",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"


def exchange_code(code: str, session_id: str, code_verifier: str = None) -> dict:
    """Exchange authorization code for Google tokens and return them.
    
    Supports both legacy DB-stored verifiers and stateless flow verifiers
    passed directly from the signed state token.
    """
    flow = get_oauth_flow()

    if not code_verifier:
        # Legacy flow: verifier stored in DB
        code_verifier = db.get_google_pkce_state(session_id)
        if not code_verifier:
            raise RuntimeError("(invalid_grant) Missing code verifier for Google leg. Start a fresh OAuth flow.")
        db.delete_google_pkce_state(session_id)

    # Explicitly set the PKCE verifier on the flow before exchanging
    flow.code_verifier = code_verifier
    flow.fetch_token(code=code)

    credentials = flow.credentials

    # Store in DB (best effort for legacy compatibility)
    try:
        db.store_tokens(
            session_id=session_id,
            access_token=credentials.token,
            refresh_token=credentials.refresh_token,
            expiry=credentials.expiry.isoformat(),
        )
    except Exception:
        pass

    return {
        "session_id": session_id,
        "access_token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "expiry": credentials.expiry.isoformat(),
    }


# Thread-local storage for stateless token payloads (avoids DB dependency)
import threading
_token_context = threading.local()

def set_token_context(payload: dict):
    """Store the decoded bearer token payload for the current request."""
    _token_context.payload = payload

def get_token_context() -> Optional[dict]:
    """Retrieve the decoded bearer token payload for the current request."""
    return getattr(_token_context, 'payload', None)

def clear_token_context():
    """Clear the token context after request processing."""
    _token_context.payload = None

def get_credentials(session_id: str) -> Optional[Credentials]:
    """Retrieve stored credentials for a session.
    
    First checks the stateless token context (no DB needed), then falls back to DB.
    """
    # Try stateless token context first (embedded Google tokens)
    ctx = get_token_context()
    if ctx and ctx.get("session_id") == session_id and ctx.get("google_access_token"):
        credentials = Credentials(
            token=ctx["google_access_token"],
            refresh_token=ctx.get("google_refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv("GOOGLE_ADS_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
            scopes=SCOPES,
        )
        if ctx.get("google_expiry"):
            credentials.expiry = datetime.fromisoformat(ctx["google_expiry"])
        return credentials
    
    # Fallback: DB lookup for legacy tokens
    tokens = db.get_tokens(session_id)
    if not tokens:
        return None

    credentials = Credentials(
        token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_ADS_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
        scopes=SCOPES,
    )

    if tokens["expiry"]:
        credentials.expiry = datetime.fromisoformat(tokens["expiry"])

    return credentials


def refresh_token_if_needed(session_id: str) -> bool:
    """Refresh token if expired or about to expire."""
    credentials = get_credentials(session_id)
    if not credentials:
        return False

    if credentials.expired or (
        credentials.expiry and credentials.expiry < datetime.utcnow() + timedelta(minutes=5)
    ):
        credentials.refresh(Request())

        # Update DB (best effort)
        try:
            db.update_tokens(
                session_id=session_id,
                access_token=credentials.token,
                expiry=credentials.expiry.isoformat(),
            )
        except Exception:
            pass

        # Update token context for stateless operation
        ctx = get_token_context()
        if ctx and ctx.get("session_id") == session_id:
            ctx["google_access_token"] = credentials.token
            ctx["google_expiry"] = credentials.expiry.isoformat()
            set_token_context(ctx)

        return True

    return False
