from oauth2client.service_account import ServiceAccountCredentials
from credentials import config
from get_transactions import get_transactions
import gspread

# get transactions
stripe_key = config.STRIPE_API_KEY
paypal_client_id = config.PAYPAL_CLIENT_ID
paypal_client_secret = config.PAYPAL_CLIENT_SECRET
meta_access_token = config.META_ACCESS_TOKEN

transactions = get_transactions(
    stripe_key, paypal_client_id, paypal_client_secret, meta_access_token
)

# set up sheets api
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "/Users/dlee/code/ecom-accounting/credentials/gkey.json", scope
)
client = gspread.authorize(creds)
sheet = client.open_by_key("1YRkWo1aHDslSiii3bfgHwuR7z0ejrBBkXNCw9cRpseU").sheet1

# write to sheet
# initialize recorded transactions
all_rows = sheet.get_all_values()
recorded_transactions = [row[0] for row in all_rows]
for row in transactions:
    # check for duplicates
    if row[0] not in recorded_transactions:
        sheet.append_row(row)
        recorded_transactions.append(row[0])
