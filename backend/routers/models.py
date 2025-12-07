from django.db import models

class Router(models.Model):
    name = models.CharField(max_length=50, help_text="e.g. Main Tower")
    ip_address = models.GenericIPAddressField(help_text="e.g. 192.168.88.1")
    username = models.CharField(max_length=50, default="admin")
    password = models.CharField(max_length=50)
    api_port = models.IntegerField(default=8728, help_text="Default MikroTik API port")
    
    def __str__(self):
        return f"{self.name} - {self.ip_address}"