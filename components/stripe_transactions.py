import datetime
import hashlib


# refunds don't have metadata, obtain from same payment intent
def get_shop_name(balance_transaction, payment_intent_id):
    for transaction in balance_transaction:
        if (
            "payment_intent" in transaction.source
            and transaction.source.payment_intent == payment_intent_id
            and transaction.type == "charge"
        ):
            return transaction.source["metadata"]["shop_name"]


def get_stripe_transactions(balance_transaction):
    rows = []
    for transaction in balance_transaction:
        if transaction.type == "charge" or transaction.type == "refund":
            # DATE (unix -> iso8601)
            timestamp = transaction.created
            dt = datetime.datetime.fromtimestamp(timestamp)
            formatted_date = dt.strftime("%Y-%m-%d")

            # STORE
            if "shop_name" in transaction.source["metadata"]:
                shop_name = transaction.source.metadata["shop_name"]
            else:
                # refunds don't have a metadata property, need to link it
                payment_intent_id = transaction.source["payment_intent"]
                shop_name = get_shop_name(balance_transaction, payment_intent_id)

            # AMOUNT
            # short circuit is a catch-all, usd transactions don't have conversion rate (null)
            net_in_USD = round(
                transaction.net / (float(transaction.exchange_rate or 1) * 100), 2
            )

            # ID
            id = f"strp:{hashlib.sha256(transaction.id.encode()).hexdigest()}"

            row = [id, "strp", formatted_date, shop_name, transaction.type, net_in_USD]
            rows.append(row)
    return rows
