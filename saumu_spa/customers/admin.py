from django.contrib import admin

# Register your models here.
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'loyalty_points', 'created_at')
    search_fields = ('first_name', 'last_name', 'email')  # Enable searching by name or email
    list_filter = ('created_at',)  # Filter by creation date