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
    image_url = models.URLField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class AdditionalTask(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='additional_tasks')
    name = models.CharField(max_length=100)
    fixed_price = models.DecimalField(max_digits=10, decimal_places=2)  # Fixed price for the task
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} (Linked to {self.service.name})"