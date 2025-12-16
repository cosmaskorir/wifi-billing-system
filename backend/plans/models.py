# backend/plans/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from routers.models import RouterProfile 

class WiFiPackage(models.Model):
    """
    Defines the available internet service packages/plans.
    """
    name = models.CharField(_("Package Name"), max_length=100, unique=True)
    price = models.DecimalField(_("Monthly Price (KES)"), max_digits=8, decimal_places=2)
    duration_days = models.IntegerField(_("Duration in Days"), default=30)
    
    # Speed limits in Mbps (Non-nullable, requires default during migration)
    max_download_speed = models.IntegerField(_("Max Download Speed (Mbps)"))
    max_upload_speed = models.IntegerField(_("Max Upload Speed (Mbps)"))
    
    # Data cap in Megabytes (MB). 0 indicates unlimited. (Non-nullable)
    data_cap_mb = models.BigIntegerField(_("Data Cap (MB)"), default=0) 
    
    # Foreign Key to RouterProfile (Nullable, set to NULL on deletion)
    mikrotik_profile = models.ForeignKey(
        RouterProfile, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name=_("MikroTik User Profile")
    )
    
    is_active = models.BooleanField(_("Is Active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("WiFi Package")
        verbose_name_plural = _("WiFi Packages")
        ordering = ['price']

    def __str__(self):
        return f"{self.name} (KES {self.price})"