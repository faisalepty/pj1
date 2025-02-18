# billing/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('pay/<int:appointment_pk>/', views.make_payment, name='make_payment'),  # Make a payment
    path('confirmation/', views.payment_confirmation, name='payment_confirmation'),  # Payment confirmation
]