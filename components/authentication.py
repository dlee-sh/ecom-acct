import requests
from oauth2client.service_account import ServiceAccountCredentials
import gspread


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


# authenticate meta
def get_meta_long_token(meta_short_token, client_id, client_secret):
    url = "https://graph.facebook.com/v18.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "fb_exchange_token": meta_short_token,
    }

    response = requests.post(url, params=params)

    # validation
    if response.status_code == 200:
        data = response.json()
        return data["access_token"]
    else:
        print("Error:", response.text)


# authenticate sheets
def authenticate_sheets(gsheet_key):
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
    return client.open_by_key(gsheet_key).sheet1
