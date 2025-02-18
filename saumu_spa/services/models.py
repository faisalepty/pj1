# services/models.py
from django.db import models

class Service(models.Model):
    CATEGORY_CHOICES = [
        ('haircut', 'Haircut'),
        ('massage', 'Massage'),
        ('spa', 'Spa'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    duration = models.DurationField()  # e.g., timedelta(hours=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name