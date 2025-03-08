# staff/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # List staff members (HTML or JSON response for AJAX)
    path('list/', views.staff_list, name='staff_list'),

    # Create or update a staff member (AJAX only)
    path('create-update/', views.staff_create_update, name='staff_create_update'),

    # Delete a staff member (AJAX only)
    path('delete/', views.staff_delete, name='staff_delete'),

    # Fetch details of a specific staff member (AJAX only)
    path('<int:pk>/', views.staff_detail, name='staff_detail'),
]