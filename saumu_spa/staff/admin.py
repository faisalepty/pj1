from django.contrib import admin

# Register your models here.
from .models import Staff

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'role', 'commission_rate', 'availability', 'created_at')
    list_filter = ('role',)  # Filter by staff role
    search_fields = ('first_name', 'last_name', 'role')  # Search by name or role