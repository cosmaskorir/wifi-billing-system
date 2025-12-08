from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Subscription, Payment
from .serializers import SubscriptionSerializer, PaymentSerializer
from users.models import User
from plans.models import WifiPackage

# Router Integration
from routers.models import Router
from routers.utils import RouterManager

class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'ADMIN':
            return Subscription.objects.all().order_by('-start_date')
        return Subscription.objects.filter(user=self.request.user).order_by('-start_date')

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def assign_package(self, request):
        """
        Manually assign package & Activate Internet on Router
        Payload: { "user_id": 1, "package_id": 2 }
        """
        user_id = request.data.get('user_id')
        package_id = request.data.get('package_id')

        try:
            user = User.objects.get(id=user_id)
            package = WifiPackage.objects.get(id=package_id)

            # 1. DB: Create Subscription (Auto-calculates End Date)
            sub = Subscription.objects.create(
                user=user,
                package=package,
                is_active=True
            )

            # 2. HARDWARE: Connect to MikroTik
            # (In production, you might select specific routers based on user location)
            router_db = Router.objects.first()
            if router_db:
                try:
                    manager = RouterManager(router_db)
                    manager.add_user(
                        username=user.phone_number, 
                        password="1234", # Or generate random
                        profile_speed=package.speed_mbps
                    )
                except Exception as e:
                    print(f"Router Connection Failed: {e}")

            return Response(SubscriptionSerializer(sub).data, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        except WifiPackage.DoesNotExist:
            return Response({"error": "Package not found"}, status=404)

class PaymentHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'ADMIN':
            return Payment.objects.all().order_by('-created_at')
        return Payment.objects.filter(user=self.request.user).order_by('-created_at')