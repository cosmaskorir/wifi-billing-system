from rest_framework import serializers
from .models import Subscription, Payment, DataUsage
from plans.models import WiFiPackage

# --- 1. Subscription Serializer (Used for display in App.js) ---
class SubscriptionSerializer(serializers.ModelSerializer):
    package_name = serializers.CharField(source='package.name', read_only=True)
    price = serializers.DecimalField(source='package.price', max_digits=8, decimal_places=2, read_only=True)
    
    class Meta:
        model = Subscription
        fields = ['id', 'user', 'package', 'package_name', 'price', 'start_date', 'end_date', 'is_active', 'status', 'created_at']
        read_only_fields = ['user', 'package', 'start_date', 'end_date', 'is_active', 'status']

# --- 2. Payment Serializer ---
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

# --- 3. Data Usage Serializer (For display on graph) ---
class DataUsageSerializer(serializers.ModelSerializer):
    # Field to format the date nicely for the frontend graph
    date = serializers.SerializerMethodField()
    
    class Meta:
        model = DataUsage
        fields = ['date', 'download', 'upload']
        
    def get_date(self, obj):
        # Format the date as 'YYYY-MM-DD' for the frontend graph
        return obj.date.strftime('%Y-%m-%d')


# --- 4. NEW: Plan Action Serializer ---
class PlanActionSerializer(serializers.Serializer):
    """
    Used to validate the package ID for upgrade/downgrade/renewal requests.
    """
    package_id = serializers.IntegerField()