from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User model that supports different roles and phone numbers.
    """
    
    # Role Constants
    ADMIN = 'ADMIN'
    CASHIER = 'CASHIER'
    TECHNICIAN = 'TECH'
    CUSTOMER = 'CUSTOMER'

    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (CASHIER, 'Cashier'),
        (TECHNICIAN, 'Technician'),
        (CUSTOMER, 'Customer'),
    )

    # Custom Fields
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=CUSTOMER)
    
    # Phone number is unique to prevent duplicate M-Pesa accounts
    phone_number = models.CharField(
        max_length=15, 
        unique=True, 
        help_text="Format: 2547XXXXXXXX"
    )
    
    location = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.username} - {self.phone_number}"

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'