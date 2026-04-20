"""Main FastAPI application for Hellenic Google Ads MCP Server."""
import os
import secrets
from typing import Optional, Any, Dict
from urllib.parse import urlencode
from datetime import datetime
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
    version="1.0.0"
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
    """OAuth 2.0 Authorization Server Metadata for AI connector discovery."""
    return {
        "issuer": OAUTH_ISSUER,
        "authorization_endpoint": f"{BASE_URL}/oauth/authorize",
        "token_endpoint": f"{BASE_URL}/oauth/token",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "token_endpoint_auth_methods_supported": ["none"],
        "code_challenge_methods_supported": ["S256"],
        "scopes_supported": ["google_ads"],
    }


@app.get("/.well-known/oauth-protected-resource")
@app.head("/.well-known/oauth-protected-resource")
async def oauth_protected_resource():
    """Resource metadata so clients can discover auth requirements for /mcp."""
    return {
        "resource": f"{BASE_URL}/mcp",
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

    auth_req = db.create_auth_request(
        client_id=client_id,
        redirect_uri=redirect_uri,
        state=state,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
    )

    google_auth_url = auth.get_auth_url(auth_req["google_state"])
    return RedirectResponse(url=google_auth_url)

@app.get("/oauth/callback")
async def oauth_callback(code: str, state: str):
    """Google OAuth callback. Supports both legacy and brokered connector flow."""
    try:
        auth_req = db.get_auth_request_by_google_state(state)

        # Legacy direct flow: state is session_id
        if not auth_req:
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

        # Brokered connector flow
        session_id = auth_req["session_id"]
        auth.exchange_code(code, session_id)
        db.mark_auth_request_completed(auth_req["request_id"])
        local_code = db.issue_oauth_code(
            request_id=auth_req["request_id"],
            session_id=session_id,
            client_id=auth_req.get("client_id"),
            redirect_uri=auth_req["redirect_uri"],
        )

        params = {"code": local_code}
        if auth_req.get("state"):
            params["state"] = auth_req["state"]
        redirect_target = f"{auth_req['redirect_uri']}?{urlencode(params)}"
        return RedirectResponse(url=redirect_target)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


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

    # Optional client_id match if one exists in stored auth request
    if auth_req.get("client_id") and client_id and auth_req["client_id"] != client_id:
        return JSONResponse({"error": "invalid_grant"}, status_code=400)

    if not auth.verify_pkce(
        code_verifier=code_verifier,
        code_challenge=auth_req["code_challenge"],
        method=auth_req["code_challenge_method"],
    ):
        return JSONResponse({"error": "invalid_grant"}, status_code=400)

    db.mark_oauth_code_used(code)
    token = db.issue_connector_token(
        session_id=code_row["session_id"],
        client_id=auth_req.get("client_id"),
    )

    return {
        "access_token": token["access_token"],
        "token_type": token["token_type"],
        "expires_in": token["expires_in"],
        "scope": "google_ads",
    }

# Initialize SSE transport at module level
sse_transport = SseServerTransport("/messages")

@app.get("/mcp")
@app.head("/mcp")
async def mcp_sse(request: Request):
    """MCP endpoint via Server-Sent Events (SSE).

    Behavior by Accept header:
    - text/event-stream => open SSE stream
    - text/html         => convenience redirect to OAuth start (browser UX)
    - otherwise         => probe-friendly JSON metadata (HTTP 200) + auth hint
    """
    accept = (request.headers.get("accept") or "").lower()

    if "text/event-stream" not in accept:
        if "text/html" in accept and request.method != "HEAD":
            # Browser-friendly behavior that matches historical UX.
            return RedirectResponse(url=f"{BASE_URL}/oauth/start")

        headers = {
            "WWW-Authenticate": (
                f'Bearer realm="{BASE_URL}/mcp", '
                f'authorization_uri="{BASE_URL}/oauth/authorize", '
                f'token_uri="{BASE_URL}/oauth/token", '
                f'resource_metadata="{BASE_URL}/.well-known/oauth-protected-resource"'
            )
        }
        return JSONResponse(
            {
                "name": "hellenic-google-ads-mcp",
                "mcp": f"{BASE_URL}/mcp",
                "authentication": "required",
                "oauth_authorization_server": f"{BASE_URL}/.well-known/oauth-authorization-server",
                "oauth_protected_resource": f"{BASE_URL}/.well-known/oauth-protected-resource",
                "hint": "Use OAuth discovery/authorize flow, then POST /mcp with Authorization: Bearer <token>.",
            },
            status_code=200,
            headers=headers,
        )

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


@app.post("/mcp")
async def mcp_http(request: Request):
    """MCP endpoint via Streamable HTTP (JSON-RPC) with mandatory bearer auth."""
    auth_header = request.headers.get("authorization", "")
    bearer_token = None
    if auth_header.lower().startswith("bearer "):
        bearer_token = auth_header.split(" ", 1)[1].strip()

    def _unauthorized(msg: str):
        headers = {
            "WWW-Authenticate": (
                f'Bearer realm="{BASE_URL}/mcp", '
                f'authorization_uri="{BASE_URL}/oauth/authorize", '
                f'token_uri="{BASE_URL}/oauth/token", '
                f'resource_metadata="{BASE_URL}/.well-known/oauth-protected-resource"'
            )
        }
        return JSONResponse(_rpc_err(-32001, msg), status_code=401, headers=headers)

    if not bearer_token:
        return _unauthorized("Missing bearer token")

    session_from_bearer = None
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
