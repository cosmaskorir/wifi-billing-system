from django.urls import path
from .views import InitiatePaymentView, MpesaCallbackView

urlpatterns = [
    # POST /api/mpesa/pay/  -> Triggers STK Push
    path('pay/', InitiatePaymentView.as_view(), name='mpesa_pay'),

    # POST /api/mpesa/callback/ -> Receives response from Safaricom
    path('callback/', MpesaCallbackView.as_view(), name='mpesa_callback'),
]