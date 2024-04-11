import requests
import json
import hashlib
from forex_python.converter import CurrencyRates
from datetime import datetime


def get_campaigns_and_currency(meta_long_token):
    # retrieve campaign IDs
    url = "https://graph.facebook.com/v18.0/me/adaccounts?fields=campaigns,currency"
    params = {"access_token": meta_long_token, "level": "campaign"}
    response = requests.get(url, params=params)
    ad_accounts_data = response.json()

    # initialize an empty dictionary
    campaign_dict = {}

    for data in ad_accounts_data["data"]:
        if "campaigns" in data:
            for campaign_id in data["campaigns"]["data"]:
                campaign_dict[campaign_id["id"]] = data["currency"]

    return campaign_dict


def get_meta_insights(meta_long_token, campaign_dict):
    batch_requests = []

    campaign_ids = list(campaign_dict.keys())
    for campaign_id in campaign_ids:
        request = {
            "method": "GET",
            "name": campaign_id,
            "relative_url": f"{campaign_id}/insights?date_preset=maximum&fields=campaign_id,campaign_name,spend,created_time",
        }
        batch_requests.append(request)

    batch_payload = json.dumps(batch_requests)
    batch_params = {
        "access_token": meta_long_token,
        "batch": batch_payload,
    }

    graph_api_url = "https://graph.facebook.com/v18.0"

    response = requests.post(graph_api_url, params=batch_params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to obtain Meta transactions")


def format_meta_transactions(meta_transactions, campaign_dict):
    rows = []
    c = CurrencyRates()

    for campaign_response in meta_transactions:
        campaign_body = json.loads(campaign_response["body"])["data"]
        if campaign_body:
            campaign_data = campaign_body[0]
            campaign_name = campaign_data["campaign_name"]
            campaign_time = campaign_data["created_time"]

            # spending: convert currency
            campaign_currency = campaign_dict[campaign_data["campaign_id"]]
            spend_in_currency = float(campaign_data["spend"]) * -1
            if campaign_currency == "AUD":
                campaign_spend = round(
                    c.convert(
                        "AUD",
                        "USD",
                        spend_in_currency,
                        datetime.strptime(campaign_time, "%Y-%m-%d"),
                    ),
                    2,
                )
            else:
                campaign_spend = spend_in_currency

            # hash transaction_id
            transaction_id = (
                f"meta:{hashlib.sha256((campaign_name).encode()).hexdigest()}"
            )

            row = [
                transaction_id,
                "meta",
                campaign_time,
                campaign_name[:4],
                "ads",
                campaign_spend,
            ]
            rows.append(row)

    return rows
