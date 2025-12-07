from rest_framework import serializers
from .models import WifiPackage

class WifiPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WifiPackage
        fields = [
            'id', 
            'name', 
            'speed_mbps', 
            'price', 
            'billing_cycle', 
            'description',  # Assuming you added this field, if not remove it
            'is_active'
        ]