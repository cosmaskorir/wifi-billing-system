# backend/routers/admin.py

from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Router, RouterProfile # Ensure both models are imported

# --- Router Admin Configuration ---
@admin.register(Router)
class RouterAdmin(ModelAdmin):
    # FIX: Removed the non-existent 'username' field and replaced it with 'ip_address' and 'vendor'.
    list_display = (
        'name',
        'ip_address', # Replaced 'username' with 'ip_address'
        'vendor',     # Added another descriptive field
        'is_active',
    )
    list_filter = ('is_active', 'vendor')
    search_fields = ('name', 'ip_address')
    ordering = ('name',)

# --- RouterProfile Admin Configuration ---
@admin.register(RouterProfile)
class RouterProfileAdmin(ModelAdmin):
    list_display = (
        'name',
        'is_active',
        'created_at',
    )
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('name',)