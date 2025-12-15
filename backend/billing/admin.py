from django.contrib import admin
from .models import Subscription, Payment

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
    Safe Admin View for User Subscriptions.
    """
    # We use only 'id' and 'user' initially to ensure the build passes.
    # You can add more fields later once we check your models.py
    list_display = ('id', 'user', 'is_active') 
    list_filter = ('is_active',)
    search_fields = ('user__username',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Safe Admin View for Payment History.
    """
    # We removed 'transaction_id' and 'payment_method' because they caused errors.
    list_display = ('id', 'user', 'amount', 'status')
    list_filter = ('status',)
    search_fields = ('user__username',)