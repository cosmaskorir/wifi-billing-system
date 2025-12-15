import json
import logging
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.core.mail import send_mail  # <--- NEW: For sending receipts

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .utils import MpesaGateWay  # Assumes you have a utility to handle the actual STK Push
from billing.models import Payment, Subscription
from plans.models import WiFiPackage

User = get_user_model()
logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_stk_push(request):
    """
    Endpoint for the Frontend to trigger a payment.
    Expects: { "phone": "2547...", "amount": 1000 }
    """
    phone = request.data.get('phone')
    amount = request.data.get('amount')
    
    if not phone or not amount:
        return Response({'error': 'Phone and Amount are required'}, status=400)

    # Convert amount to integer
    try:
        amount = int(float(amount))
    except ValueError:
        return Response({'error': 'Invalid amount'}, status=400)

    # Initialize M-Pesa Gateway
    gateway = MpesaGateWay()
    
    # Send STK Push
    # We use the User's ID as the AccountReference so we know who paid later
    response = gateway.stk_push(
        phone_number=phone,
        amount=amount,
        account_reference=str(request.user.id), 
        transaction_desc="WiFi Subscription Payment"
    )

    return Response(response)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def process_stk_callback(request):
    """
    Callback URL called by Safaricom when payment is complete.
    This runs in the background.
    """
    data = request.data
    logger.info(f"M-Pesa Callback Data: {json.dumps(data)}")

    try:
        # 1. Extract Data from Safaricom JSON
        body = data.get('Body', {}).get('stkCallback', {})
        result_code = body.get('ResultCode')
        result_desc = body.get('ResultDesc')
        merchant_request_id = body.get('MerchantRequestID')
        checkout_request_id = body.get('CheckoutRequestID')

        # 2. Check if Payment was Successful (ResultCode 0)
        if result_code == 0:
            metadata = body.get('CallbackMetadata', {}).get('Item', [])
            
            # Helper to find items in the list
            def get_item(name):
                for item in metadata:
                    if item.get('Name') == name:
                        return item.get('Value')
                return None

            amount = get_item('Amount')
            mpesa_receipt_number = get_item('MpesaReceiptNumber')
            phone_number = str(get_item('PhoneNumber'))
            transaction_date = get_item('TransactionDate')

            # 3. Find the User
            # We assume the user exists based on phone or AccountReference logic.
            # Here we try to match by Phone Number if AccountReference isn't available in callback
            try:
                user = User.objects.get(phone_number=phone_number)
            except User.DoesNotExist:
                logger.warning(f"Payment received from unknown number: {phone_number}")
                user = None

            # 4. Save Payment Record
            payment = Payment.objects.create(
                user=user,
                amount=amount,
                transaction_id=mpesa_receipt_number,
                phone_number=phone_number,
                payment_method='M-Pesa',
                status='Completed'
            )

            # 5. Activate Subscription (Logic: Find package matching amount)
            package = None
            if user:
                # Find a package that costs this amount
                package = WiFiPackage.objects.filter(price=amount).first()
                
                if package:
                    # Calculate end date (e.g., 30 days from now)
                    end_date = timezone.now() + timedelta(days=package.duration_days)
                    
                    # Create or Update Subscription
                    Subscription.objects.update_or_create(
                        user=user,
                        defaults={
                            'package': package,
                            'start_date': timezone.now(),
                            'end_date': end_date,
                            'is_active': True
                        }
                    )

                    # --- 6. SEND EMAIL RECEIPT ---
                    try:
                        if user.email:
                            subject = f"Payment Received - {mpesa_receipt_number}"
                            message = f"""
                            Dear {user.username},

                            We have received your payment of KES {amount}.

                            --------------------------------
                            Receipt No: {mpesa_receipt_number}
                            Plan: {package.name}
                            Speed: {package.speed} Mbps
                            Valid Until: {end_date.strftime('%Y-%m-%d %H:%M')}
                            --------------------------------

                            Your internet connection is now active.
                            Thank you for choosing us!

                            Regards,
                            ISP Billing Team
                            """
                            
                            send_mail(
                                subject,
                                message,
                                settings.DEFAULT_FROM_EMAIL,
                                [user.email],
                                fail_silently=True
                            )
                            logger.info(f"Receipt sent to {user.email}")
                    except Exception as email_err:
                        logger.error(f"Failed to send receipt email: {email_err}")

            return Response({"ResultCode": 0, "ResultDesc": "Accepted"})

        else:
            # Payment Failed / Cancelled by user
            logger.info(f"Payment Failed: {result_desc}")
            return Response({"ResultCode": 0, "ResultDesc": "Failed acknowledged"})

    except Exception as e:
        logger.error(f"Error processing callback: {e}")
        return Response({"ResultCode": 1, "ResultDesc": "Error processing"}, status=500)