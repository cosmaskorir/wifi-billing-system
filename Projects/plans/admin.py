from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import WifiPackage

@admin.register(WifiPackage)
class WifiPackageAdmin(ModelAdmin):
    # FIXED: Added 'is_active' to this list so it can be edited
    list_display = ('name', 'speed_mbps', 'price_display', 'billing_cycle', 'is_active')
    
    list_filter = ('billing_cycle', 'is_active')
    search_fields = ('name',)
    
    # This creates the toggle switch in the list view
    list_editable = ('is_active',)

    def price_display(self, obj):
        return f"KES {obj.price}"
    price_display.short_description = "Price"