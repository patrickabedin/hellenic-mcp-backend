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

async def connect_google_ads(session_id: str = None) -> Dict[str, str]:
    """Generate OAuth URL for user to connect Google Ads account.
    
    Uses stateless flow so credentials survive Render restarts.
    """
    import secrets
    from datetime import datetime, timedelta
    
    if not session_id:
        session_id = secrets.token_urlsafe(24)
    
    # Create stateless auth URL (survives DB wipes)
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = auth._b64url_sha256(code_verifier)
    
    state_payload = {
        "session_id": session_id,
        "client_id": "manual_flow",
        "redirect_uri": f"{os.getenv('PUBLIC_BASE_URL', 'https://api.google-ads-mcp.hellenicai.com')}/oauth/callback",
        "code_challenge": code_challenge,
        "code_verifier": code_verifier,
        "exp": int((datetime.utcnow() + timedelta(minutes=10)).timestamp()),
    }
    signed_state = auth._sign_state(state_payload)
    
    auth_url = auth.get_auth_url_for_connector(signed_state, code_verifier)
    
    return {
        "auth_url": auth_url,
        "message": "Click the URL above to authorize access to your Google Ads account. After authorization, copy the session token from the success page and provide it here.",
        "session_id": session_id
    }

async def list_accessible_customers(session_id: str) -> List[Dict[str, Any]]:
    """List all accessible Google Ads customer accounts (MCC + direct)."""
    try:
        client = get_google_ads_client(session_id)
        customer_service = client.get_service("CustomerService")
        
        accessible_customers = customer_service.list_accessible_customers()
        customers = []
        for resource_name in accessible_customers.resource_names:
            customer_id = resource_name.split('/')[-1]
            customers.append({"customer_id": customer_id, "resource_name": resource_name})
        
        return customers
    except Exception as e:
        return {"error": str(e)}

async def list_accounts(session_id: str) -> List[Dict[str, Any]]:
    """List all accessible Google Ads accounts with details."""
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

async def list_mcc_child_accounts(session_id: str, manager_customer_id: str) -> List[Dict[str, Any]]:
    """List all child accounts under a Manager/MCC account.
    
    This queries the Google Ads API using the MCC as login-customer-id
    to discover all accessible child accounts in the hierarchy.
    """
    try:
        client = get_google_ads_client(session_id)
        
        # Use CustomerService with login-customer-id set to the MCC
        # This allows querying child accounts under the manager
        customer_service = client.get_service("CustomerService")
        
        # Set login-customer-id to the MCC for this request
        # This is the key to accessing child accounts
        from google.ads.googleads.client import GoogleAdsClient
        credentials = auth.get_credentials(session_id)
        
        # Create client with login-customer-id set to MCC
        mcc_client = GoogleAdsClient(
            credentials=credentials,
            developer_token=os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
            use_proto_plus=True,
            login_customer_id=manager_customer_id
        )
        
        # List accessible customers under this MCC
        mcc_customer_service = mcc_client.get_service("CustomerService")
        accessible_customers = mcc_customer_service.list_accessible_customers()
        
        child_accounts = []
        for resource_name in accessible_customers.resource_names:
            customer_id = resource_name.split('/')[-1]
            # Skip the MCC itself
            if customer_id == manager_customer_id:
                continue
                
            try:
                ga_service = mcc_client.get_service("GoogleAdsService")
                query = """
                    SELECT
                        customer.id,
                        customer.descriptive_name,
                        customer.currency_code,
                        customer.time_zone,
                        customer.status,
                        customer.manager
                    FROM customer
                    LIMIT 1
                """
                response = ga_service.search(customer_id=customer_id, query=query)
                
                for row in response:
                    child_accounts.append({
                        "customer_id": str(row.customer.id),
                        "name": row.customer.descriptive_name,
                        "currency": row.customer.currency_code,
                        "timezone": row.customer.time_zone,
                        "status": row.customer.status.name,
                        "is_manager": row.customer.manager
                    })
            except GoogleAdsException:
                # Skip accounts we can't access
                continue
        
        return child_accounts
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

