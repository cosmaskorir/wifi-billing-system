from django.contrib import admin
from unfold.admin import ModelAdmin
from django.utils.html import format_html
from .models import Subscription, Payment

@admin.register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    list_display = ('user', 'package', 'start_date', 'end_date', 'active_status')
    search_fields = ('user__username', 'user__phone_number')
    list_filter = ('is_active', 'package')
    
    # We keep end_date read-only because the model calculates it automatically
    readonly_fields = ('end_date',) 

    def active_status(self, obj):
        if obj.is_active:
            return format_html('<span class="bg-green-100 text-green-800 px-2 py-1 rounded">Active</span>')
        return format_html('<span class="bg-red-100 text-red-800 px-2 py-1 rounded">Expired</span>')

@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = ('phone_number', 'amount', 'transaction_id', 'status_badge', 'created_at')
    search_fields = ('phone_number', 'checkout_request_id', 'mpesa_receipt_number')
    list_filter = ('status', 'created_at')

    def transaction_id(self, obj):
        return obj.mpesa_receipt_number or obj.checkout_request_id

    def status_badge(self, obj):
        colors = {
            'COMPLETED': 'green',
            'PENDING': 'orange',
            'FAILED': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            f'<span class="bg-{color}-100 text-{color}-800 px-2 py-1 rounded">{obj.status}</span>'
        )