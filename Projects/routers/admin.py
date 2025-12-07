from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Router

@admin.register(Router)
class RouterAdmin(ModelAdmin):
    list_display = ('name', 'ip_address', 'api_port', 'username')
    search_fields = ('name', 'ip_address')