async def get_account_budget(session_id: str, customer_id: str) -> Dict[str, Any]:
    """Get account-level budget allocation and spend pacing."""
    try:
        client = get_google_ads_client(session_id)
        ga_service = client.get_service("GoogleAdsService")
        
        query = """
            SELECT
                account_budget.status,
                account_budget.amount_served_micros,
                account_budget.total_adjustments_micros,
                account_budget.approved_spending_limit_micros,
                account_budget.proposed_spending_limit_micros
            FROM account_budget
            LIMIT 1
        """
        
        response = ga_service.search(customer_id=customer_id, query=query)
        
        for row in response:
            return {
                "status": row.account_budget.status.name,
                "amount_served": row.account_budget.amount_served_micros / 1_000_000,
                "total_adjustments": row.account_budget.total_adjustments_micros / 1_000_000,
                "approved_spending_limit": row.account_budget.approved_spending_limit_micros / 1_000_000 if row.account_budget.approved_spending_limit_micros else None,
                "proposed_spending_limit": row.account_budget.proposed_spending_limit_micros / 1_000_000 if row.account_budget.proposed_spending_limit_micros else None
            }
        
        return {"error": "No account budget found"}
    except Exception as e:
        return {"error": str(e)}

async def get_billing_summary(session_id: str, customer_id: str) -> Dict[str, Any]:
    """Get billing summary: payment method health, account status, spend."""
    try:
        client = get_google_ads_client(session_id)
        ga_service = client.get_service("GoogleAdsService")
        
        query = """
            SELECT
                billing_setup.status,
                billing_setup.payments_account_info.payments_account_id,
                billing_setup.payments_account_info.payments_account_name,
                billing_setup.payments_account_info.currency_code
            FROM billing_setup
            LIMIT 1
        """
        
        response = ga_service.search(customer_id=customer_id, query=query)
        
        for row in response:
            return {
                "status": row.billing_setup.status.name,
                "payments_account_id": row.billing_setup.payments_account_info.payments_account_id,
                "payments_account_name": row.billing_setup.payments_account_info.payments_account_name,
                "currency_code": row.billing_setup.payments_account_info.currency_code
            }
        
        return {"error": "No billing setup found"}
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

async def create_campaign(
    session_id: str,
    customer_id: str,
    name: str,
    budget_amount: float,
    advertising_channel_type: str = "SEARCH"
) -> Dict[str, Any]:
    """Create new campaign with budget, channel type, and bidding strategy."""
    try:
        client = get_google_ads_client(session_id)
        
        # Create budget
        campaign_budget_service = client.get_service("CampaignBudgetService")
        campaign_budget_operation = client.get_type("CampaignBudgetOperation")
        campaign_budget = campaign_budget_operation.create
        campaign_budget.name = f"Budget for {name}"
        campaign_budget.amount_micros = int(budget_amount * 1_000_000)
        campaign_budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
        
        budget_response = campaign_budget_service.mutate_campaign_budgets(
            customer_id=customer_id,
            operations=[campaign_budget_operation]
        )
        budget_resource_name = budget_response.results[0].resource_name
        
        # Create campaign
        campaign_service = client.get_service("CampaignService")
        campaign_operation = client.get_type("CampaignOperation")
        campaign = campaign_operation.create
        campaign.name = name
        campaign.advertising_channel_type = getattr(
            client.enums.AdvertisingChannelTypeEnum, advertising_channel_type.upper()
        )
        campaign.status = client.enums.CampaignStatusEnum.PAUSED
        campaign.campaign_budget = budget_resource_name
        campaign.manual_cpc = client.get_type("ManualCpc")
        
        campaign_response = campaign_service.mutate_campaigns(
            customer_id=customer_id,
            operations=[campaign_operation]
        )
        
        return {
            "success": True,
            "campaign_id": campaign_response.results[0].resource_name.split('/')[-1],
            "campaign_name": name,
            "budget_amount": budget_amount
        }
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
                metrics.average_cpm,
                metrics.roas
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
                "avg_cpm": row.metrics.average_cpm / 1_000_000,
                "roas": row.metrics.roas
            }
        
        return {"error": "Campaign not found"}
    except Exception as e:
        return {"error": str(e)}

