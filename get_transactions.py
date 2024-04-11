import stripe
from components.stripe_transactions import get_stripe_transactions
from components.paypal_transactions import (
    get_paypal_data,
    get_paypal_transactions,
)
from components.meta_transactions import (
    get_campaigns_and_currency,
    get_meta_insights,
    format_meta_transactions,
)
import json

def get_transactions(stripe_key, paypal_access_token, meta_access_token):
    transactions = []

    # STRIPE
    stripe.api_key = stripe_key
    balance_transaction = stripe.BalanceTransaction.list(
        limit=100, expand=["data.source"]
    )
    stripe_rows = get_stripe_transactions(balance_transaction)
    for row in stripe_rows:
        transactions.append(row)

    # PAYPAL
    paypal_data = get_paypal_data(paypal_access_token)
    paypal_rows = get_paypal_transactions(paypal_data)
    for row in paypal_rows:
        transactions.append(row)

    # META
    campaign_dict = get_campaigns_and_currency(meta_access_token)
    meta_rows = get_meta_insights(meta_access_token, campaign_dict)
    formatted_meta_transactions = format_meta_transactions(meta_rows, campaign_dict)
    for row in formatted_meta_transactions:
        transactions.append(row)

    return transactions


def format_shop_name(transactions):
    # Shop name formatting
    with open("credentials/shops.json", "r") as json_file:
        shop_keys = json.load(json_file)

    for row in transactions:
        for key in shop_keys:
            if isinstance(row[3], str) and key["name"].lower() in row[3].lower():
                row[3] = key["pid"]

    return transactions

