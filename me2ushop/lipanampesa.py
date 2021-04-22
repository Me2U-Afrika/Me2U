import base64
from datetime import datetime

import requests
from requests.auth import HTTPBasicAuth

import keys


# format generated 2021-04-21 23:39:58.350427

current_time = datetime.now()

# required format 20210421233958
timestamp = current_time.strftime("%Y%m%d%H%M%S")
# print(timestamp)

business_short_code = keys.businessShortCode
pass_key = keys.lipa_na_mpesa_passkey

# Data to be encoded to produce password
data = business_short_code + pass_key + timestamp

encoded = base64.b64encode(data.encode())
decoded = encoded.decode()
# print(decoded)


# Generate access token

consumer_key = keys.consumer_key
consumer_secret = keys.consumer_secret
api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))

# print(r.json())
# {'access_token': 'yEQz2EjLlINzgNxoer5GHUM1AKwh', 'expires_in': '3599'}
json_response = r.json()
my_access_token = json_response['access_token']
print(my_access_token)


def lipa_na_mpesa():
    access_token = my_access_token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": "Bearer %s" % access_token}
    request = {
        "BusinessShortCode": business_short_code,
        "Password": decoded,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": "1",
        "PartyA": keys.phone_number,
        "PartyB": business_short_code,
        "PhoneNumber": keys.phone_number,
        "CallBackURL": "https://me2uafrica-cli.herokuapp.com/api/payments/lnm",
        "AccountReference": "12345678",
        "TransactionDesc": "Me2U Online Payment"
    }

    response = requests.post(api_url, json=request, headers=headers)

    print(response.text)

lipa_na_mpesa()