async def update_campaign(
    session_id: str,
    customer_id: str,
    campaign_id: str,
    name: Optional[str] = None,
    status: Optional[str] = None,
    budget_amount: Optional[float] = None
) -> Dict[str, Any]:
    """Modify campaign settings, budgets, and targeting parameters."""
    try:
        client = get_google_ads_client(session_id)
        campaign_service = client.get_service("CampaignService")
        
        campaign_operation = client.get_type("CampaignOperation")
        campaign = campaign_operation.update
        campaign.resource_name = campaign_service.campaign_path(customer_id, campaign_id)
        
        field_mask_paths = []
        
        if name:
            campaign.name = name
            field_mask_paths.append("name")
        
        if status:
            campaign.status = getattr(client.enums.CampaignStatusEnum, status.upper())
            field_mask_paths.append("status")
        
        if budget_amount:
            # Get current budget resource name
            ga_service = client.get_service("GoogleAdsService")
            query = f"""
                SELECT campaign.campaign_budget
                FROM campaign
                WHERE campaign.id = {campaign_id}
            """
            response = ga_service.search(customer_id=customer_id, query=query)
            for row in response:
                campaign.campaign_budget = row.campaign.campaign_budget
                field_mask_paths.append("campaign_budget")
                
                # Update budget separately
                campaign_budget_service = client.get_service("CampaignBudgetService")
                budget_operation = client.get_type("CampaignBudgetOperation")
                budget = budget_operation.update
                budget.resource_name = row.campaign.campaign_budget
                budget.amount_micros = int(budget_amount * 1_000_000)
                
                client.copy_from(
                    budget_operation.update_mask,
                    client.get_type("FieldMask"),
                    paths=["amount_micros"]
                )
                campaign_budget_service.mutate_campaign_budgets(
                    customer_id=customer_id,
                    operations=[budget_operation]
                )
                break
        
        client.copy_from(
            campaign_operation.update_mask,
            client.get_type("FieldMask"),
            paths=field_mask_paths
        )
        
        campaign_service.mutate_campaigns(
            customer_id=customer_id,
            operations=[campaign_operation]
        )
        
        return {
            "success": True,
            "campaign_id": campaign_id,
            "updated_fields": field_mask_paths
        }
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

async def get_ad_group_performance(
    session_id: str,
    customer_id: str,
    ad_group_id: str,
    date_from: str = "2024-01-01",
    date_to: str = "2024-12-31"
) -> Dict[str, Any]:
    """Get ad group-level metrics for granular performance analysis."""
    try:
        client = get_google_ads_client(session_id)
        ga_service = client.get_service("GoogleAdsService")
        
        query = f"""
            SELECT
                ad_group.id,
                ad_group.name,
                metrics.cost_micros,
                metrics.impressions,
                metrics.clicks,
                metrics.conversions,
                metrics.conversions_value,
                metrics.ctr,
                metrics.average_cpc
            FROM ad_group
            WHERE ad_group.id = {ad_group_id}
                AND segments.date BETWEEN '{date_from}' AND '{date_to}'
        """
        
        response = ga_service.search(customer_id=customer_id, query=query)
        
        for row in response:
            return {
                "ad_group_id": str(row.ad_group.id),
                "ad_group_name": row.ad_group.name,
                "date_range": f"{date_from} to {date_to}",
                "spend": row.metrics.cost_micros / 1_000_000,
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "conversions": row.metrics.conversions,
                "conversion_value": row.metrics.conversions_value,
                "ctr": row.metrics.ctr * 100,
                "avg_cpc": row.metrics.average_cpc / 1_000_000
            }
        
        return {"error": "Ad group not found"}
    except Exception as e:
        return {"error": str(e)}

