from django.db import models

class WifiPackage(models.Model):
    CYCLE_CHOICES = (
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
    )
    name = models.CharField(max_length=50)
    speed_mbps = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    billing_cycle = models.CharField(max_length=10, choices=CYCLE_CHOICES)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.price}"