# services/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.service_list, name='services'),  # List of services
    path('add/', views.add_service, name='add_service'),  # Add a new service
    path('edit/<int:pk>/', views.edit_service, name='edit_service'),  # Edit a service
    path('delete/<int:pk>/', views.delete_service, name='delete_service'),  # Delete a service
]