async def create_ad_group(
    session_id: str,
    customer_id: str,
    campaign_id: str,
    name: str,
    cpc_bid: Optional[float] = None
) -> Dict[str, Any]:
    """Create ad groups within campaigns with custom bids and targeting."""
    try:
        client = get_google_ads_client(session_id)
        ad_group_service = client.get_service("AdGroupService")
        
        campaign_service = client.get_service("CampaignService")
        
        ad_group_operation = client.get_type("AdGroupOperation")
        ad_group = ad_group_operation.create
        ad_group.name = name
        ad_group.campaign = campaign_service.campaign_path(customer_id, campaign_id)
        ad_group.status = client.enums.AdGroupStatusEnum.ENABLED
        
        if cpc_bid:
            ad_group.cpc_bid_micros = int(cpc_bid * 1_000_000)
        
        response = ad_group_service.mutate_ad_groups(
            customer_id=customer_id,
            operations=[ad_group_operation]
        )
        
        return {
            "success": True,
            "ad_group_id": response.results[0].resource_name.split('/')[-1],
            "ad_group_name": name
        }
    except Exception as e:
        return {"error": str(e)}

async def update_ad_group(
    session_id: str,
    customer_id: str,
    ad_group_id: str,
    name: Optional[str] = None,
    status: Optional[str] = None,
    cpc_bid: Optional[float] = None
) -> Dict[str, Any]:
    """Modify ad group settings, bids, and status."""
    try:
        client = get_google_ads_client(session_id)
        ad_group_service = client.get_service("AdGroupService")
        
        ad_group_operation = client.get_type("AdGroupOperation")
        ad_group = ad_group_operation.update
        ad_group.resource_name = ad_group_service.ad_group_path(customer_id, ad_group_id)
        
        field_mask_paths = []
        
        if name:
            ad_group.name = name
            field_mask_paths.append("name")
        
        if status:
            ad_group.status = getattr(client.enums.AdGroupStatusEnum, status.upper())
            field_mask_paths.append("status")
        
        if cpc_bid:
            ad_group.cpc_bid_micros = int(cpc_bid * 1_000_000)
            field_mask_paths.append("cpc_bid_micros")
        
        client.copy_from(
            ad_group_operation.update_mask,
            client.get_type("FieldMask"),
            paths=field_mask_paths
        )
        
        ad_group_service.mutate_ad_groups(
            customer_id=customer_id,
            operations=[ad_group_operation]
        )
        
        return {
            "success": True,
            "ad_group_id": ad_group_id,
            "updated_fields": field_mask_paths
        }
    except Exception as e:
        return {"error": str(e)}

