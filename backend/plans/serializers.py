# backend/plans/serializers.py

from rest_framework import serializers
from .models import WiFiPackage

class WiFiPackageSerializer(serializers.ModelSerializer):
    """
    Serializer for exposing WiFi package details to the customer portal.
    """
    class Meta:
        model = WiFiPackage
        fields = [
            'id', 
            'name', 
            'price', 
            'duration_days', 
            'max_download_speed', 
            'max_upload_speed', 
            'data_cap_mb'
        ]