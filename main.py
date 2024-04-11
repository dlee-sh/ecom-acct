from credentials import config
from components.authentication import (
    authenticate_paypal,
    get_meta_long_token,
    authenticate_sheets,
)
from get_transactions import get_transactions, format_shop_name

# authenticate stripe
stripe_key = config.STRIPE_API_KEY

# authenticate paypal
paypal_access_token = authenticate_paypal(
    config.PAYPAL_CLIENT_ID, config.PAYPAL_CLIENT_SECRET
)

# authenticate meta
meta_access_token = get_meta_long_token(
    config.META_SHORT_TOKEN, config.META_CLIENT_ID, config.META_CLIENT_SECRET
)

# authenticate sheets
sheet = authenticate_sheets(config.GOOGLE_SHEETS_KEY)

# get transactions
transactions = get_transactions(stripe_key, paypal_access_token, meta_access_token)
transactions_formatted = format_shop_name(transactions)

# write to sheet
all_rows = sheet.get_all_values()
recorded_transactions = [row[0] for row in all_rows]
for row in transactions:
    # check for duplicates
    if row[0] not in recorded_transactions:
        sheet.append_row(row)
        recorded_transactions.append(row[0])