async def get_keywords(session_id: str, customer_id: str, ad_group_id: str) -> List[Dict[str, Any]]:
    """Get keyword performance with quality scores."""
    try:
        client = get_google_ads_client(session_id)
        ga_service = client.get_service("GoogleAdsService")
        
        query = f"""
            SELECT
                ad_group_criterion.criterion_id,
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
                "criterion_id": str(row.ad_group_criterion.criterion_id),
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

async def get_keyword_performance(
    session_id: str,
    customer_id: str,
    criterion_id: str,
    date_from: str = "2024-01-01",
    date_to: str = "2024-12-31"
) -> Dict[str, Any]:
    """Get keyword performance with quality scores — optimize what works."""
    try:
        client = get_google_ads_client(session_id)
        ga_service = client.get_service("GoogleAdsService")
        
        query = f"""
            SELECT
                ad_group_criterion.criterion_id,
                ad_group_criterion.keyword.text,
                ad_group_criterion.keyword.match_type,
                ad_group_criterion.quality_info.quality_score,
                metrics.cost_micros,
                metrics.impressions,
                metrics.clicks,
                metrics.conversions,
                metrics.conversions_value,
                metrics.ctr,
                metrics.average_cpc
            FROM keyword_view
            WHERE ad_group_criterion.criterion_id = {criterion_id}
                AND segments.date BETWEEN '{date_from}' AND '{date_to}'
        """
        
        response = ga_service.search(customer_id=customer_id, query=query)
        
        for row in response:
            return {
                "criterion_id": str(row.ad_group_criterion.criterion_id),
                "keyword": row.ad_group_criterion.keyword.text,
                "match_type": row.ad_group_criterion.keyword.match_type.name,
                "quality_score": row.ad_group_criterion.quality_info.quality_score,
                "date_range": f"{date_from} to {date_to}",
                "spend": row.metrics.cost_micros / 1_000_000,
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "conversions": row.metrics.conversions,
                "conversion_value": row.metrics.conversions_value,
                "ctr": row.metrics.ctr * 100,
                "avg_cpc": row.metrics.average_cpc / 1_000_000
            }
        
        return {"error": "Keyword not found"}
    except Exception as e:
        return {"error": str(e)}

async def add_keywords(
    session_id: str,
    customer_id: str,
    ad_group_id: str,
    keywords: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Add new keywords to ad groups with match types and bids."""
    try:
        client = get_google_ads_client(session_id)
        ad_group_criterion_service = client.get_service("AdGroupCriterionService")
        
        operations = []
        for kw in keywords:
            operation = client.get_type("AdGroupCriterionOperation")
            criterion = operation.create
            criterion.ad_group = client.get_service("AdGroupService").ad_group_path(customer_id, ad_group_id)
            criterion.keyword.text = kw["text"]
            criterion.keyword.match_type = getattr(
                client.enums.KeywordMatchTypeEnum, kw.get("match_type", "BROAD").upper()
            )
            criterion.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
            
            if "cpc_bid" in kw:
                criterion.cpc_bid_micros = int(kw["cpc_bid"] * 1_000_000)
            
            operations.append(operation)
        
        response = ad_group_criterion_service.mutate_ad_group_criteria(
            customer_id=customer_id,
            operations=operations
        )
        
        return {
            "success": True,
            "added_count": len(response.results),
            "keyword_ids": [r.resource_name.split('/')[-1] for r in response.results]
        }
    except Exception as e:
        return {"error": str(e)}

async def update_keyword_bid(
    session_id: str,
    customer_id: str,
    ad_group_id: str,
    criterion_id: str,
    cpc_bid: float
) -> Dict[str, Any]:
    """Adjust keyword-level bids for optimal cost-per-click."""
    try:
        client = get_google_ads_client(session_id)
        ad_group_criterion_service = client.get_service("AdGroupCriterionService")
        
        operation = client.get_type("AdGroupCriterionOperation")
        criterion = operation.update
        criterion.resource_name = ad_group_criterion_service.ad_group_criterion_path(
            customer_id, ad_group_id, criterion_id
        )
        criterion.cpc_bid_micros = int(cpc_bid * 1_000_000)
        
        client.copy_from(
            operation.update_mask,
            client.get_type("FieldMask"),
            paths=["cpc_bid_micros"]
        )
        
        ad_group_criterion_service.mutate_ad_group_criteria(
            customer_id=customer_id,
            operations=[operation]
        )
        
        return {
            "success": True,
            "criterion_id": criterion_id,
            "new_cpc_bid": cpc_bid
        }
    except Exception as e:
        return {"error": str(e)}

