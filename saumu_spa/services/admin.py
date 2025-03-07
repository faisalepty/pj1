from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Service, AdditionalTask

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'duration', 'description')
    list_filter = ('category',)  # Filter by service category
    search_fields = ('name', 'category')  # Search by service name or category

admin.site.register(AdditionalTask)