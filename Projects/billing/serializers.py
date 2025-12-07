from rest_framework import serializers
from .models import Subscription, Payment
from plans.models import WifiPackage
from users.serializers import UserSerializer  # Optional: if you want full user details

class PaymentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 
            'user', 
            'username', 
            'amount', 
            'phone_number', 
            'mpesa_receipt_number', 
            'status', 
            'created_at'
        ]
        read_only_fields = ['status', 'mpesa_receipt_number', 'checkout_request_id', 'created_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    # Flatten package details so the frontend gets "package_name" and "speed" directly
    package_name = serializers.CharField(source='package.name', read_only=True)
    speed = serializers.IntegerField(source='package.speed_mbps', read_only=True)
    price = serializers.DecimalField(source='package.price', max_digits=10, decimal_places=2, read_only=True)
    
    # Calculate days remaining dynamically
    days_remaining = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = [
            'id', 
            'user', 
            'package',          # The ID (for writing/selecting)
            'package_name',     # Read-only detail
            'speed',            # Read-only detail
            'price',            # Read-only detail
            'start_date', 
            'end_date', 
            'is_active',
            'days_remaining'
        ]
        read_only_fields = ['start_date', 'end_date', 'is_active']

    def get_days_remaining(self, obj):
        from django.utils import timezone
        now = timezone.now()
        if obj.end_date and obj.end_date > now:
            delta = obj.end_date - now
            return delta.days
        return 0