async def get_ad_performance(
    session_id: str,
    customer_id: str,
    ad_group_id: str,
    date_from: str = "2024-01-01",
    date_to: str = "2024-12-31"
) -> List[Dict[str, Any]]:
    """Get ad creative performance metrics and engagement data."""
    try:
        client = get_google_ads_client(session_id)
        ga_service = client.get_service("GoogleAdsService")
        
        query = f"""
            SELECT
                ad_group_ad.ad.id,
                ad_group_ad.status,
                ad_group_ad.ad.responsive_search_ad.headlines,
                ad_group_ad.ad.responsive_search_ad.descriptions,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions
            FROM ad_group_ad
            WHERE ad_group.id = {ad_group_id}
                AND segments.date BETWEEN '{date_from}' AND '{date_to}'
        """
        
        response = ga_service.search(customer_id=customer_id, query=query)
        
        ads = []
        for row in response:
            headlines = [h.text for h in row.ad_group_ad.ad.responsive_search_ad.headlines]
            descriptions = [d.text for d in row.ad_group_ad.ad.responsive_search_ad.descriptions]
            
            ads.append({
                "ad_id": str(row.ad_group_ad.ad.id),
                "status": row.ad_group_ad.status.name,
                "headlines": headlines,
                "descriptions": descriptions,
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "spend": row.metrics.cost_micros / 1_000_000,
                "conversions": row.metrics.conversions
            })
        
        return ads
    except Exception as e:
        return {"error": str(e)}

async def create_responsive_search_ad(
    session_id: str,
    customer_id: str,
    ad_group_id: str,
    headlines: List[str],
    descriptions: List[str],
    final_url: str
) -> Dict[str, Any]:
    """Build responsive search ads with multiple headlines and descriptions."""
    try:
        client = get_google_ads_client(session_id)
        ad_group_ad_service = client.get_service("AdGroupAdService")
        
        operation = client.get_type("AdGroupAdOperation")
        ad_group_ad = operation.create
        ad_group_ad.ad_group = client.get_service("AdGroupService").ad_group_path(customer_id, ad_group_id)
        ad_group_ad.status = client.enums.AdGroupAdStatusEnum.PAUSED
        
        # Set final URL
        ad_group_ad.ad.final_urls.append(final_url)
        
        # Add headlines
        for headline_text in headlines:
            headline = client.get_type("AdTextAsset")
            headline.text = headline_text
            ad_group_ad.ad.responsive_search_ad.headlines.append(headline)
        
        # Add descriptions
        for desc_text in descriptions:
            description = client.get_type("AdTextAsset")
            description.text = desc_text
            ad_group_ad.ad.responsive_search_ad.descriptions.append(description)
        
        response = ad_group_ad_service.mutate_ad_group_ads(
            customer_id=customer_id,
            operations=[operation]
        )
        
        return {
            "success": True,
            "ad_id": response.results[0].resource_name.split('/')[-1],
            "headlines_count": len(headlines),
            "descriptions_count": len(descriptions)
        }
    except Exception as e:
        return {"error": str(e)}

async def update_ad(
    session_id: str,
    customer_id: str,
    ad_group_id: str,
    ad_id: str,
    status: Optional[str] = None
) -> Dict[str, Any]:
    """Modify existing ad copy, headlines, and descriptions."""
    try:
        client = get_google_ads_client(session_id)
        ad_group_ad_service = client.get_service("AdGroupAdService")
        
        operation = client.get_type("AdGroupAdOperation")
        ad_group_ad = operation.update
        ad_group_ad.resource_name = ad_group_ad_service.ad_group_ad_path(customer_id, ad_group_id, ad_id)
        
        if status:
            ad_group_ad.status = getattr(client.enums.AdGroupAdStatusEnum, status.upper())
        
        client.copy_from(
            operation.update_mask,
            client.get_type("FieldMask"),
            paths=["status"]
        )
        
        ad_group_ad_service.mutate_ad_group_ads(
            customer_id=customer_id,
            operations=[operation]
        )
        
        return {
            "success": True,
            "ad_id": ad_id,
            "updated_fields": ["status"] if status else []
        }
    except Exception as e:
        return {"error": str(e)}

