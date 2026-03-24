"""MCP tools for Google Ads operations."""
import os
from typing import Any, Dict, List, Optional
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import auth

def get_google_ads_client(session_id: str) -> GoogleAdsClient:
    """Create Google Ads client with session credentials."""
    credentials = auth.get_credentials(session_id)
    if not credentials:
        raise ValueError(f"No credentials found for session {session_id}")
    
    # Refresh if needed
    auth.refresh_token_if_needed(session_id)
    credentials = auth.get_credentials(session_id)
    
    # Create Google Ads client
    client = GoogleAdsClient(
        credentials=credentials,
        developer_token=os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
        use_proto_plus=True
    )
    
    return client

async def connect_google_ads(session_id: str) -> Dict[str, str]:
    """Generate OAuth URL for user to connect Google Ads account."""
    auth_url = auth.get_auth_url(session_id)
    return {
        "auth_url": auth_url,
        "message": "Click the URL above to authorize access to your Google Ads account.",
        "session_id": session_id
    }

async def list_accounts(session_id: str) -> List[Dict[str, Any]]:
    """List all accessible Google Ads accounts."""
    try:
        client = get_google_ads_client(session_id)
        customer_service = client.get_service("CustomerService")
        
        # Get accessible customers
        accessible_customers = customer_service.list_accessible_customers()
        customer_ids = [
            customer.split('/')[-1] 
            for customer in accessible_customers.resource_names
        ]
        
        # Get details for each customer
        accounts = []
        for customer_id in customer_ids:
            try:
                ga_service = client.get_service("GoogleAdsService")
                query = """
                    SELECT
                        customer.id,
                        customer.descriptive_name,
                        customer.currency_code,
                        customer.time_zone,
                        customer.status
                    FROM customer
                    LIMIT 1
                """
                response = ga_service.search(customer_id=customer_id, query=query)
                
                for row in response:
                    accounts.append({
                        "customer_id": str(row.customer.id),
                        "name": row.customer.descriptive_name,
                        "currency": row.customer.currency_code,
                        "timezone": row.customer.time_zone,
                        "status": row.customer.status.name
                    })
            except GoogleAdsException:
                # Skip accounts we can't access
                continue
        
        return accounts
    
    except Exception as e:
        return {"error": str(e)}

async def get_account_summary(
    session_id: str,
    customer_id: str,
    date_from: str = "2024-01-01",
    date_to: str = "2024-12-31"
) -> Dict[str, Any]:
    """Get account summary metrics for a date range."""
    try:
        client = get_google_ads_client(session_id)
        ga_service = client.get_service("GoogleAdsService")
        
        query = f"""
            SELECT
                metrics.cost_micros,
                metrics.impressions,
                metrics.clicks,
                metrics.conversions,
                metrics.conversions_value,
                metrics.ctr,
                metrics.average_cpc
            FROM customer
            WHERE segments.date BETWEEN '{date_from}' AND '{date_to}'
        """
        
        response = ga_service.search(customer_id=customer_id, query=query)
        
        total_cost = 0
        total_impressions = 0
        total_clicks = 0
        total_conversions = 0
        total_conversion_value = 0
        
        for row in response:
            total_cost += row.metrics.cost_micros
            total_impressions += row.metrics.impressions
            total_clicks += row.metrics.clicks
            total_conversions += row.metrics.conversions
            total_conversion_value += row.metrics.conversions_value
        
        return {
            "customer_id": customer_id,
            "date_range": f"{date_from} to {date_to}",
            "spend": total_cost / 1_000_000,
            "impressions": total_impressions,
            "clicks": total_clicks,
            "conversions": total_conversions,
            "conversion_value": total_conversion_value,
            "ctr": (total_clicks / total_impressions * 100) if total_impressions > 0 else 0,
            "avg_cpc": (total_cost / 1_000_000 / total_clicks) if total_clicks > 0 else 0
        }
    
    except Exception as e:
        return {"error": str(e)}

async def list_campaigns(session_id: str, customer_id: str) -> List[Dict[str, Any]]:
    """List all campaigns with status and budget."""
    try:
        client = get_google_ads_client(session_id)
        ga_service = client.get_service("GoogleAdsService")
        
        query = """
            SELECT
                campaign.id,
                campaign.name,
                campaign.status,
                campaign.advertising_channel_type,
                campaign_budget.amount_micros,
                metrics.cost_micros,
                metrics.impressions,
                metrics.clicks
            FROM campaign
            ORDER BY campaign.name
        """
        
        response = ga_service.search(customer_id=customer_id, query=query)
        
        campaigns = []
        for row in response:
            campaigns.append({
                "id": str(row.campaign.id),
                "name": row.campaign.name,
                "status": row.campaign.status.name,
                "type": row.campaign.advertising_channel_type.name,
                "budget_micros": row.campaign_budget.amount_micros,
                "spend_micros": row.metrics.cost_micros,
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks
            })
        
        return campaigns
    
    except Exception as e:
        return {"error": str(e)}

