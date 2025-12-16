from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import Subscription, Payment, DataUsage
from .serializers import SubscriptionSerializer, PaymentSerializer, DataUsageSerializer, PlanActionSerializer
from plans.models import WiFiPackage


# --- 1. Subscription ViewSet (Read Only) ---

class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Allows authenticated users to view their active and past subscriptions.
    Endpoint: /api/billing/subscriptions/
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own subscriptions
        return Subscription.objects.filter(user=self.request.user).order_by('-start_date')


# --- 2. Payment ViewSet (Read Only) ---

class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Allows authenticated users to view their payment history.
    Endpoint: /api/billing/payments/
    """
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).order_by('-created_at')


# --- 3. Data Usage ViewSet (Fixes the 404 error) ---

class DataUsageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Provides endpoints for retrieving user data usage history and live status.
    Base Endpoint: /api/billing/usage/ (or usages if registered as such)
    """
    serializer_class = DataUsageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filters historical data for the current user, ordered by date
        # Note: If list() is called, it returns this queryset (the history)
        return DataUsage.objects.filter(user=self.request.user).order_by('date')
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """ 
        Custom action to return the live (or last recorded) data usage.
        Endpoint: /api/billing/usage/current/ 
        """
        # Fetch the latest usage entry for the current user
        latest_usage = DataUsage.objects.filter(user=request.user).order_by('-date').first()
        
        if latest_usage:
            serializer = self.get_serializer(latest_usage)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Return sensible defaults if no usage data exists (e.g., for a new user)
        return Response({
            "date": timezone.now().strftime('%Y-%m-%d'),
            "download": 0,
            "upload": 0
        }, status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['get'])
    def history(self, request):
        """ 
        Custom action to return the historical data (same as the default list() method).
        Endpoint: /api/billing/usage/history/
        """
        return self.list(request) # Use the built-in list logic


# --- 4. Plan Action ViewSet (Upgrade/Downgrade/Renew) ---

class PlanActionViewSet(viewsets.ViewSet):
    """
    Provides endpoints for users to manage (upgrade, downgrade, renew) their subscriptions.
    Base Endpoint: /api/billing/plan-actions/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def change_plan(self, request):
        """ Handles both upgrade and downgrade requests. """
        # PlanActionSerializer is required to validate the package_id
        serializer = PlanActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        package_id = serializer.validated_data['package_id']
        user = request.user
        
        try:
            new_package = WiFiPackage.objects.get(pk=package_id)
        except WiFiPackage.DoesNotExist:
            return Response({"detail": "Invalid package ID."}, status=status.HTTP_404_NOT_FOUND)

        current_subscription = Subscription.objects.filter(user=user, is_active=True).first()

        if not current_subscription:
            return Response({"detail": "No active subscription found. Please pay first."}, status=status.HTTP_400_BAD_REQUEST)
            
        if current_subscription.package == new_package:
             return Response({"detail": "You are already subscribed to this plan."}, status=status.HTTP_400_BAD_REQUEST)

        
        # --- PROVISIONING & TRANSACTION LOGIC (SIMULATED) ---
        # In a real app, you would process a payment for the price difference here.
        
        # 1. Deactivate old subscription
        current_subscription.is_active = False
        current_subscription.status = 'INACTIVE'
        current_subscription.end_date = timezone.now()
        current_subscription.save()

        # 2. Create new subscription (starting now, ending based on package duration)
        new_end_date = timezone.now() + timedelta(days=new_package.duration_days)

        Subscription.objects.create(
            user=user,
            package=new_package,
            start_date=timezone.now(),
            end_date=new_end_date,
            is_active=True,
            status='ACTIVE'
        )

        return Response({
            "detail": f"Plan successfully changed to {new_package.name}.",
            "new_end_date": new_end_date.strftime('%Y-%m-%d %H:%M:%S')
        }, status=status.HTTP_200_OK)


    @action(detail=False, methods=['post'])
    def renew(self, request):
        """ Handles subscription renewal. """
        user = request.user
        current_subscription = Subscription.objects.filter(user=user, is_active=True).first()

        if not current_subscription:
            return Response({"detail": "No active subscription to renew. Please purchase a plan first."}, status=status.HTTP_400_BAD_REQUEST)
        
        package = current_subscription.package
        
        # --- PROVISIONING & TRANSACTION LOGIC (SIMULATED) ---
        # In a real app, a renewal payment (KES X) would be charged here.
        
        # Calculate new end date (starts from current end date)
        old_end_date = current_subscription.end_date
        new_start_date = old_end_date if old_end_date > timezone.now() else timezone.now()
        new_end_date = new_start_date + timedelta(days=package.duration_days)

        # Update the existing subscription's dates and status
        current_subscription.start_date = current_subscription.start_date
        current_subscription.end_date = new_end_date
        current_subscription.is_active = True
        current_subscription.status = 'ACTIVE'
        current_subscription.save()

        return Response({
            "detail": f"Subscription renewed successfully. New expiry date is {new_end_date.strftime('%Y-%m-%d %H:%M:%S')}.",
            "new_end_date": new_end_date.strftime('%Y-%m-%d %H:%M:%S')
        }, status=status.HTTP_200_OK)