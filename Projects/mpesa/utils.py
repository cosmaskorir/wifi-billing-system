import requests
import base64
from datetime import datetime
from django.conf import settings

class MpesaGate:
    def get_access_token(self):
        consumer_key = settings.MPESA_CONSUMER_KEY
        consumer_secret = settings.MPESA_CONSUMER_SECRET
        api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        
        r = requests.get(api_URL, auth=(consumer_key, consumer_secret))
        return r.json()['access_token']

    def stk_push(self, phone_number, amount, account_ref):
        access_token = self.get_access_token()
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_str = settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp
        password = base64.b64encode(password_str.encode()).decode('utf-8')
        
        headers = { "Authorization": "Bearer %s" % access_token }
        
        payload = {
            "BusinessShortCode": settings.MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount), 
            "PartyA": phone_number, 
            "PartyB": settings.MPESA_SHORTCODE,
            "PhoneNumber": phone_number,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": account_ref, # E.g., UserID
            "TransactionDesc": "Wifi Subscription"
        }
        
        response = requests.post(api_url, json=payload, headers=headers)
        return response.json()