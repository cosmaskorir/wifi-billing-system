from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Subscription, Payment
from .serializers import SubscriptionSerializer, PaymentSerializer
from users.models import User
from plans.models import WifiPackage

class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Subscriptions.
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Admins see all subscriptions; Customers see only their own
        if self.request.user.role == 'ADMIN':
            return Subscription.objects.all().order_by('-start_date')
        return Subscription.objects.filter(user=self.request.user).order_by('-start_date')

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def assign_package(self, request):
        """
        Custom Endpoint for Admins to manually assign a package.
        Payload: { "user_id": 1, "package_id": 3 }
        """
        user_id = request.data.get('user_id')
        package_id = request.data.get('package_id')

        try:
            user = User.objects.get(id=user_id)
            package = WifiPackage.objects.get(id=package_id)

            # Create the subscription (save() logic in model will handle end_date)
            sub = Subscription.objects.create(
                user=user,
                package=package,
                is_active=True
            )
            
            return Response(SubscriptionSerializer(sub).data, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        except WifiPackage.DoesNotExist:
            return Response({"error": "Package not found"}, status=404)


class PaymentHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing Payment History.
    """
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Admins see all payments; Customers see only their own
        if self.request.user.role == 'ADMIN':
            return Payment.objects.all().order_by('-created_at')
        return Payment.objects.filter(user=self.request.user).order_by('-created_at')