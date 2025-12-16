from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, SubscriptionViewSet, UsageViewSet # Corrected import

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'usage', UsageViewSet, basename='usage')

urlpatterns = [
    path('', include(router.urls)),
]