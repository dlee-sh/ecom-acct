import requests
import hashlib
from datetime import datetime, timedelta


def authenticate_paypal(client_id, client_secret):
    token_url = "https://api-m.paypal.com/v1/oauth2/token"
    headers = {"Accept": "application/json", "Accept-Language": "en_US"}
    data = {"grant_type": "client_credentials"}
    auth = (client_id, client_secret)

    response = requests.post(token_url, headers=headers, data=data, auth=auth)

    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception("Failed to obtain access token")


def get_paypal_data(access_token):
    transactions_url = "https://api-m.paypal.com/v1/reporting/transactions"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # this means we need to run the script once a month
    current_time = datetime.now()
    start_date = current_time - timedelta(days=31)
    end_date_str = current_time.strftime("%Y-%m-%dT%H:%M:%S-0700")
    start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%S-0700")

    params = (
        ("start_date", start_date_str),
        ("end_date", end_date_str),
        ("fields", "all"),
        ("page_size", "100"),
        ("page", "1"),
    )

    response = requests.get(transactions_url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to retrieve transactions")


def get_paypal_transactions(transactions):
    rows = []
    for transaction in transactions["transaction_details"]:
        transaction_info = transaction["transaction_info"]
        cart_info = transaction["cart_info"]

        if (
            "custom_field" in transaction_info
            and transaction_info["custom_field"] == "Shopify"
        ):
            transaction_id = transaction_info["transaction_id"]
            id = f"payp:{hashlib.sha256(transaction_id.encode()).hexdigest()}"

            timestamp = datetime.strptime(
                transaction_info["transaction_initiation_date"], "%Y-%m-%dT%H:%M:%S%z"
            )
            formatted_timestamp = timestamp.strftime("%Y-%m-%d")

            status = (
                "refund" if transaction_info["transaction_status"] == "V" else "charge"
            )
            product_name = cart_info["item_details"][0]["item_name"]
            store_name = product_name.split()[0]
            net_inflow = float(transaction_info["transaction_amount"]["value"]) + float(
                transaction_info["fee_amount"]["value"]
            )

            row = [id, formatted_timestamp, store_name, status, net_inflow]
            rows.append(row)

    return rows
