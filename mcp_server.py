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
        name="list_accessible_customers",
        description="List all accessible Google Ads customer accounts including MCC children. Returns customer IDs only — use list_accounts for full details.",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string", "description": "Session ID from OAuth flow"}
            },
            "required": ["session_id"]
        }
    ),
    Tool(
        name="list_accounts",
        description="List all Google Ads accounts accessible to the authenticated user with full details (name, currency, timezone, status).",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string", "description": "Session ID from OAuth flow"}
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
        name="get_account_budget",
        description="View account-level budget allocation and spend pacing.",
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
        name="get_billing_summary",
        description="Get billing summary: payment method health, account status, and spend summary.",
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
        name="create_campaign",
        description="Create new campaigns with budget, channel type, and bidding strategy.",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "customer_id": {"type": "string", "description": "Google Ads customer ID"},
                "name": {"type": "string", "description": "Campaign name"},
                "budget_amount": {"type": "number", "description": "Daily budget in account currency"},
                "advertising_channel_type": {"type": "string", "description": "SEARCH, DISPLAY, VIDEO, etc.", "default": "SEARCH"}
            },
            "required": ["session_id", "customer_id", "name", "budget_amount"]
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
        name="update_campaign",
        description="Modify campaign settings, budgets, and targeting parameters.",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "customer_id": {"type": "string"},
                "campaign_id": {"type": "string", "description": "Campaign ID"},
                "name": {"type": "string", "description": "New campaign name (optional)"},
                "status": {"type": "string", "description": "ENABLED, PAUSED (optional)"},
                "budget_amount": {"type": "number", "description": "New daily budget (optional)"}
            },
            "required": ["session_id", "customer_id", "campaign_id"]
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
        name="get_ad_group_performance",
        description="Get ad group-level metrics for granular performance analysis.",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "customer_id": {"type": "string"},
                "ad_group_id": {"type": "string", "description": "Ad group ID"},
                "date_from": {"type": "string", "default": "2024-01-01"},
                "date_to": {"type": "string", "default": "2024-12-31"}
            },
            "required": ["session_id", "customer_id", "ad_group_id"]
        }
    ),
    Tool(
        name="create_ad_group",
        description="Create ad groups within campaigns with custom bids and targeting.",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "customer_id": {"type": "string"},
                "campaign_id": {"type": "string", "description": "Campaign ID"},
                "name": {"type": "string", "description": "Ad group name"},
                "cpc_bid": {"type": "number", "description": "Max CPC bid (optional)", "default": None}
            },
            "required": ["session_id", "customer_id", "campaign_id", "name"]
        }
    ),
    Tool(
        name="update_ad_group",
        description="Modify ad group settings, bids, and status.",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "customer_id": {"type": "string"},
                "ad_group_id": {"type": "string", "description": "Ad group ID"},
                "name": {"type": "string", "description": "New name (optional)"},
                "status": {"type": "string", "description": "ENABLED, PAUSED (optional)"},
                "cpc_bid": {"type": "number", "description": "New max CPC bid (optional)"}
            },
            "required": ["session_id", "customer_id", "ad_group_id"]
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
        name="get_keyword_performance",
        description="Get keyword performance with quality scores — optimize what works.",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "customer_id": {"type": "string"},
                "criterion_id": {"type": "string", "description": "Keyword criterion ID"},
                "date_from": {"type": "string", "default": "2024-01-01"},
                "date_to": {"type": "string", "default": "2024-12-31"}
            },
            "required": ["session_id", "customer_id", "criterion_id"]
        }
    ),
    Tool(
        name="add_keywords",
        description="Add new keywords to ad groups with match types and bids.",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "customer_id": {"type": "string"},
                "ad_group_id": {"type": "string", "description": "Ad group ID"},
                "keywords": {
                    "type": "array",
                    "description": "List of keywords with text, match_type (BROAD, PHRASE, EXACT), and optional cpc_bid",
                    "items": {"type": "object"}
                }
            },
            "required": ["session_id", "customer_id", "ad_group_id", "keywords"]
        }
    ),
    Tool(
        name="update_keyword_bid",
        description="Adjust keyword-level bids for optimal cost-per-click.",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "customer_id": {"type": "string"},
                "ad_group_id": {"type": "string", "description": "Ad group ID"},
                "criterion_id": {"type": "string", "description": "Keyword criterion ID"},
                "cpc_bid": {"type": "number", "description": "New max CPC bid"}
            },
            "required": ["session_id", "customer_id", "ad_group_id", "criterion_id", "cpc_bid"]
        }
    ),
    Tool(
        name="get_ad_performance",
        description="Get ad creative performance metrics and engagement data.",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "customer_id": {"type": "string"},
                "ad_group_id": {"type": "string", "description": "Ad group ID"},
                "date_from": {"type": "string", "default": "2024-01-01"},
                "date_to": {"type": "string", "default": "2024-12-31"}
            },
            "required": ["session_id", "customer_id", "ad_group_id"]
        }
    ),
    Tool(
        name="create_responsive_search_ad",
        description="Build responsive search ads with multiple headlines and descriptions.",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "customer_id": {"type": "string"},
                "ad_group_id": {"type": "string", "description": "Ad group ID"},
                "headlines": {"type": "array", "description": "List of headline texts (up to 15)", "items": {"type": "string"}},
                "descriptions": {"type": "array", "description": "List of description texts (up to 4)", "items": {"type": "string"}},
                "final_url": {"type": "string", "description": "Final URL for the ad"}
            },
            "required": ["session_id", "customer_id", "ad_group_id", "headlines", "descriptions", "final_url"]
        }
    ),
    Tool(
        name="update_ad",
        description="Modify existing ad copy, headlines, and descriptions.",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "customer_id": {"type": "string"},
                "ad_group_id": {"type": "string", "description": "Ad group ID"},
                "ad_id": {"type": "string", "description": "Ad ID"},
                "status": {"type": "string", "description": "ENABLED, PAUSED (optional)"}
            },
            "required": ["session_id", "customer_id", "ad_group_id", "ad_id"]
        }
    ),
    Tool(
        name="get_conversion_actions",
        description="View all conversion actions and tracking configuration.",
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
        name="create_conversion_action",
        description="Set up new conversion tracking for key business events.",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "customer_id": {"type": "string"},
                "name": {"type": "string", "description": "Conversion action name"},
                "category": {"type": "string", "description": "DEFAULT, PURCHASE, SIGNUP, etc.", "default": "DEFAULT"},
                "value": {"type": "number", "description": "Default conversion value (optional)"}
            },
            "required": ["session_id", "customer_id", "name"]
        }
    ),
    Tool(
        name="get_audience_insights",
        description="Get audience demographics, interests, and behavior data.",
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
        name="get_recommendations",
        description="Surface Google's AI optimization suggestions for your campaigns.",
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
        name="apply_recommendation",
        description="One-click apply any optimization recommendation from Google.",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "customer_id": {"type": "string"},
                "recommendation_resource_name": {"type": "string", "description": "Resource name of the recommendation"}
            },
            "required": ["session_id", "customer_id", "recommendation_resource_name"]
        }
    ),
    Tool(
        name="dismiss_recommendation",
        description="Dismiss irrelevant recommendations to keep your list clean.",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "customer_id": {"type": "string"},
                "recommendation_resource_name": {"type": "string", "description": "Resource name of the recommendation"}
            },
            "required": ["session_id", "customer_id", "recommendation_resource_name"]
        }
    ),
    Tool(
        name="generate_keyword_ideas",
        description="Discover new keyword opportunities based on seed terms.",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "customer_id": {"type": "string"},
                "seed_keywords": {"type": "array", "description": "List of seed keywords", "items": {"type": "string"}},
                "language_id": {"type": "string", "description": "Language ID (default 1000 = English)", "default": "1000"},
                "location_ids": {"type": "array", "description": "Optional location IDs", "items": {"type": "string"}}
            },
            "required": ["session_id", "customer_id", "seed_keywords"]
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
            "list_accessible_customers": tools.list_accessible_customers,
            "list_accounts": tools.list_accounts,
            "get_account_summary": tools.get_account_summary,
            "get_account_budget": tools.get_account_budget,
            "get_billing_summary": tools.get_billing_summary,
            "list_campaigns": tools.list_campaigns,
            "create_campaign": tools.create_campaign,
            "get_campaign_performance": tools.get_campaign_performance,
            "update_campaign": tools.update_campaign,
            "pause_campaign": tools.pause_campaign,
            "enable_campaign": tools.enable_campaign,
            "update_campaign_budget": tools.update_campaign_budget,
            "list_ad_groups": tools.list_ad_groups,
            "get_ad_group_performance": tools.get_ad_group_performance,
            "create_ad_group": tools.create_ad_group,
            "update_ad_group": tools.update_ad_group,
            "get_keywords": tools.get_keywords,
            "get_keyword_performance": tools.get_keyword_performance,
            "add_keywords": tools.add_keywords,
            "update_keyword_bid": tools.update_keyword_bid,
            "get_ad_performance": tools.get_ad_performance,
            "create_responsive_search_ad": tools.create_responsive_search_ad,
            "update_ad": tools.update_ad,
            "get_conversion_actions": tools.get_conversion_actions,
            "create_conversion_action": tools.create_conversion_action,
            "get_audience_insights": tools.get_audience_insights,
            "get_recommendations": tools.get_recommendations,
            "apply_recommendation": tools.apply_recommendation,
            "dismiss_recommendation": tools.dismiss_recommendation,
            "generate_keyword_ideas": tools.generate_keyword_ideas,
            "get_search_terms_report": tools.get_search_terms_report
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