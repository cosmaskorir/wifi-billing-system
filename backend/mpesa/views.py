from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import MpesaGate
from billing.models import Payment, Subscription
from users.models import User
from django.utils import timezone
from datetime import timedelta

class InitiatePaymentView(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        amount = request.data.get('amount')
        user_id = request.user.id # or explicit ID if admin is paying
        
        cl = MpesaGate()
        response = cl.stk_push(phone, amount, account_ref=f"USER_{user_id}")
        
        if response.get('ResponseCode') == '0':
            # Save pending payment
            Payment.objects.create(
                user_id=user_id,
                amount=amount,
                phone_number=phone,
                checkout_request_id=response['CheckoutRequestID']
            )
            return Response(response, status=status.HTTP_200_OK)
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

class MpesaCallbackView(APIView):
    permission_classes = [] # Allow Safaricom to hit this without token
    
    def post(self, request):
        data = request.data
        body = data.get('Body', {}).get('stkCallback', {})
        
        checkout_id = body.get('CheckoutRequestID')
        result_code = body.get('ResultCode')
        
        try:
            payment = Payment.objects.get(checkout_request_id=checkout_id)
            
            if result_code == 0:
                payment.status = 'COMPLETED'
                
                # Extract receipt number
                meta = body.get('CallbackMetadata', {}).get('Item', [])
                for item in meta:
                    if item['Name'] == 'MpesaReceiptNumber':
                        payment.mpesa_receipt_number = item['Value']
                payment.save()
                
                # ACTIVATE SUBSCRIPTION LOGIC HERE
                # 1. Find the plan based on amount or user selection
                # 2. Create Subscription object
                
            else:
                payment.status = 'FAILED'
                payment.save()
                
        except Payment.DoesNotExist:
            pass # Handle error logging
            
        return Response({"status": "received"})