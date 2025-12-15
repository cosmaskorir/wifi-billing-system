from django.contrib import admin
from .models import Subscription, Payment

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
    Admin View for User Subscriptions.
    Simplified to prevent 500 Errors by listing only database fields.
    """
    list_display = (
        'id', 
        'user', 
        'package', 
        'start_date', 
        'end_date', 
        'is_active', 
        'created_at'
    )
    list_filter = ('is_active', 'package', 'created_at')
    search_fields = ('user__username', 'user__email', 'package__name')
    ordering = ('-created_at',)
    
    # Read-only fields prevent accidental edits that might break logic
    readonly_fields = ('created_at',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Admin View for Payment History.
    """
    list_display = (
        'transaction_id', 
        'user', 
        'amount', 
        'status', 
        'payment_method', 
        'created_at'
    )
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('transaction_id', 'user__username', 'phone_number')
    ordering = ('-created_at',)