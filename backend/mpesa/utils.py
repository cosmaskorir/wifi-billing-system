import requests
import base64
from datetime import datetime
from django.conf import settings

class MpesaGateWay:
    def __init__(self):
        # Load credentials from settings.py
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.shortcode = settings.MPESA_SHORTCODE
        self.passkey = settings.MPESA_PASSKEY
        self.callback_url = settings.MPESA_CALLBACK_URL
        
        # Switch between Sandbox (Test) and Production URLs
        if settings.DEBUG:
            self.base_url = "https://sandbox.safaricom.co.ke"
        else:
            self.base_url = "https://api.safaricom.co.ke"

    def get_access_token(self):
        """ Authenticate with Safaricom to get a security token. """
        try:
            url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
            response = requests.get(url, auth=(self.consumer_key, self.consumer_secret))
            response.raise_for_status()
            result = response.json()
            return result.get('access_token')
        except Exception as e:
            print(f"M-Pesa Token Error: {e}")
            return None

    def get_password(self, timestamp):
        """ Generate the password required for STK Push. """
        data_to_encode = f"{self.shortcode}{self.passkey}{timestamp}"
        return base64.b64encode(data_to_encode.encode()).decode('utf-8')

    def lipa_na_mpesa_online(self, phone_number, amount, account_reference="WiFi Subscription", transaction_desc="Payment"):
        """ Trigger the STK Push on the user's phone. """
        access_token = self.get_access_token()
        if not access_token:
            return {"ResponseCode": "1", "ResponseDescription": "Internal Error: Token Failed"}

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = self.get_password(timestamp)
        
        # Ensure phone number is in format 2547XXXXXXXX
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        elif phone_number.startswith('+254'):
            phone_number = phone_number[1:]

        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone_number,
            "PartyB": self.shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": self.callback_url,
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        try:
            url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
            response = requests.post(url, json=payload, headers=headers)
            return response.json()
        except Exception as e:
            print(f"STK Push Error: {e}")
            return {"ResponseCode": "1", "ResponseDescription": f"STK Push Failed: {str(e)}"}