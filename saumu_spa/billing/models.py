# billing/models.py
from django.db import models
from appointments.models import Appointment

class Billing(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('mpesa', 'MPesa'),
        ('cash', 'Cash'),
    ]

    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='billing')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tax = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)  # Track when the payment was made

    def __str__(self):
        return f"Billing for {self.appointment.customer} - {self.payment_method}"