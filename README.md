# 🚀 Hellenic Google Ads MCP Server

Production-ready remote MCP (Model Context Protocol) server providing secure multi-tenant access to the Google Ads API.

**Built by Hellenic Technologies**

## ✨ Features

- **🔐 Multi-tenant OAuth2** - Each user connects their own Google Ads account
- **🌐 Remote Access** - Use from Claude Desktop, ChatGPT, Gemini, or any MCP client
- **🔒 Secure** - All API calls route through Hellenic Technologies' Developer Token
- **⚡ Fast** - SSE-based streaming for real-time responses
- **📊 Comprehensive** - 25 tools covering campaigns, keywords, budgets, billing, recommendations, and reporting

## 🔑 Quick Start

### Connect from Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "google-ads": {
      "url": "https://google-ads-mcp.hellenicai.com/mcp",
      "transport": "sse"
    }
  }
}
```

Restart Claude Desktop, then:

1. Ask Claude: "Connect to my Google Ads account"
2. Claude will call `connect_google_ads` and give you an OAuth URL
3. Open the URL, authorize access to your Google Ads account
4. You're ready! Claude can now access your campaigns, keywords, and performance data

### Connect from Other MCP Clients

**MCP Endpoint:** `https://google-ads-mcp.hellenicai.com/mcp`

Use this URL in any MCP-compatible client (ChatGPT, Gemini, etc.)

## 🛠️ Available Tools (25)

### 🔐 Authentication (1)

| Tool | Description |
|------|-------------|
| `connect_google_ads` | Authenticate with Google Ads via OAuth. Returns a link to click in chat. |

### 📋 Account Management (3)

| Tool | Description |
|------|-------------|
| `list_accounts` | List all client accounts under the Hellenic Technologies MCC (356-856-4840) |
| `get_account_summary` | Get spend, clicks, impressions, conversions for a date range |
| `get_conversion_tracking` | View conversion actions and tracking status |

### 📣 Campaign Management (6)

| Tool | Description |
|------|-------------|
| `list_campaigns` | List all campaigns with status and budget |
| `get_campaign_performance` | Performance metrics for a campaign (impressions, clicks, cost, conversions) |
| `create_campaign` | Create a new campaign (starts PAUSED for safety) |
| `delete_campaign` | Delete a campaign permanently |
| `pause_campaign` | Pause a running campaign |
| `enable_campaign` | Re-enable a paused campaign |

### 💰 Budget & Bidding (3)

| Tool | Description |
|------|-------------|
| `update_campaign_budget` | Change a campaign's daily budget |
| `update_bidding_strategy` | Switch bidding strategy (TARGET_CPA, TARGET_ROAS, MAXIMIZE_CONVERSIONS, etc.) |
| `budget_forecast` | 30-day spend/clicks/conversions forecast based on recent performance |

### 🎯 Ad Groups & Keywords (3)

| Tool | Description |
|------|-------------|
| `list_ad_groups` | List ad groups within a campaign |
| `create_ad_group` | Create a new ad group |
| `get_keywords` | List keywords with match type, bids, and status |

### 🔍 Search Intelligence (3)

| Tool | Description |
|------|-------------|
| `get_search_terms_report` | See actual search queries that triggered ads |
| `get_quality_score` | Quality scores and component breakdown per keyword |
| `get_auction_insights` | Competitive auction data — impression share vs competitors |

### 💡 Recommendations & Extensions (3)

| Tool | Description |
|------|-------------|
| `list_recommendations` | Google's optimization suggestions for the account |
| `apply_recommendation` | Apply a recommendation automatically |
| `list_ad_extensions` | View sitelinks, callouts, structured snippets |

### 📊 Reach & Planning (1)

| Tool | Description |
|------|-------------|
| `get_reach_estimate` | Estimate reach for keyword/audience targeting combinations |

### 💳 Billing & Health Monitoring (2)

| Tool | Description |
|------|-------------|
| `get_billing_status` | Check payment method health, account status, spend gaps for one account |
| `check_all_accounts_billing` | Scan ALL MCC accounts for billing issues — returns CRITICAL/WARNING/healthy summary |

## 💬 Example Questions You Can Ask

**Daily monitoring:**
- "Check billing health across all my accounts"
- "Are any of my client accounts suspended or having payment issues?"
- "Show me yesterday's performance for [client name]"

