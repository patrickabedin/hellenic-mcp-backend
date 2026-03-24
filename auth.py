"""OAuth2 authentication flow for Google Ads."""
import os
from datetime import datetime, timedelta
from typing import Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import db

# OAuth2 scopes for Google Ads
SCOPES = ['https://www.googleapis.com/auth/adwords']

def get_oauth_flow() -> Flow:
    """Create OAuth2 flow instance."""
    client_config = {
        "web": {
            "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [os.getenv("GOOGLE_ADS_REDIRECT_URI")]
        }
    }
    
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=os.getenv("GOOGLE_ADS_REDIRECT_URI")
    )
    return flow

def get_auth_url(session_id: str) -> str:
    """Generate OAuth2 authorization URL."""
    flow = get_oauth_flow()
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        state=session_id,
        prompt='consent'  # Force consent screen to get refresh token
    )
    return auth_url

def exchange_code(code: str, session_id: str) -> dict:
    """Exchange authorization code for tokens."""
    flow = get_oauth_flow()
    flow.fetch_token(code=code)
    
    credentials = flow.credentials
    
    # Store tokens in database
    db.store_tokens(
        session_id=session_id,
        access_token=credentials.token,
        refresh_token=credentials.refresh_token,
        expiry=credentials.expiry.isoformat()
    )
    
    return {
        "session_id": session_id,
        "access_token": credentials.token,
        "expiry": credentials.expiry.isoformat()
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
        scopes=SCOPES
    )
    
    # Set expiry
    if tokens["expiry"]:
        credentials.expiry = datetime.fromisoformat(tokens["expiry"])
    
    return credentials

def refresh_token_if_needed(session_id: str) -> bool:
    """Refresh token if expired or about to expire."""
    credentials = get_credentials(session_id)
    if not credentials:
        return False
    
    # Refresh if expired or expires in next 5 minutes
    if credentials.expired or (
        credentials.expiry and 
        credentials.expiry < datetime.utcnow() + timedelta(minutes=5)
    ):
        credentials.refresh(Request())
        
        # Update stored tokens
        db.update_tokens(
            session_id=session_id,
            access_token=credentials.token,
            expiry=credentials.expiry.isoformat()
        )
        
        return True
    
    return False
