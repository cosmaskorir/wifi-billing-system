# backend/routers/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _

class RouterProfile(models.Model):
    """
    Model representing a user profile/rate limit defined on a router (e.g., MikroTik).
    Used as a Foreign Key in the WiFiPackage model.
    """
    name = models.CharField(_("Profile Name"), max_length=100, unique=True)
    
    # Optional fields for Mikrotik rate limits can go here
    # e.g., speed_limit = models.CharField(max_length=50, default="10M/5M") 

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Router Profile")
        verbose_name_plural = _("Router Profiles")
        ordering = ['name'] # Fixes admin.E033 in RouterProfileAdmin

    def __str__(self):
        return self.name

class Router(models.Model):
    """
    Model representing a physical networking device.
    """
    name = models.CharField(_("Name/Location"), max_length=100)
    ip_address = models.GenericIPAddressField(_("IP Address"), unique=True)
    vendor = models.CharField(_("Vendor"), max_length=50, default="MikroTik")
    api_port = models.IntegerField(_("API Port"), default=8728)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Router")
        verbose_name_plural = _("Routers")
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.ip_address})"