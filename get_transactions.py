from credentials import config
import stripe
from components.stripe_transactions import get_stripe_transactions
from components.paypal_transactions import (
    authenticate_paypal,
    get_paypal_data,
    get_paypal_transactions,
)
from components.meta_transactions import get_campaigns, get_meta_transactions
import json


def get_transactions(
    stripe_key, paypal_client_id, paypal_client_secret, meta_access_token
):
    stripe.api_key = stripe_key
    transactions = []

    # STRIPE
    balance_transaction = stripe.BalanceTransaction.list(
        limit=100, expand=["data.source"]
    )
    stripe_rows = get_stripe_transactions(balance_transaction)
    for row in stripe_rows:
        transactions.append(row)

    # PAYPAL
    paypal_access_token = authenticate_paypal(paypal_client_id, paypal_client_secret)
    paypal_data = get_paypal_data(paypal_access_token)
    paypal_rows = get_paypal_transactions(paypal_data)
    for row in paypal_rows:
        transactions.append(row)

    # META
    campaign_ids = get_campaigns(meta_access_token)
    meta_rows = get_meta_transactions(meta_access_token, campaign_ids)
    for row in meta_rows:
        transactions.append(row)

    # Shop name formatting
    with open("credentials/shops.json", "r") as json_file:
        shop_keys = json.load(json_file)

    print(f"Retrieved the following transactions:")
    for row in transactions:
        for key in shop_keys:
            if isinstance(row[2], str) and key["name"].lower() in row[2].lower():
                row[2] = key["pid"]
        print(row)

    return transactions
