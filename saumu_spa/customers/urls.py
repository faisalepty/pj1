from django.urls import path
from customers import views

urlpatterns = [
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),
     path('register-prompt/', views.register_prompt, name='register_prompt'),
     path('register/', views.register, name='register'),  # Add this line for the register view
    path('login/', views.user_login, name='login'),  # Login page
    path('logout/', views.user_logout, name='logout'),  # Logout action

]