"""Main FastAPI application for Hellenic Google Ads MCP Server."""
import os
import secrets
from typing import Optional, Any, Dict
from urllib.parse import urlencode
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from mcp.server.sse import SseServerTransport
from mcp.server.stdio import stdio_server
import uvicorn

import db
import auth
from mcp_server import mcp_server, TOOLS, call_tool as mcp_call_tool

BASE_URL = os.getenv("PUBLIC_BASE_URL", "https://api.google-ads-mcp.hellenicai.com").rstrip("/")
OAUTH_ISSUER = BASE_URL

# Load environment variables
load_dotenv()

# Initialize database
db.init_db()

# Create FastAPI app
app = FastAPI(
    title="Hellenic Google Ads MCP Server",
    description="Multi-tenant MCP server for Google Ads API access",
    version="1.0.1"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Landing page with connection instructions."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hellenic Google Ads MCP Server</title>
        <style>
            body {
                font-family: system-ui, -apple-system, sans-serif;
                max-width: 800px;
                margin: 40px auto;
                padding: 20px;
                line-height: 1.6;
                color: #333;
            }
            h1 { color: #0066cc; }
            code {
                background: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-size: 0.9em;
            }
            pre {
                background: #f4f4f4;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
            }
            .section {
                margin: 30px 0;
            }
            .endpoint {
                background: #e8f4f8;
                padding: 10px;
                border-left: 4px solid #0066cc;
                margin: 10px 0;
            }
        </style>
    </head>
    <body>
        <h1>🚀 Hellenic Google Ads MCP Server</h1>
        <p>Production-ready remote MCP server for Google Ads API access by <strong>Hellenic Technologies</strong>.</p>
        
        <div class="section">
            <h2>📡 MCP Endpoint</h2>
            <div class="endpoint">
                <strong>HTTP + SSE:</strong> <code>https://google-ads-mcp.hellenicai.com/mcp</code>
            </div>
            <p>Use this URL in Claude Desktop, ChatGPT, or any MCP-compatible client.</p>
        </div>
        
        <div class="section">
            <h2>🔗 Quick Connect</h2>
            <h3>Claude Desktop</h3>
            <p>Add to <code>claude_desktop_config.json</code>:</p>
            <pre>{
  "mcpServers": {
    "google-ads": {
      "url": "https://google-ads-mcp.hellenicai.com/mcp",
      "transport": "sse"
    }
  }
}</pre>
            
            <h3>OpenAI Desktop / Gemini</h3>
            <p>Use the URL: <code>https://google-ads-mcp.hellenicai.com/mcp</code></p>
        </div>
        
        <div class="section">
            <h2>🔐 Authentication Flow</h2>
            <ol>
                <li>Client generates a unique <code>session_id</code></li>
                <li>Call <code>connect_google_ads</code> tool with your session_id</li>
                <li>Open the returned OAuth URL in your browser</li>
                <li>Authorize access to your Google Ads account</li>
                <li>Subsequent tool calls use your session_id to access your data</li>
            </ol>
        </div>
        
        <div class="section">
            <h2>🛠️ Available Tools</h2>
            <ul>
                <li><code>connect_google_ads</code> - Start OAuth flow</li>
                <li><code>list_accounts</code> - List accessible accounts</li>
                <li><code>get_account_summary</code> - Account performance metrics</li>
                <li><code>list_campaigns</code> - All campaigns</li>
                <li><code>get_campaign_performance</code> - Campaign metrics</li>
                <li><code>list_ad_groups</code> - Ad groups for a campaign</li>
                <li><code>get_keywords</code> - Keyword performance + quality scores</li>
                <li><code>get_search_terms_report</code> - Search queries triggering ads</li>
                <li><code>pause_campaign</code> - Pause a campaign</li>
                <li><code>enable_campaign</code> - Enable a campaign</li>
                <li><code>update_campaign_budget</code> - Change daily budget</li>
            </ul>
        </div>
        
        <div class="section">
            <h2>📚 Resources</h2>
            <ul>
                <li><a href="https://github.com/patrickabedin/hellenic-google-ads-mcp">GitHub Repository</a></li>
                <li><a href="/health">Health Check</a></li>
            </ul>
        </div>
        
        <div class="section">
            <p><em>Powered by Hellenic Technologies • Built with MCP Protocol</em></p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.get("/health")
@app.head("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "hellenic-google-ads-mcp",
        "version": "1.0.0"
    }

@app.get("/.well-known/oauth-authorization-server")
@app.head("/.well-known/oauth-authorization-server")
async def oauth_discovery():
    """OAuth 2.0 Authorization Server Metadata for AI connector discovery (RFC 8414)."""
    return {
        "issuer": OAUTH_ISSUER,
        "authorization_endpoint": f"{BASE_URL}/oauth/authorize",
        "token_endpoint": f"{BASE_URL}/oauth/token",
        "registration_endpoint": f"{BASE_URL}/oauth/register",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "token_endpoint_auth_methods_supported": ["none"],
        "code_challenge_methods_supported": ["S256"],
        "scopes_supported": ["google_ads"],
    }


@app.post("/oauth/register")
async def oauth_register(request: Request):
    """Dynamic Client Registration (RFC 7591) — required by Claude connectors."""
    try:
        body = await request.json()
    except Exception:
        body = {}

    redirect_uris = body.get("redirect_uris") or []
    if not isinstance(redirect_uris, list) or not redirect_uris:
        return JSONResponse({"error": "invalid_redirect_uri"}, status_code=400)

    client = db.register_oauth_client(
        client_name=body.get("client_name"),
        redirect_uris=redirect_uris,
        grant_types=body.get("grant_types"),
        response_types=body.get("response_types"),
        token_endpoint_auth_method=body.get("token_endpoint_auth_method"),
        scope=body.get("scope"),
    )

    return JSONResponse(
        {
            "client_id": client["client_id"],
            "client_name": client["client_name"],
            "redirect_uris": client["redirect_uris"],
            "grant_types": client["grant_types"],
            "response_types": client["response_types"],
            "token_endpoint_auth_method": client["token_endpoint_auth_method"],
            "scope": client["scope"],
            "client_id_issued_at": int(datetime.utcnow().timestamp()),
        },
        status_code=201,
    )


@app.get("/.well-known/oauth-protected-resource")
@app.head("/.well-known/oauth-protected-resource")
async def oauth_protected_resource():
    """RFC 9728 resource metadata (origin-level)."""
    return {
        "resource": BASE_URL,
        "authorization_servers": [OAUTH_ISSUER],
        "bearer_methods_supported": ["header"],
        "scopes_supported": ["google_ads"],
    }


@app.get("/.well-known/oauth-protected-resource/mcp")
@app.head("/.well-known/oauth-protected-resource/mcp")
async def oauth_protected_resource_mcp():
    """RFC 9728 resource metadata (resource-specific path), used by some clients."""
    return {
        "resource": BASE_URL,
        "authorization_servers": [OAUTH_ISSUER],
        "bearer_methods_supported": ["header"],
        "scopes_supported": ["google_ads"],
    }


@app.get("/oauth/start")
async def oauth_start(session_id: Optional[str] = None):
    """Legacy start OAuth flow by explicit session_id."""
    if not session_id:
        session_id = secrets.token_urlsafe(32)

    auth_url = auth.get_auth_url(session_id)
    return RedirectResponse(url=auth_url)


@app.get("/oauth/authorize")
async def oauth_authorize(
    response_type: str,
    client_id: Optional[str] = None,
    redirect_uri: str = "",
    state: Optional[str] = None,
    code_challenge: str = "",
    code_challenge_method: str = "",
):
    """OAuth authorize endpoint for connector clients (Claude/ChatGPT/Gemini)."""
    if response_type != "code":
        raise HTTPException(status_code=400, detail="unsupported response_type")
    if not redirect_uri:
        raise HTTPException(status_code=400, detail="missing redirect_uri")
    if not code_challenge or code_challenge_method != "S256":
        raise HTTPException(status_code=400, detail="PKCE S256 is required")

    # Build signed state token containing all callback context
    # This makes the flow stateless and resilient to DB wipes
    session_id = secrets.token_urlsafe(24)
    code_verifier = secrets.token_urlsafe(64)
    state_payload = {
        "session_id": session_id,
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "state": state,
        "code_challenge": code_challenge,
        "code_verifier": code_verifier,
        "exp": int((datetime.utcnow() + timedelta(minutes=10)).timestamp()),
    }
    signed_state = auth._sign_state(state_payload)
    
    # Also store in DB for fallback (best effort)
    try:
        db.create_auth_request(
            client_id=client_id,
            redirect_uri=redirect_uri,
            state=state,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
        )
        db.store_google_pkce_state(session_id, code_verifier)
    except Exception:
        pass

    google_auth_url = auth.get_auth_url_for_connector(signed_state, code_verifier)
    return RedirectResponse(url=google_auth_url)

@app.get("/oauth/callback")
async def oauth_callback(code: str, state: str):
    """Google OAuth callback. Supports both legacy and brokered connector flow."""
    import logging
    logger = logging.getLogger(__name__)
    try:
        logger.info(f"OAuth callback received: state_len={len(state)}, code_len={len(code)}")
        
        # Try database lookup first
        auth_req = db.get_auth_request_by_google_state(state)
        logger.info(f"DB lookup result: {auth_req is not None}")

        # Legacy direct flow: state is session_id
        if not auth_req:
            # Try to decode signed state token (stateless fallback)
            state_payload = auth._verify_state(state)
            logger.info(f"Stateless verification result: {state_payload is not None}")
            
            if state_payload:
                # Stateless connector flow: decode state from token
                session_id = state_payload["session_id"]
                redirect_uri = state_payload["redirect_uri"]
                connector_state = state_payload.get("state")
                code_challenge = state_payload.get("code_challenge", "")
                
                # Extract code_verifier from stateless token for Google PKCE exchange
                code_verifier = state_payload.get("code_verifier")
                
                # Exchange Google code
                google_tokens = auth.exchange_code(code, session_id, code_verifier)
                
                # Issue signed auth code with embedded Google tokens (stateless — survives DB wipes)
                code_payload = {
                    "session_id": session_id,
                    "client_id": state_payload.get("client_id"),
                    "redirect_uri": redirect_uri,
                    "code_challenge": code_challenge,
                    "google_access_token": google_tokens["access_token"],
                    "google_refresh_token": google_tokens["refresh_token"],
                    "google_expiry": google_tokens["expiry"],
                    "exp": int((datetime.utcnow() + timedelta(minutes=10)).timestamp()),
                }
                local_code = auth.sign_auth_code(code_payload)
                
                # Redirect back to connector
                params = {"code": local_code}
                if connector_state:
                    params["state"] = connector_state
                redirect_target = f"{redirect_uri}?{urlencode(params)}"
                return RedirectResponse(url=redirect_target)
            
            # Pure legacy flow: state is just session_id
            result = auth.exchange_code(code, state)
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Authorization Complete</title>
                <style>
                    body {{
                        font-family: system-ui, -apple-system, sans-serif;
                        max-width: 600px;
                        margin: 100px auto;
                        padding: 40px;
                        text-align: center;
                        background: #f8f9fa;
                    }}
                    .success {{
                        background: #d4edda;
                        color: #155724;
                        padding: 20px;
                        border-radius: 8px;
                        margin: 20px 0;
                    }}
                    code {{
                        background: #fff;
                        padding: 5px 10px;
                        border-radius: 3px;
                        font-size: 0.9em;
                        display: inline-block;
                        margin: 10px 0;
                    }}
                </style>
            </head>
            <body>
                <h1>✅ Authorization Complete!</h1>
                <div class="success">
                    <p>Your Google Ads account has been successfully connected.</p>
                    <p>Your session ID: <code>{state}</code></p>
                </div>
                <p>You can now close this window and return to your MCP client.</p>
                <p>Use your session ID in all subsequent tool calls.</p>
            </body>
            </html>
            """
            return HTMLResponse(content=html)

        # Brokered connector flow (DB lookup succeeded)
        session_id = auth_req["session_id"]
        auth.exchange_code(code, session_id)
        db.mark_auth_request_completed(auth_req["request_id"])
        
        # Issue signed auth code (stateless — survives DB wipes)
        code_payload = {
            "session_id": session_id,
            "client_id": auth_req.get("client_id"),
            "redirect_uri": auth_req["redirect_uri"],
            "code_challenge": auth_req["code_challenge"],
            "exp": int((datetime.utcnow() + timedelta(minutes=10)).timestamp()),
        }
        local_code = auth.sign_auth_code(code_payload)

        params = {"code": local_code}
        if auth_req.get("state"):
            params["state"] = auth_req["state"]
        redirect_target = f"{auth_req['redirect_uri']}?{urlencode(params)}"
        return RedirectResponse(url=redirect_target)

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        msg = str(e)
        logger.error(f"OAuth callback error: {msg}")
        # Self-heal stale sessions
        if "Missing code verifier" in msg or "invalid_grant" in msg.lower():
            return RedirectResponse(url=f"{BASE_URL}/oauth/start")
        raise HTTPException(status_code=400, detail=msg)


@app.post("/oauth/token")
async def oauth_token(request: Request):
    """OAuth token exchange endpoint for connector clients."""
    content_type = request.headers.get("content-type", "")
    if "application/x-www-form-urlencoded" in content_type:
        form = await request.form()
        payload = dict(form)
    else:
        payload = await request.json()

    grant_type = payload.get("grant_type")
    code = payload.get("code")
    redirect_uri = payload.get("redirect_uri")
    client_id = payload.get("client_id")
    code_verifier = payload.get("code_verifier")

    if grant_type != "authorization_code":
        return JSONResponse({"error": "unsupported_grant_type"}, status_code=400)
    if not code or not code_verifier or not redirect_uri:
        return JSONResponse({"error": "invalid_request"}, status_code=400)

    # Try stateless signed code first (survives DB wipes)
    code_payload = auth.verify_auth_code(code)
    
    if code_payload:
        # Stateless verification
        if code_payload.get("exp") and code_payload["exp"] < datetime.utcnow().timestamp():
            return JSONResponse({"error": "invalid_grant"}, status_code=400)
        if redirect_uri != code_payload.get("redirect_uri"):
            return JSONResponse({"error": "invalid_grant"}, status_code=400)
        if not auth.verify_pkce(
            code_verifier=code_verifier,
            code_challenge=code_payload.get("code_challenge", ""),
            method="S256",
        ):
            return JSONResponse({"error": "invalid_grant"}, status_code=400)
        
        session_id = code_payload["session_id"]
        token_payload = {
            "session_id": session_id,
            "client_id": code_payload.get("client_id"),
            "exp": int((datetime.utcnow() + timedelta(days=30)).timestamp()),
        }
        
        # Embed Google tokens in bearer token for fully stateless operation
        if code_payload.get("google_access_token"):
            token_payload["google_access_token"] = code_payload["google_access_token"]
            token_payload["google_refresh_token"] = code_payload["google_refresh_token"]
            token_payload["google_expiry"] = code_payload["google_expiry"]
        
        access_token = auth.sign_auth_code(token_payload)
        
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 2592000,
            "scope": "google_ads",
        }

    # Fallback: DB lookup for legacy codes
    code_row = db.get_oauth_code(code)
    if not code_row:
        return JSONResponse({"error": "invalid_grant"}, status_code=400)
    if int(code_row.get("used", 0)) == 1:
        return JSONResponse({"error": "invalid_grant"}, status_code=400)
    if datetime.fromisoformat(code_row["expires_at"]) < datetime.utcnow():
        return JSONResponse({"error": "invalid_grant"}, status_code=400)
    if redirect_uri != code_row["redirect_uri"]:
        return JSONResponse({"error": "invalid_grant"}, status_code=400)

    auth_req = db.get_auth_request_by_id(code_row["request_id"])
    if not auth_req:
        return JSONResponse({"error": "invalid_grant"}, status_code=400)

    if auth_req.get("client_id") and client_id and auth_req["client_id"] != client_id:
        return JSONResponse({"error": "invalid_grant"}, status_code=400)

    if not auth.verify_pkce(
        code_verifier=code_verifier,
        code_challenge=auth_req["code_challenge"],
        method=auth_req["code_challenge_method"],
    ):
        return JSONResponse({"error": "invalid_grant"}, status_code=400)

    db.mark_oauth_code_used(code)
    
    # Issue signed token (stateless)
    token_payload = {
        "session_id": code_row["session_id"],
        "client_id": auth_req.get("client_id"),
        "exp": int((datetime.utcnow() + timedelta(days=30)).timestamp()),
    }
    access_token = auth.sign_auth_code(token_payload)

    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": 2592000,
        "scope": "google_ads",
    }

# Initialize SSE transport at module level
sse_transport = SseServerTransport("/messages")

def _oauth_www_authenticate_header() -> Dict[str, str]:
    # Per RFC 9728, keep WWW-Authenticate minimal. Clients discover endpoints via
    # /.well-known/oauth-protected-resource, not by parsing this header.
    return {"WWW-Authenticate": 'Bearer error="invalid_token"'}


def _validate_bearer(request: Request) -> Optional[str]:
    auth_header = request.headers.get("authorization", "")
    if not auth_header.lower().startswith("bearer "):
        return None
    token = auth_header.split(" ", 1)[1].strip()
    
    # Try stateless signed token first (survives DB wipes)
    token_payload = auth.verify_auth_code(token)
    if token_payload:
        if token_payload.get("exp") and token_payload["exp"] < datetime.utcnow().timestamp():
            return None
        # Store payload in thread-local for tools to access Google tokens without DB
        auth.set_token_context(token_payload)
        return token_payload.get("session_id")
    
    # Fallback: DB lookup for legacy tokens
    row = db.get_connector_token(token)
    if not row:
        return None
    if datetime.fromisoformat(row["expires_at"]) < datetime.utcnow():
        return None
    return row["session_id"]


@app.get("/mcp")
@app.head("/mcp")
async def mcp_sse(request: Request):
    """Primary MCP endpoint (Claude-focused behavior).

    - HTML browsers: redirect to OAuth start
    - Any unauthenticated probe: 401 + WWW-Authenticate (strict challenge)
    - Authenticated non-SSE probe: 200 status JSON
    - Authenticated SSE accept: opens stream
    """
    accept = (request.headers.get("accept") or "").lower()

    if "text/html" in accept and request.method != "HEAD":
        return RedirectResponse(url=f"{BASE_URL}/oauth/start")

    session_id = _validate_bearer(request)
    if not session_id:
        return JSONResponse(
            {"error": "invalid_token", "error_description": "Authentication required"},
            status_code=401,
            headers=_oauth_www_authenticate_header(),
        )

    if "text/event-stream" not in accept:
        return JSONResponse({"ok": True, "authenticated": True, "transport": "sse"}, status_code=200)

    async with sse_transport.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await mcp_server.run(
            streams[0],
            streams[1],
            mcp_server.create_initialization_options()
        )

@app.post("/messages")
async def mcp_messages(request: Request):
    """Handle MCP client messages posted back."""
    await sse_transport.handle_post_message(
        request.scope, request.receive, request._send
    )

def _rpc_ok(result: Any, req_id: Any) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _rpc_err(code: int, message: str, req_id: Any = None) -> Dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {
            "code": code,
            "message": message
        }
    }


@app.options("/mcp")
async def mcp_http_options():
    """CORS/preflight support for streamable HTTP clients."""
    return Response(status_code=204)


# Legacy SSE aliases used by some MCP clients
@app.get("/sse")
@app.head("/sse")
async def sse_alias(request: Request):
    """Compatibility alias for UIs with brittle connection tests.

    Returns probe-friendly 200 metadata when unauthenticated (with OAuth hint),
    but still delegates authenticated/SSE flows to /mcp logic.
    """
    accept = (request.headers.get("accept") or "").lower()
    session_id = _validate_bearer(request)

    if not session_id:
        if "text/event-stream" in accept:
            # SSE request without auth — still need to challenge
            return JSONResponse(
                {"error": "invalid_token", "error_description": "Authentication required"},
                status_code=401,
                headers=_oauth_www_authenticate_header(),
            )
        # Probe-friendly JSON response for non-SSE requests
        return JSONResponse(
            {
                "ok": True,
                "transport": "sse",
                "authenticated": False,
                "note": "Use OAuth 2.1 flow to authenticate"
            },
            status_code=200,
            headers=_oauth_www_authenticate_header(),
        )

    return await mcp_sse(request)


@app.options("/sse")
async def sse_options():
    return Response(status_code=204)


@app.post("/mcp")
async def mcp_http(request: Request):
    """MCP endpoint via Streamable HTTP (JSON-RPC) with mandatory bearer auth."""
    auth_header = request.headers.get("authorization", "")
    bearer_token = None
    if auth_header.lower().startswith("bearer "):
        bearer_token = auth_header.split(" ", 1)[1].strip()

    def _unauthorized(msg: str):
        return JSONResponse(_rpc_err(-32001, msg), status_code=401, headers=_oauth_www_authenticate_header())

    if not bearer_token:
        return _unauthorized("Missing bearer token")

    session_from_bearer = None
    
    # Try stateless signed token first (survives DB wipes)
    token_payload = auth.verify_auth_code(bearer_token)
    if token_payload:
        if token_payload.get("exp") and token_payload["exp"] < datetime.utcnow().timestamp():
            return _unauthorized("Expired bearer token")
        auth.set_token_context(token_payload)
        session_from_bearer = token_payload.get("session_id")
    else:
        # Fallback: DB lookup for legacy tokens
        token_row = db.get_connector_token(bearer_token)
        if not token_row:
            return _unauthorized("Invalid bearer token")
        if datetime.fromisoformat(token_row["expires_at"]) < datetime.utcnow():
            return _unauthorized("Expired bearer token")
        session_from_bearer = token_row["session_id"]

    try:
        body = await request.json()
    except Exception:
        return JSONResponse(_rpc_err(-32700, "Parse error"), status_code=400)

    # Support both single and batch JSON-RPC payloads
    is_batch = isinstance(body, list)
    calls = body if is_batch else [body]
    responses: list[Dict[str, Any]] = []

    for call in calls:
        if not isinstance(call, dict):
            responses.append(_rpc_err(-32600, "Invalid Request"))
            continue

        method = call.get("method")
        req_id = call.get("id")
        params = call.get("params") or {}

        # Notifications do not require responses
        is_notification = req_id is None

        try:
            if method == "initialize":
                result = {
                    "protocolVersion": params.get("protocolVersion", "2024-11-05"),
                    "capabilities": {
                        "tools": {
                            "listChanged": False
                        }
                    },
                    "serverInfo": {
                        "name": "hellenic-google-ads-mcp",
                        "version": "1.0.0"
                    }
                }
                if not is_notification:
                    responses.append(_rpc_ok(result, req_id))

            elif method in ("notifications/initialized", "initialized"):
                # Client lifecycle notification
                if not is_notification:
                    responses.append(_rpc_ok({}, req_id))

            elif method == "tools/list":
                tools = []
                for t in TOOLS:
                    tools.append({
                        "name": t.name,
                        "description": t.description,
                        "inputSchema": t.inputSchema,
                    })
                if not is_notification:
                    responses.append(_rpc_ok({"tools": tools}, req_id))

            elif method == "tools/call":
                name = params.get("name")
                arguments = params.get("arguments") or {}
                if not name:
                    if not is_notification:
                        responses.append(_rpc_err(-32602, "Missing tool name", req_id))
                    continue

                # If bearer token auth exists, inject session_id so tools can run
                if session_from_bearer:
                    arguments.setdefault("session_id", session_from_bearer)

                result_content = await mcp_call_tool(name, arguments)
                content = []
                for item in result_content:
                    content.append({
                        "type": getattr(item, "type", "text"),
                        "text": getattr(item, "text", str(item))
                    })
                if not is_notification:
                    responses.append(_rpc_ok({"content": content, "isError": False}, req_id))

            else:
                if not is_notification:
                    responses.append(_rpc_err(-32601, f"Method not found: {method}", req_id))

        except Exception as e:
            if not is_notification:
                responses.append(_rpc_err(-32603, str(e), req_id))

    if not responses:
        return Response(status_code=204)

    if is_batch:
        return JSONResponse(responses)
    return JSONResponse(responses[0])

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8090))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
