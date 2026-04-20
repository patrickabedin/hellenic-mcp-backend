"""OAuth2 authentication flow for Google Ads + MCP connector broker support."""
import os
import hashlib
import base64
import secrets
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlencode
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import db

# OAuth2 scopes for Google Ads
SCOPES = ["https://www.googleapis.com/auth/adwords"]


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
    flow.code_verifier = None
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


def exchange_code(code: str, session_id: str) -> dict:
    """Exchange authorization code for Google tokens and store by session_id."""
    flow = get_oauth_flow()

    code_verifier = db.get_google_pkce_state(session_id)
    if not code_verifier:
        raise RuntimeError("(invalid_grant) Missing code verifier for Google leg. Start a fresh OAuth flow.")

    flow.fetch_token(code=code, code_verifier=code_verifier)
    db.delete_google_pkce_state(session_id)

    credentials = flow.credentials

    db.store_tokens(
        session_id=session_id,
        access_token=credentials.token,
        refresh_token=credentials.refresh_token,
        expiry=credentials.expiry.isoformat(),
    )

    return {
        "session_id": session_id,
        "access_token": credentials.token,
        "expiry": credentials.expiry.isoformat(),
    }


def get_credentials(session_id: str) -> Optional[Credentials]:
    """Retrieve stored credentials for a session."""
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

        db.update_tokens(
            session_id=session_id,
            access_token=credentials.token,
            expiry=credentials.expiry.isoformat(),
        )

        return True

    return False
