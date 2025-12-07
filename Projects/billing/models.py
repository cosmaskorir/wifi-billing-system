from django.db import models
from django.conf import settings
from plans.models import WifiPackage
from django.utils import timezone
from datetime import timedelta

class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    package = models.ForeignKey(WifiPackage, on_delete=models.SET_NULL, null=True)
    
    # We use timezone.now so we can edit the start date if needed
    start_date = models.DateTimeField(default=timezone.now)
    
    # Allowed to be blank because we auto-calculate it
    end_date = models.DateTimeField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Logic: If end_date is empty, calculate it based on the package cycle
        if not self.end_date and self.package:
            if self.package.billing_cycle == 'DAILY':
                self.end_date = self.start_date + timedelta(days=1)
            elif self.package.billing_cycle == 'WEEKLY':
                self.end_date = self.start_date + timedelta(weeks=1)
            elif self.package.billing_cycle == 'MONTHLY':
                self.end_date = self.start_date + timedelta(days=30)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.package}"

class Payment(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed')
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # M-Pesa specific fields
    checkout_request_id = models.CharField(max_length=100, unique=True) 
    mpesa_receipt_number = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=15)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone_number} - {self.amount}"