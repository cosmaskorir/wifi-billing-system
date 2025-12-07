from rest_framework import viewsets, permissions
from .models import WifiPackage
from .serializers import WifiPackageSerializer

class WifiPackageViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing WiFi Packages.
    """
    serializer_class = WifiPackageSerializer

    def get_queryset(self):
        """
        Custom logic:
        - Admins see ALL packages (including inactive ones).
        - Regular users/visitors only see ACTIVE packages.
        """
        if self.request.user.is_staff:
            return WifiPackage.objects.all().order_by('price')
        return WifiPackage.objects.filter(is_active=True).order_by('price')

    def get_permissions(self):
        """
        Custom permissions:
        - GET requests (listing plans): Allowed for everyone (AllowAny).
        - POST/PUT/DELETE (managing plans): Only for Admins.
        """
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]