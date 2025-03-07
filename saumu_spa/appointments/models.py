from django.db import models

# Create your models here.
from customers.models import Customer
from services.models import Service,  AdditionalTask
from staff.models import Staff

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('transacted', 'Transacted'),
        ('cancelled', 'Cancelled'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)  # Allow guest bookings
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)
    appointment_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)  # Optional notes for the appointment
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def completion_percentage(self):
        # Define logic for completion percentage based on status
        if self.status == 'pending':
            return 25
        elif self.status == 'confirmed':
            return 50
        elif self.status == 'completed':
            return 75
        elif self.status == 'transacted':
            return 100
        else:
            return 0

    def __str__(self):
        return f"{self.customer} - {self.service} ({self.status})"



class TaskAssignment(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='task_assignments')
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)  # For primary service
    additional_task = models.ForeignKey(AdditionalTask, on_delete=models.CASCADE, null=True, blank=True)  # For additional tasks

    def __str__(self):
        if self.additional_task:
            return f"{self.staff} - {self.additional_task.name}"
        return f"{self.staff} - {self.service.name}"