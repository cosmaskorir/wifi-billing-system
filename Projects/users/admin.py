from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin  # Import Unfold's Admin class
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    # Modern layout config
    list_display = ('username', 'role_badge', 'phone_number', 'location', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'phone_number')
    list_filter = ('role', 'is_active')
    
    # Organize the "Add User" form into tabs
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    def role_badge(self, obj):
        # Adds a colored badge based on role
        colors = {
            'ADMIN': 'red-600',
            'CASHIER': 'yellow-600',
            'TECH': 'purple-600',
            'CUSTOMER': 'green-600',
        }
        color = colors.get(obj.role, 'gray-600')
        return f'<span class="bg-{color} text-white px-2 py-1 rounded text-xs">{obj.get_role_display()}</span>'
    
    role_badge.allow_tags = True
    role_badge.short_description = "Role"