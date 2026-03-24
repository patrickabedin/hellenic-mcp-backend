"""MCP Server implementation for Google Ads."""
import json
from typing import Any, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent
import tools

# Create MCP server instance
mcp_server = Server("hellenic-google-ads-mcp")

# Define all MCP tools
TOOLS = [
    Tool(
        name="connect_google_ads",
        description="Generate OAuth URL to connect a Google Ads account. Returns an authorization URL for the user to visit.",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "Unique session identifier for this user"
                }
            },
            "required": ["session_id"]
        }
    ),
    Tool(
        name="list_accounts",
        description="List all Google Ads accounts accessible to the authenticated user.",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "Session ID from OAuth flow"
                }
            },
            "required": ["session_id"]
        }
    ),
    Tool(
        name="get_account_summary",
        description="Get summary metrics (spend, impressions, clicks, conversions) for an account over a date range.",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "customer_id": {"type": "string", "description": "Google Ads customer ID"},
                "date_from": {"type": "string", "description": "Start date (YYYY-MM-DD)", "default": "2024-01-01"},
                "date_to": {"type": "string", "description": "End date (YYYY-MM-DD)", "default": "2024-12-31"}
            },
            "required": ["session_id", "customer_id"]
        }
    ),
    Tool(
        name="list_campaigns",
        description="List all campaigns for an account with status, budget, and basic metrics.",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "customer_id": {"type": "string", "description": "Google Ads customer ID"}
            },
            "required": ["session_id", "customer_id"]
        }
    ),
    Tool(
        name="get_campaign_performance",
        description="Get detailed performance metrics for a specific campaign over a date range.",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "customer_id": {"type": "string"},
                "campaign_id": {"type": "string", "description": "Campaign ID"},
                "date_from": {"type": "string", "default": "2024-01-01"},
                "date_to": {"type": "string", "default": "2024-12-31"}
            },
            "required": ["session_id", "customer_id", "campaign_id"]
        }
    ),
    Tool(
        name="list_ad_groups",
        description="List all ad groups for a campaign with bids and performance.",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "customer_id": {"type": "string"},
                "campaign_id": {"type": "string", "description": "Campaign ID"}
            },
            "required": ["session_id", "customer_id", "campaign_id"]
        }
    ),
    Tool(
        name="get_keywords",
        description="Get keyword performance and quality scores for an ad group.",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "customer_id": {"type": "string"},
                "ad_group_id": {"type": "string", "description": "Ad group ID"}
            },
            "required": ["session_id", "customer_id", "ad_group_id"]
        }
    ),
    Tool(
        name="get_search_terms_report",
        description="Get search terms that triggered ads, with performance data.",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "customer_id": {"type": "string"},
                "campaign_id": {"type": "string", "description": "Optional campaign ID filter"},
                "date_from": {"type": "string", "default": "2024-01-01"},
                "date_to": {"type": "string", "default": "2024-12-31"}
            },
            "required": ["session_id", "customer_id"]
        }
    ),
    Tool(
        name="pause_campaign",
        description="Pause a campaign to stop serving ads.",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "customer_id": {"type": "string"},
                "campaign_id": {"type": "string", "description": "Campaign ID to pause"}
            },
            "required": ["session_id", "customer_id", "campaign_id"]
        }
    ),
    Tool(
        name="enable_campaign",
        description="Enable a paused campaign to resume serving ads.",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "customer_id": {"type": "string"},
                "campaign_id": {"type": "string", "description": "Campaign ID to enable"}
            },
            "required": ["session_id", "customer_id", "campaign_id"]
        }
    ),
    Tool(
        name="update_campaign_budget",
        description="Update the daily budget for a campaign.",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "customer_id": {"type": "string"},
                "campaign_id": {"type": "string", "description": "Campaign ID"},
                "budget_amount": {"type": "number", "description": "New daily budget amount in account currency"}
            },
            "required": ["session_id", "customer_id", "campaign_id", "budget_amount"]
        }
    )
]

@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return TOOLS

@mcp_server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute an MCP tool."""
    try:
        # Route to appropriate tool function
        tool_map = {
            "connect_google_ads": tools.connect_google_ads,
            "list_accounts": tools.list_accounts,
            "get_account_summary": tools.get_account_summary,
            "list_campaigns": tools.list_campaigns,
            "get_campaign_performance": tools.get_campaign_performance,
            "list_ad_groups": tools.list_ad_groups,
            "get_keywords": tools.get_keywords,
            "get_search_terms_report": tools.get_search_terms_report,
            "pause_campaign": tools.pause_campaign,
            "enable_campaign": tools.enable_campaign,
            "update_campaign_budget": tools.update_campaign_budget
        }
        
        if name not in tool_map:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Unknown tool: {name}"})
            )]
        
        # Execute tool
        result = await tool_map[name](**arguments)
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)})
        )]

# Export server instance
__all__ = ["mcp_server"]