async def get_conversion_actions(session_id: str, customer_id: str) -> List[Dict[str, Any]]:
    """View all conversion actions and tracking configuration."""
    try:
        client = get_google_ads_client(session_id)
        ga_service = client.get_service("GoogleAdsService")
        
        query = """
            SELECT
                conversion_action.id,
                conversion_action.name,
                conversion_action.status,
                conversion_action.type,
                conversion_action.category,
                conversion_action.counting_type,
                conversion_action.value_settings.default_value
            FROM conversion_action
            ORDER BY conversion_action.name
        """
        
        response = ga_service.search(customer_id=customer_id, query=query)
        
        actions = []
        for row in response:
            actions.append({
                "id": str(row.conversion_action.id),
                "name": row.conversion_action.name,
                "status": row.conversion_action.status.name,
                "type": row.conversion_action.type.name,
                "category": row.conversion_action.category.name,
                "counting_type": row.conversion_action.counting_type.name,
                "default_value": row.conversion_action.value_settings.default_value
            })
        
        return actions
    except Exception as e:
        return {"error": str(e)}

async def create_conversion_action(
    session_id: str,
    customer_id: str,
    name: str,
    category: str = "DEFAULT",
    value: Optional[float] = None
) -> Dict[str, Any]:
    """Set up new conversion tracking for key business events."""
    try:
        client = get_google_ads_client(session_id)
        conversion_action_service = client.get_service("ConversionActionService")
        
        operation = client.get_type("ConversionActionOperation")
        conversion_action = operation.create
        conversion_action.name = name
        conversion_action.type = client.enums.ConversionActionTypeEnum.WEBPAGE
        conversion_action.category = getattr(client.enums.ConversionActionCategoryEnum, category.upper())
        conversion_action.status = client.enums.ConversionActionStatusEnum.ENABLED
        
        if value:
            conversion_action.value_settings.default_value = value
            conversion_action.value_settings.always_use_default_value = True
        
        response = conversion_action_service.mutate_conversion_actions(
            customer_id=customer_id,
            operations=[operation]
        )
        
        return {
            "success": True,
            "conversion_action_id": response.results[0].resource_name.split('/')[-1],
            "name": name
        }
    except Exception as e:
        return {"error": str(e)}

async def get_audience_insights(session_id: str, customer_id: str) -> List[Dict[str, Any]]:
    """Get audience demographics, interests, and behavior data."""
    try:
        client = get_google_ads_client(session_id)
        ga_service = client.get_service("GoogleAdsService")
        
        query = """
            SELECT
                ad_group.id,
                ad_group.name,
                segments.age_range,
                segments.gender,
                metrics.impressions,
                metrics.clicks,
                metrics.conversions
            FROM ad_group
            WHERE segments.date DURING LAST_30_DAYS
        """
        
        response = ga_service.search(customer_id=customer_id, query=query)
        
        insights = []
        for row in response:
            insights.append({
                "ad_group_id": str(row.ad_group.id),
                "ad_group_name": row.ad_group.name,
                "age_range": row.segments.age_range.name,
                "gender": row.segments.gender.name,
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "conversions": row.metrics.conversions
            })
        
        return insights
    except Exception as e:
        return {"error": str(e)}

async def get_recommendations(session_id: str, customer_id: str) -> List[Dict[str, Any]]:
    """Surface Google's AI optimization suggestions for your campaigns."""
    try:
        client = get_google_ads_client(session_id)
        ga_service = client.get_service("GoogleAdsService")
        
        query = """
            SELECT
                recommendation.type,
                recommendation.campaign,
                recommendation.impact.base_metrics.clicks,
                recommendation.impact.base_metrics.conversions,
                recommendation.impact.base_metrics.cost_micros
            FROM recommendation
            ORDER BY recommendation.impact.base_metrics.conversions DESC
        """
        
        response = ga_service.search(customer_id=customer_id, query=query)
        
        recommendations = []
        for row in response:
            recommendations.append({
                "type": row.recommendation.type.name,
                "campaign": row.recommendation.campaign,
                "impact_clicks": row.recommendation.impact.base_metrics.clicks,
                "impact_conversions": row.recommendation.impact.base_metrics.conversions,
                "impact_cost": row.recommendation.impact.base_metrics.cost_micros / 1_000_000
            })
        
        return recommendations
    except Exception as e:
        return {"error": str(e)}

