from django.contrib import admin

# Register your models here.
from .models import Appointment, TaskAssignment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'service', 'staff', 'appointment_date', 'status', 'created_at')
    list_filter = ('status', 'appointment_date', 'staff')  # Filter by status, date, and staff
    search_fields = ('customer__first_name', 'service__name', 'staff__first_name')  # Search by customer, service, or staff

admin.site.register(TaskAssignment)