from django.db import models

# Create your models here.
from django.db import models

class Staff(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('barber', 'Barber'),
        ('masseuse', 'Masseuse'),
    ]
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    availability = models.JSONField(default=dict)  # Store availability as JSON (e.g., {"Monday": "9AM-5PM"})
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.10)  # 10% commission
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"