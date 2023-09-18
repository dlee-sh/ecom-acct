import requests
import json
import hashlib


def get_campaigns(access_token):
    # retrieve campaign IDs
    url = "https://graph.facebook.com/v18.0/me/adaccounts?fields=campaigns"
    params = {"access_token": access_token, "level": "campaign"}

    response = requests.get(url, params=params)
    ad_accounts_data = response.json()

    campaign_ids = []

    for data in ad_accounts_data["data"]:
        if "campaigns" in data:
            for campaign_id in data["campaigns"]["data"]:
                campaign_ids.append(campaign_id["id"])

    return campaign_ids


def get_meta_transactions(access_token, campaign_ids):
    batch_requests = []

    for campaign_id in campaign_ids:
        request = {
            "method": "GET",
            "name": campaign_id,
            "relative_url": f"{campaign_id}/insights?fields=campaign_name,spend,created_time",
        }
        batch_requests.append(request)

    batch_payload = json.dumps(batch_requests)

    graph_api_url = "https://graph.facebook.com/v18.0"

    batch_params = {
        "access_token": access_token,
        "batch": batch_payload,
    }
    campaign_responses = requests.post(graph_api_url, params=batch_params)

    rows = []
    for campaign_response in campaign_responses.json():
        campaign_body = json.loads(campaign_response["body"])["data"]
        if campaign_body:
            campaign_data = campaign_body[0]
            campaign_name = campaign_data["campaign_name"]
            store_name = campaign_name[:4]
            campaign_spend = float(campaign_data["spend"]) * -1
            campaign_time = campaign_data["created_time"]
            campaign_id = f"meta:{hashlib.sha256((campaign_name).encode()).hexdigest()}"
            row = [campaign_id, campaign_time, store_name, "ads", campaign_spend]
            rows.append(row)

    return rows
