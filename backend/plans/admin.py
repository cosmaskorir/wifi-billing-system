# backend/plans/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import WiFiPackage
from unfold.admin import ModelAdmin 

@admin.register(WiFiPackage)
class WiFiPackageAdmin(ModelAdmin):
    list_display = (
        'name', 
        'price', 
        'duration_days', 
        'display_speed',  
        'display_data_cap', 
        'mikrotik_profile', 
        'is_active',
    )
    
    list_filter = ('is_active', 'duration_days')
    search_fields = ('name', 'price')
    ordering = ('price',)
    
    fieldsets = (
        ("Plan Details", {
            'fields': ('name', 'price', 'duration_days', 'is_active'),
        }),
        ("Speed and Data", {
            'fields': ('max_download_speed', 'max_upload_speed', 'data_cap_mb'),
        }),
        ("Provisioning Link", {
            'fields': ('mikrotik_profile',), 
            'description': 'Link this package to a MikroTik User Profile for automated provisioning.'
        }),
    )

    def display_speed(self, obj):
        return f"{obj.max_download_speed} / {obj.max_upload_speed} Mbps"
    
    display_speed.short_description = "Speed (Down/Up)"

    def display_data_cap(self, obj):
        if obj.data_cap_mb == 0:
            return format_html('<b>Unlimited</b>')
        else:
            gb_value = obj.data_cap_mb / 1024
            return f"{gb_value:,.0f} GB"

    display_data_cap.short_description = "Data Cap"