async def apply_recommendation(session_id: str, customer_id: str, recommendation_resource_name: str) -> Dict[str, Any]:
    """One-click apply any optimization recommendation from Google."""
    try:
        client = get_google_ads_client(session_id)
        recommendation_service = client.get_service("RecommendationService")
        
        operation = client.get_type("ApplyRecommendationOperation")
        operation.resource_name = recommendation_resource_name
        
        response = recommendation_service.mutate_recommendations(
            customer_id=customer_id,
            operations=[operation]
        )
        
        return {
            "success": True,
            "applied_resource": response.results[0].resource_name
        }
    except Exception as e:
        return {"error": str(e)}

async def dismiss_recommendation(session_id: str, customer_id: str, recommendation_resource_name: str) -> Dict[str, Any]:
    """Dismiss irrelevant recommendations to keep your list clean."""
    try:
        client = get_google_ads_client(session_id)
        recommendation_service = client.get_service("RecommendationService")
        
        operation = client.get_type("DismissRecommendationOperation")
        operation.resource_name = recommendation_resource_name
        
        response = recommendation_service.mutate_recommendations(
            customer_id=customer_id,
            operations=[operation]
        )
        
        return {
            "success": True,
            "dismissed_resource": response.results[0].resource_name
        }
    except Exception as e:
        return {"error": str(e)}

async def generate_keyword_ideas(
    session_id: str,
    customer_id: str,
    seed_keywords: List[str],
    language_id: str = "1000",
    location_ids: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """Discover new keyword opportunities based on seed terms."""
    try:
        client = get_google_ads_client(session_id)
        keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")
        
        # Build request
        request = client.get_type("GenerateKeywordIdeasRequest")
        request.customer_id = customer_id
        request.language = client.get_service("GoogleAdsService").language_constant_path(language_id)
        
        if location_ids:
            for loc_id in location_ids:
                request.geo_target_constants.append(
                    client.get_service("GoogleAdsService").geo_target_constant_path(loc_id)
                )
        
        # Add seed keywords
        for keyword in seed_keywords:
            keyword_seed = client.get_type("KeywordSeed")
            keyword_seed.keyword = keyword
            request.keyword_seed.keywords.append(keyword)
        
        response = keyword_plan_idea_service.generate_keyword_ideas(request=request)
        
        ideas = []
        for result in response.results:
            ideas.append({
                "keyword": result.text,
                "avg_monthly_searches": result.keyword_idea_metrics.avg_monthly_searches,
                "competition": result.keyword_idea_metrics.competition.name,
                "low_top_of_page_bid": result.keyword_idea_metrics.low_top_of_page_bid_micros / 1_000_000 if result.keyword_idea_metrics.low_top_of_page_bid_micros else None,
                "high_top_of_page_bid": result.keyword_idea_metrics.high_top_of_page_bid_micros / 1_000_000 if result.keyword_idea_metrics.high_top_of_page_bid_micros else None
            })
        
        return ideas
    except Exception as e:
        return {"error": str(e)}

async def get_search_terms_report(
    session_id: str,
    customer_id: str,
    campaign_id: Optional[str] = None,
    date_from: str = "2024-01-01",
    date_to: str = "2024-12-31"
) -> List[Dict[str, Any]]:
    """Get search terms that triggered ads — real user intent revealed."""
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