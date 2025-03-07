from django.contrib import admin

# Register your models here.
from .models import Billing

@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'payment_method', 'amount', 'discount', 'tax', 'total', 'created_at')
    list_filter = ('payment_method', 'created_at', 'appointment__staff')  # Filter by payment method and creation date
    search_fields = ('appointment__customer__first_name', 'appointment__service__name')  # Search by customer or service