"""Main FastAPI application for Hellenic Google Ads MCP Server."""
import os
import secrets
from typing import Optional
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from mcp.server.sse import SseServerTransport
from mcp.server.stdio import stdio_server
import uvicorn

import db
import auth
from mcp_server import mcp_server

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
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "hellenic-google-ads-mcp",
        "version": "1.0.0"
    }

@app.get("/oauth/start")
async def oauth_start(session_id: Optional[str] = None):
    """Start OAuth flow - redirect to Google authorization."""
    if not session_id:
        session_id = secrets.token_urlsafe(32)
    
    auth_url = auth.get_auth_url(session_id)
    return RedirectResponse(url=auth_url)

@app.get("/oauth/callback")
async def oauth_callback(code: str, state: str):
    """OAuth callback - exchange code for tokens."""
    try:
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
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/mcp")
async def mcp_sse(request: Request):
    """MCP endpoint via Server-Sent Events (SSE)."""
    session_id = request.query_params.get("session_id")
    
    async with SseServerTransport("/messages") as transport:
        # Store session_id in context if provided
        if session_id:
            transport.session_id = session_id
        
        await mcp_server.run(
            transport.read_stream,
            transport.write_stream,
            mcp_server.create_initialization_options()
        )

@app.post("/mcp")
async def mcp_http(request: Request):
    """MCP endpoint via HTTP POST."""
    try:
        # Get session ID from header or body
        session_id = request.headers.get("X-Session-ID")
        
        body = await request.json()
        if not session_id and "session_id" in body:
            session_id = body["session_id"]
        
        # Process MCP request
        # This would need full HTTP transport implementation
        # For now, return basic response directing to SSE
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": body.get("id"),
            "result": {
                "message": "Please use SSE transport at GET /mcp"
            }
        })
    
    except Exception as e:
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": str(e)
            }
        }, status_code=500)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8090))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