**Campaign management:**
- "Pause all campaigns for [client] — they're on holiday"
- "What's the budget utilization for [campaign]?"
- "Create a new Search campaign for [client] with €50/day budget"

**Optimization:**
- "What recommendations does Google have for [account]?"
- "Show me the search terms report for [campaign] — I want to find negative keywords"
- "What's the quality score breakdown for [campaign]'s keywords?"

**Competitive intelligence:**
- "Who am I competing against in auctions for [campaign]?"
- "What's my impression share vs competitors?"

**Billing & alerts:**
- "Check if 1926 Collection's ads are running and billing is healthy"
- "Scan all accounts for payment failures"
- "Which accounts have had zero spend in the last 2 days?"

## 🔐 Authentication Flow

1. **Generate Session** - Client generates a unique `session_id` (UUID)
2. **Start OAuth** - Call `connect_google_ads` with your session_id
3. **Authorize** - Open the returned URL and grant access to your Google Ads account
4. **Use Tools** - All subsequent tool calls include your session_id to access your data

Your tokens are stored securely and automatically refreshed. Each user's data is completely isolated.

## 📊 Example Usage

```python
# In Claude or ChatGPT:
"Show me my Google Ads campaigns for customer ID 1234567890"
"What are my top performing keywords this month?"
"Pause campaign ID 9876543210"
"Update campaign 9876543210 budget to $50 per day"
"Create a new Search campaign with $100/day budget"
"Show me Google's recommendations for my account"
"What's my quality score for 'running shoes' keyword?"
```

## 🏗️ Architecture

- **FastAPI** - Modern async web framework
- **MCP Protocol** - Server-Sent Events (SSE) for streaming
- **Google Ads API** - Official Python client library
- **SQLite** - Local token storage (per-session isolation)
- **OAuth2** - Secure user authentication via Google

## 🚀 Deployment

Deployed on AWS Ireland (eu-west-1) with:
- **Process Manager:** PM2 (auto-restart on crash)
- **Web Server:** OpenLiteSpeed (reverse proxy)
- **SSL:** Let's Encrypt (auto-renewal)

**Health Check:** https://google-ads-mcp.hellenicai.com/health

## 📁 Project Structure

```
hellenic-google-ads-mcp/
├── main.py           # FastAPI application
├── mcp_server.py     # MCP server setup
├── tools.py          # All 25 Google Ads tools
├── auth.py           # OAuth2 flow
├── db.py             # SQLite token storage
├── .env              # Environment variables
└── README.md         # This file
```

## 🔧 Development

### Local Setup

```bash
# Clone repository
git clone https://github.com/patrickabedin/hellenic-google-ads-mcp.git
cd hellenic-google-ads-mcp

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn mcp google-ads google-auth-oauthlib python-dotenv aiofiles

# Set environment variables
cp .env.example .env
# Edit .env with your credentials

# Run server
uvicorn main:app --host 0.0.0.0 --port 8090 --reload
```

### Environment Variables

```bash
GOOGLE_ADS_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_ADS_CLIENT_SECRET=your-client-secret
GOOGLE_ADS_DEVELOPER_TOKEN=your-developer-token
GOOGLE_ADS_REDIRECT_URI=https://your-domain.com/oauth/callback
MCP_SECRET_KEY=random-32-byte-hex
PORT=8090
```

## 📤 Submit to Directories

### Smithery

```bash
# Create smithery.json
{
  "name": "hellenic-google-ads-mcp",
  "description": "Multi-tenant MCP server for Google Ads API access",
  "url": "https://google-ads-mcp.hellenicai.com/mcp",
  "transport": "sse"
}
```

Submit at: https://smithery.ai/submit

### Glama

Submit at: https://glama.ai/mcp/submit

## 📝 License

Apache License 2.0

## 🏢 About Hellenic Technologies

Professional software development and AI solutions.

**Website:** https://hellenicai.com  
**GitHub:** https://github.com/patrickabedin

## 🤝 Support

For issues or questions:
- Open an issue on [GitHub](https://github.com/patrickabedin/hellenic-google-ads-mcp/issues)
- Contact: support@hellenicai.com

## 🔒 Privacy & Security

- Your Google Ads credentials are stored securely and never shared
- Each user's data is completely isolated
- All API calls route through Hellenic Technologies' Developer Token
- OAuth tokens are automatically refreshed
- HTTPS only (TLS 1.3)

---

**Made with ❤️ by Hellenic Technologies**
