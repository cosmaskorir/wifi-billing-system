from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.conf import settings
from .utils import MpesaGateWay
from plans.models import WiFiPackage
from billing.models import Payment, Subscription
from django.utils import timezone
from datetime import timedelta

class InitiatePaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # We fetch the amount from the frontend, but we should verify it against a plan if possible
        phone_number = request.data.get('phone')
        amount = request.data.get('amount')
        
        if not phone_number or not amount:
            return Response({"error": "Phone number and amount required"}, status=status.HTTP_400_BAD_REQUEST)

        gateway = MpesaGateWay()
        
        response = gateway.lipa_na_mpesa_online(
            phone_number=phone_number,
            amount=int(amount),
            account_reference=f"User {request.user.username}",
            transaction_desc="Internet Subscription"
        )

        if response.get('ResponseCode') == '0':
            Payment.objects.create(
                user=request.user,
                amount=amount,
                phone_number=phone_number,
                transaction_id=response.get('CheckoutRequestID'),
                status='Pending',
                payment_method='M-Pesa'
            )
            return Response(response, status=status.HTTP_200_OK)
        else:
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

class MpesaCallbackView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data

        try:
            body = data.get('Body', {}).get('stkCallback', {})
            result_code = body.get('ResultCode')
            checkout_id = body.get('CheckoutRequestID')
            
            payment = Payment.objects.filter(transaction_id=checkout_id).first()
            
            if payment:
                if result_code == 0:
                    payment.status = 'Completed'
                    
                    meta_items = body.get('CallbackMetadata', {}).get('Item', [])
                    for item in meta_items:
                        if item.get('Name') == 'MpesaReceiptNumber':
                            payment.mpesa_receipt_number = item.get('Value')
                    
                    payment.save()

                    # Find the plan matching the payment amount
                    matched_plan = WiFiPackage.objects.filter(price=payment.amount).first()
                    
                    if matched_plan:
                        Subscription.objects.update_or_create(
                            user=payment.user,
                            defaults={
                                'package': matched_plan,
                                'start_date': timezone.now(),
                                'end_date': timezone.now() + timedelta(days=matched_plan.duration_days),
                                'is_active': True
                            }
                        )
                        # TODO: Trigger MikroTik API call here to apply the profile
                    
                else:
                    payment.status = 'Failed'
                    payment.save()

        except Exception as e:
            # Log the error
            pass
        
        return Response({"status": "received"})