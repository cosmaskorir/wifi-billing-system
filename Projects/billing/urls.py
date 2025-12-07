from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubscriptionViewSet, PaymentHistoryViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()

# Endpoint: /api/billing/subscriptions/
# Allows users to view their current and past package subscriptions
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')

# Endpoint: /api/billing/payments/
# Allows users to view their transaction history (M-Pesa receipts)
router.register(r'payments', PaymentHistoryViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
]