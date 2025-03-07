# # billing/urls.py
# from django.urls import path
# from . import views

# urlpatterns = [
#     path('pay/<int:appointment_pk>/', views.make_payment, name='make_payment'),  # Make a payment
#     path('confirmation/', views.payment_confirmation, name='payment_confirmation'),  # Payment confirmation
# ]

# billing/urls.py
from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    # Staff Dashboard
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff-dashboard/<int:pk>/', views.staff_dashboard, name='staff_dashboard'),
    path('staff-sales/', views.staff_sales, name='staff_sales'),
    path('staff-sales/<int:pk>/', views.staff_sales, name='staff_sales'),
    


    path('<int:service_id>/additional-tasks/', views.get_additional_tasks, name='get_additional_tasks'),

    path('list/', views.billing_list, name='billing_list'),
    path('update/', views.update_billing, name='update_billing'),
    path('create-update/', views.create_update_billing, name='create_update_billing'),
    path('delete/', views.delete_billing, name='delete_billing'),
    path('<int:billing_id>/', views.get_billing, name='get_billing'), 
     path('mark-as-transacted/', views.mark_as_transacted, name='mark_as_transacted'),  # Add this line

    path('add-walkin/', views.add_walkin_appointment, name='add_walkin_appointment'),
    # path('mark-transacted/<int:appointment_id>/', views.mark_as_transacted, name='mark_as_transacted'),
    path('dashboard/', views.dashboard, name='admin_dashboard'),  # New route for the table

     path('sales-list/', views.sales_list, name='sales_list'),
    path('get-appointment/<int:appointment_id>/', views.get_appointment_details, name='get_appointment_details'),
    path('update-appointment/<int:appointment_id>/', views.update_appointment, name='update_appointment'),
    path('mark-transacted/<int:appointment_id>/', views.mark_as_transacted, name='mark_as_transacted'),
    #path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('delete/<int:appointment_id>/', views.delete_appointment, name='delete_appointment'),
     path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
]