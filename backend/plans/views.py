# backend/plans/views.py

from rest_framework import viewsets, permissions
from .models import WiFiPackage  # <-- Corrected import to WiFiPackage
from .serializers import WiFiPackageSerializer


class WiFiPackageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows customers to view the available internet packages.
    Endpoint: /api/plans/wifipackages/
    """
    serializer_class = WiFiPackageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only show packages that are marked as active
        return WiFiPackage.objects.filter(is_active=True)