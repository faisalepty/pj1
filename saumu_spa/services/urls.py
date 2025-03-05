# services/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.service_list, name='service_list'),
    path('create-update/', views.create_update_service, name='create_update_service'),
    path('delete/', views.delete_service, name='delete_service'),
    path('<int:service_id>/', views.get_service, name='get_service'),

    path('', views.service_list_client, name='services'),  # List of services
    # path('add/', views.add_service, name='add_service'),  # Add a new service
    # path('edit/<int:pk>/', views.edit_service, name='edit_service'),  # Edit a service
    # path('delete/<int:pk>/', views.delete_service, name='delete_service'),  # Delete a service
]