async def get_campaign_performance(
    session_id: str,
    customer_id: str,
    campaign_id: str,
    date_from: str = "2024-01-01",
    date_to: str = "2024-12-31"
) -> Dict[str, Any]:
    """Get detailed performance metrics for a specific campaign."""
    try:
        client = get_google_ads_client(session_id)
        ga_service = client.get_service("GoogleAdsService")
        
        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                metrics.cost_micros,
                metrics.impressions,
                metrics.clicks,
                metrics.conversions,
                metrics.conversions_value,
                metrics.ctr,
                metrics.average_cpc,
                metrics.average_cpm
            FROM campaign
            WHERE campaign.id = {campaign_id}
                AND segments.date BETWEEN '{date_from}' AND '{date_to}'
        """
        
        response = ga_service.search(customer_id=customer_id, query=query)
        
        for row in response:
            return {
                "campaign_id": str(row.campaign.id),
                "campaign_name": row.campaign.name,
                "date_range": f"{date_from} to {date_to}",
                "spend": row.metrics.cost_micros / 1_000_000,
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "conversions": row.metrics.conversions,
                "conversion_value": row.metrics.conversions_value,
                "ctr": row.metrics.ctr * 100,
                "avg_cpc": row.metrics.average_cpc / 1_000_000,
                "avg_cpm": row.metrics.average_cpm / 1_000_000
            }
        
        return {"error": "Campaign not found"}
    
    except Exception as e:
        return {"error": str(e)}

async def list_ad_groups(session_id: str, customer_id: str, campaign_id: str) -> List[Dict[str, Any]]:
    """List ad groups for a campaign."""
    try:
        client = get_google_ads_client(session_id)
        ga_service = client.get_service("GoogleAdsService")
        
        query = f"""
            SELECT
                ad_group.id,
                ad_group.name,
                ad_group.status,
                ad_group.cpc_bid_micros,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros
            FROM ad_group
            WHERE campaign.id = {campaign_id}
            ORDER BY ad_group.name
        """
        
        response = ga_service.search(customer_id=customer_id, query=query)
        
        ad_groups = []
        for row in response:
            ad_groups.append({
                "id": str(row.ad_group.id),
                "name": row.ad_group.name,
                "status": row.ad_group.status.name,
                "cpc_bid": row.ad_group.cpc_bid_micros / 1_000_000 if row.ad_group.cpc_bid_micros else None,
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "spend": row.metrics.cost_micros / 1_000_000
            })
        
        return ad_groups
    
    except Exception as e:
        return {"error": str(e)}

async def get_keywords(session_id: str, customer_id: str, ad_group_id: str) -> List[Dict[str, Any]]:
    """Get keyword performance with quality scores."""
    try:
        client = get_google_ads_client(session_id)
        ga_service = client.get_service("GoogleAdsService")
        
        query = f"""
            SELECT
                ad_group_criterion.keyword.text,
                ad_group_criterion.keyword.match_type,
                ad_group_criterion.quality_info.quality_score,
                ad_group_criterion.status,
                ad_group_criterion.cpc_bid_micros,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions
            FROM keyword_view
            WHERE ad_group.id = {ad_group_id}
            ORDER BY metrics.impressions DESC
        """
        
        response = ga_service.search(customer_id=customer_id, query=query)
        
        keywords = []
        for row in response:
            keywords.append({
                "keyword": row.ad_group_criterion.keyword.text,
                "match_type": row.ad_group_criterion.keyword.match_type.name,
                "quality_score": row.ad_group_criterion.quality_info.quality_score,
                "status": row.ad_group_criterion.status.name,
                "cpc_bid": row.ad_group_criterion.cpc_bid_micros / 1_000_000 if row.ad_group_criterion.cpc_bid_micros else None,
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "spend": row.metrics.cost_micros / 1_000_000,
                "conversions": row.metrics.conversions
            })
        
        return keywords
    
    except Exception as e:
        return {"error": str(e)}

async def get_search_terms_report(
    session_id: str,
    customer_id: str,
    campaign_id: Optional[str] = None,
    date_from: str = "2024-01-01",
    date_to: str = "2024-12-31"
) -> List[Dict[str, Any]]:
    """Get search terms that triggered ads."""
    try:
        client = get_google_ads_client(session_id)
        ga_service = client.get_service("GoogleAdsService")
        
        campaign_filter = f"AND campaign.id = {campaign_id}" if campaign_id else ""
        
        query = f"""
            SELECT
                search_term_view.search_term,
                search_term_view.status,
                ad_group.name,
                campaign.name,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions
            FROM search_term_view
            WHERE segments.date BETWEEN '{date_from}' AND '{date_to}'
                {campaign_filter}
            ORDER BY metrics.impressions DESC
            LIMIT 100
        """
        
        response = ga_service.search(customer_id=customer_id, query=query)
        
        search_terms = []
        for row in response:
            search_terms.append({
                "search_term": row.search_term_view.search_term,
                "status": row.search_term_view.status.name,
                "ad_group": row.ad_group.name,
                "campaign": row.campaign.name,
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "spend": row.metrics.cost_micros / 1_000_000,
                "conversions": row.metrics.conversions
            })
        
        return search_terms
    
    except Exception as e:
        return {"error": str(e)}

async def pause_campaign(session_id: str, customer_id: str, campaign_id: str) -> Dict[str, Any]:
    """Pause a campaign."""
    try:
        client = get_google_ads_client(session_id)
        campaign_service = client.get_service("CampaignService")
        
        campaign_operation = client.get_type("CampaignOperation")
        campaign = campaign_operation.update
        campaign.resource_name = campaign_service.campaign_path(customer_id, campaign_id)
        campaign.status = client.enums.CampaignStatusEnum.PAUSED
        
        client.copy_from(
            campaign_operation.update_mask,
            client.get_type("FieldMask"),
            paths=["status"]
        )
        
        campaign_service.mutate_campaigns(
            customer_id=customer_id,
            operations=[campaign_operation]
        )
        
        return {
            "success": True,
            "campaign_id": campaign_id,
            "new_status": "PAUSED"
        }
    
    except Exception as e:
        return {"error": str(e)}

async def enable_campaign(session_id: str, customer_id: str, campaign_id: str) -> Dict[str, Any]:
    """Enable a campaign."""
    try:
        client = get_google_ads_client(session_id)
        campaign_service = client.get_service("CampaignService")
        
        campaign_operation = client.get_type("CampaignOperation")
        campaign = campaign_operation.update
        campaign.resource_name = campaign_service.campaign_path(customer_id, campaign_id)
        campaign.status = client.enums.CampaignStatusEnum.ENABLED
        
        client.copy_from(
            campaign_operation.update_mask,
            client.get_type("FieldMask"),
            paths=["status"]
        )
        
        campaign_service.mutate_campaigns(
            customer_id=customer_id,
            operations=[campaign_operation]
        )
        
        return {
            "success": True,
            "campaign_id": campaign_id,
            "new_status": "ENABLED"
        }
    
    except Exception as e:
        return {"error": str(e)}

async def update_campaign_budget(
    session_id: str,
    customer_id: str,
    campaign_id: str,
    budget_amount: float
) -> Dict[str, Any]:
    """Update campaign daily budget."""
    try:
        client = get_google_ads_client(session_id)
        
        # First get the campaign budget ID
        ga_service = client.get_service("GoogleAdsService")
        query = f"""
            SELECT campaign.campaign_budget
            FROM campaign
            WHERE campaign.id = {campaign_id}
        """
        response = ga_service.search(customer_id=customer_id, query=query)
        
        budget_resource_name = None
        for row in response:
            budget_resource_name = row.campaign.campaign_budget
            break
        
        if not budget_resource_name:
            return {"error": "Campaign budget not found"}
        
        # Update the budget
        campaign_budget_service = client.get_service("CampaignBudgetService")
        campaign_budget_operation = client.get_type("CampaignBudgetOperation")
        campaign_budget = campaign_budget_operation.update
        campaign_budget.resource_name = budget_resource_name
        campaign_budget.amount_micros = int(budget_amount * 1_000_000)
        
        client.copy_from(
            campaign_budget_operation.update_mask,
            client.get_type("FieldMask"),
            paths=["amount_micros"]
        )
        
        campaign_budget_service.mutate_campaign_budgets(
            customer_id=customer_id,
            operations=[campaign_budget_operation]
        )
        
        return {
            "success": True,
            "campaign_id": campaign_id,
            "new_budget": budget_amount
        }
    
    except Exception as e:
        return {"error": str(e)}
