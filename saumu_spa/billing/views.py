# billing/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Billing
from appointments.models import Appointment
from .forms import BillingForm
from django.core.paginator import Paginator


from django.http import JsonResponse
import json



def mpesa_callback(request):
    if request.method == "POST":
        data = json.loads(request.body)
        print("MPESA CALLBACK DATA:", data)  # Check logs for response

        return JsonResponse({"message": "Callback received"}, status=200)

    return JsonResponse({"error": "Invalid request"}, status=400)


# billing/views.py
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from .models import Billing
from django.views.decorators.csrf import csrf_exempt
import json



def get_billing(request, billing_id):
    # Fetch the billing record by ID or return a 404 response if it doesn't exist
    billing = get_object_or_404(Billing, id=billing_id)
    data = {
        'id': billing.id,
        'appointment': {
            'id': billing.appointment.id if billing.appointment else None,
            'customer': {
                'id': billing.appointment.customer.id if billing.appointment and billing.appointment.customer else None,
                'first_name': billing.appointment.customer.first_name if billing.appointment and billing.appointment.customer else '',
                'last_name': billing.appointment.customer.last_name if billing.appointment and billing.appointment.customer else '',
            } if billing.appointment and billing.appointment.customer else None,
            'staff': {
                'id': billing.appointment.staff.id if billing.appointment and billing.appointment.staff else None,
                'first_name': billing.appointment.staff.first_name if billing.appointment and billing.appointment.staff else '',
                'last_name': billing.appointment.staff.last_name if billing.appointment and billing.appointment.staff else '',
            } if billing.appointment and billing.appointment.staff else None,
            'service': {
                'id': billing.appointment.service.id if billing.appointment and billing.appointment.service else None,
                'name': billing.appointment.service.name if billing.appointment and billing.appointment.service else '',
            } if billing.appointment and billing.appointment.service else None,
        } if billing.appointment else None,
        'payment_method': billing.payment_method,
        'amount': str(billing.amount),
        'discount': str(billing.discount or 0),
        'tax': str(billing.tax or 0),
        'total': str(billing.total),
    }
    return JsonResponse(data)


# billing/views.py
def billing_list(request):
    queryset = Billing.objects.all().order_by('-created_at')


    staff_list = Staff.objects.all()
    services = Service.objects.all()

    # Apply payment method filter
    payment_method_filter = request.GET.get('payment_method', '')  # Default to no filter
    if payment_method_filter:
        queryset = queryset.filter(payment_method=payment_method_filter)

    # Pagination
    page_number = request.GET.get('page', 1)
    entries_per_page = request.GET.get('entries', 10)  # Default to 10 entries per page
    paginator = Paginator(queryset, entries_per_page)

    try:
        page_obj = paginator.page(page_number)
    except (EmptyPage, PageNotAnInteger):
        page_obj = paginator.page(1)

    # Check if the request is an AJAX call
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = {
            'billings': [
                {
                    'id': b.id,
                    'appointment_id': b.appointment.id,
                    'customer_name': f"{b.appointment.customer.first_name} {b.appointment.customer.last_name}"
                                     if b.appointment and b.appointment.customer else "Unknown Customer",
                    'staff_name': f"{b.appointment.staff.first_name} {b.appointment.staff.last_name}"
                                  if b.appointment and b.appointment.staff else "No Staff Assigned",
                    'payment_method': b.payment_method,
                    'amount': str(b.amount or 0),
                    'discount': str(b.discount or 0),
                    'tax': str(b.tax or 0),
                    'total': str(b.total or 0),
                    'status': b.appointment.status,  # Add status field
                    'completion_percentage': b.appointment.completion_percentage,  # Calculate completion percentage
                    'created_at': b.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                }
                for b in page_obj.object_list
            ],
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        }
        return JsonResponse(data)

    # Render the template for non-AJAX requests
    return render(request, 'reports/billing_report.html', {'billings': page_obj, 's': 's', 'staff_list': staff_list, 'services': services,})

from .models import Billing
from appointments.models import Appointment
from customers.models import Customer
from staff.models import Staff
from services.models import Service

@csrf_exempt
def create_update_billing(request):
    if request.method == 'POST':
        try:
            # Extract form data
            billing_id = request.POST.get('id')  # For updates
            customer_name = request.POST.get('walkin_customer_name')
            staff_id = request.POST.get('walkin_staff_name')
            service_id = request.POST.get('walkin_service')
            amount_paid = request.POST.get('walkin_amount_paid')

            # Validate required fields
            if not customer_name or not staff_id or not service_id or not amount_paid:
                return JsonResponse({'success': False, 'error': 'Please fill out all required fields.'})

            # Fetch related objects
            staff = get_object_or_404(Staff, id=staff_id)
            service = get_object_or_404(Service, id=service_id)

            # Create or update customer
            first_name, last_name = customer_name.split(' ', 1) if ' ' in customer_name else (customer_name, '')
            customer, created = Customer.objects.get_or_create(
                first_name=first_name,
                last_name=last_name,
                defaults={'email': f'{customer_name.replace(" ", ".")}@example.com', 'phone_number': 'N/A'}
            )

            if billing_id:
                # Update existing billing record
                billing = get_object_or_404(Billing, id=billing_id)
                appointment = billing.appointment
                appointment.customer = customer
                appointment.staff = staff
                appointment.service = service
                appointment.save()

                billing.amount = amount_paid
                billing.total = amount_paid
                billing.save()
            else:
                # Create new appointment and billing record
                appointment = Appointment.objects.create(
                    customer=customer,
                    service=service,
                    staff=staff,
                    appointment_date=now(),
                    status='completed'
                )

                Billing.objects.create(
                    appointment=appointment,
                    payment_method='cash',  # Default payment method for walk-ins
                    amount=amount_paid,
                    discount=0,
                    tax=0,
                    total=amount_paid
                )

            return JsonResponse({'success': True, 'message': 'Billing record saved successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})




@csrf_exempt
def delete_billing(request):
    if request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            billing_id = data.get('id')
            billing = get_object_or_404(Billing, id=billing_id)
            appointment = billing.appointment  # Get the related Appointment
            billing.delete()                  # Delete the Billing
            appointment.delete()              # Delete the Appointment
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

    
@csrf_exempt
def mark_as_transacted(request):
    if request.method == 'POST':
        try:
            # Parse the request body
            data = json.loads(request.body)
            billing_id = data.get('id')

            # Fetch the billing record
            billing = get_object_or_404(Billing, id=billing_id)

            # Update the status to "transacted"
            appointment = get_object_or_404(Appointment, id=billing.appointment.id)
            appointment.status = 'transacted'
            appointment.save()
            print('success \n \n \n \n', billing.appointment.id)

            return JsonResponse({'success': True})
        except Exception as e:
            print('error \n \n \n \n', e)
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

















# billing/views.py
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils.timezone import now
from appointments.models import Appointment
from customers.models import Customer
from staff.models import Staff
from services.models import Service
from .models import Billing
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta




from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

def get_revenue_and_profit_last_seven_months():
    today = timezone.now().date()  # March 1, 2025
    data = []

    for i in range(6, -1, -1):
        start_of_month = (today.replace(day=1) - relativedelta(months=i))
        if i == 0:
            end_of_month = today + timedelta(days=1) - timedelta(seconds=1)
        else:
            end_of_month = (start_of_month + relativedelta(months=1) - timedelta(days=1))

        # Make dates timezone-aware
        start_of_month = timezone.make_aware(datetime.combine(start_of_month, datetime.min.time()))
        end_of_month = timezone.make_aware(datetime.combine(end_of_month, datetime.max.time()))

        total_revenue = Billing.objects.filter(
            created_at__range=(start_of_month, end_of_month)
        ).filter(appointment__status='transacted').aggregate(total=Sum('total'))['total'] or 0

        total_profit = int(total_revenue) * 0.6

        data.append({
            'month': start_of_month.strftime('%b'),
            'revenue': float(total_revenue),
            'profit': float(total_profit)
        })

    return data

def get_service_performance():
    # Query total revenue grouped by service name via the appointment relationship
    service_performance = Billing.objects.values('appointment__service__name')[:5].annotate(
        total_revenue=Sum('total')
    )

    # Convert the data into a list of dictionaries
    data = [
        {
            'service': item['appointment__service__name'],
            'revenue': float(item['total_revenue'])  # Convert Decimal to float for JavaScript compatibility
        }
        for item in service_performance
    ]

    return data

def dashboard(request):
    # Fetch all appointments with related billing and customer/staff details
    appointments = Appointment.objects.select_related('customer', 'staff', 'billing').filter(
    status__in=['completed', 'transacted']
)
    for appointment in appointments:
        print(appointment.service , appointment.customer, appointment.status,'\n \n \n \n', appointment.completion_percentage)
    # Fetch all staff members and services for the dropdowns
    staff_list = Staff.objects.all()
    services = Service.objects.all()



    today = timezone.now().date()
    start_of_day = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
    end_of_day = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.max.time()))

    todays_revenue = Billing.objects.filter(
        created_at__range=(start_of_day, end_of_day), appointment__status='transacted'
    ).aggregate(total=Sum('total'))['total'] or 0
    total_revenue = Billing.objects.filter(appointment__status='transacted').aggregate(total=Sum('total'))['total'] or 0

    todays_profit = round(int(todays_revenue) * 0.6, 2)
    total_profit = round(int(total_revenue) * 0.6, 2)


      # Count appointments created today
    appointments_today = Appointment.objects.filter(
        created_at__range=(start_of_day, end_of_day)
    ).count()

    # Count all appointments in the database
    total_appointments = Appointment.objects.count()

      # Get revenue data for the last 7 months
    revenue_data = get_revenue_and_profit_last_seven_months()

       # Get service performance data
    service_performance = get_service_performance()
    # Pass the data to the template
    return render(request, 'reports/admin_dashboard.html', {
        'appointments': appointments,
        'staff_list': staff_list,  # Add staff list to the context
        'services': services,
        'todays_revenue': todays_revenue,
        'total_revenue': round(total_revenue, 2),
        'todays_profit': todays_profit,
        'total_profit': total_profit,
        'appointments_today': appointments_today,
        'total_appointments': total_appointments,
        'revenue_data': revenue_data,
        'service_performance': service_performance,
        'd': 'd',

             # Add services list to the context
    })


def sales_list(request):

    staff_list = Staff.objects.all()
    services = Service.objects.all()
    # Default filter: completed and transacted appointments
    status_filter = request.GET.get('status', 'completed,transacted')
    
    # Split the status_filter into a list, ensuring no empty or invalid values
    statuses = [status.strip() for status in status_filter.split(',') if status.strip() and status.strip().lower() != 'none']

    # If no valid statuses are provided, default to ['completed', 'transacted']
    if not statuses:
        statuses = ['completed', 'transacted']

    # Debugging: Print the statuses
    print("statuses:", statuses)

    # Query filtered appointments
    appointments = Appointment.objects.filter(status__in=statuses).select_related('customer', 'staff', 'billing').order_by('-created_at')

    # Debugging: Print the filtered appointments
    print("Filtered Appointments:", appointments)

    # Pagination
    page_number = request.GET.get('page', 1)
    entries_per_page = request.GET.get('entries', 10)  # Default to 10 entries per page
    paginator = Paginator(appointments, entries_per_page)
    page_obj = paginator.get_page(page_number)

    # Debugging: Print the paginated object list
    print("Paginated Appointments:", page_obj.object_list)

    # Check if the request is an AJAX call
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return JSON response for AJAX
        data = {
            'appointments': [
                {
                    'id': appt.id,
                    'customer_name': f"{appt.customer.first_name} {appt.customer.last_name}",
                    'staff_name': f"{appt.staff.first_name} {appt.staff.last_name}",
                    'amount_paid': str(appt.billing.total) if hasattr(appt, 'billing') and appt.billing else "0.00",
                    'completion_percentage': appt.completion_percentage,
                    'status': appt.status,
                }
                for appt in page_obj.object_list
            ],
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        }
        print("JSON Response Data:", data)
        return JsonResponse(data)

    # Render the template for non-AJAX requests
    return render(request, 'reports/sales_report.html', {
        'appointments': page_obj,
        'statuses': ['completed', 'transacted'],
        'staff_list': staff_list,  # Add staff list to the context
        'services': services,
        's': 's',
    })
def add_walkin_appointment(request):
    if request.method == 'POST':
        print("success1")
        # Extract form data
        customer_name = request.POST.get('walkin_customer_name')
        staff_id = request.POST.get('walkin_staff_name')
        service_id = request.POST.get('walkin_service')
        amount_paid = request.POST.get('walkin_amount_paid')

        # Validate required fields
        if not customer_name or not staff_id or not service_id or not amount_paid:
            print("error","amount_paid:", amount_paid, "service_id:", service_id, "customer_name:", customer_name, "staff_id:", staff_id)
            return JsonResponse({'success': False, 'error': 'Please fill out all required fields.'})
            
        # Fetch related objects
        staff = get_object_or_404(Staff, id=staff_id)
        service = get_object_or_404(Service, id=service_id)

        # Create a temporary customer record
        first_name, last_name = customer_name.split(' ', 1) if ' ' in customer_name else (customer_name, '')
        customer, created = Customer.objects.get_or_create(
            first_name=first_name,
            last_name=last_name,
            defaults={'email': f'{customer_name.replace(" ", ".")}@example.com', 'phone_number': 'N/A'}
        )

        # Create the appointment
        appointment = Appointment.objects.create(
            customer=customer,
            service=service,
            staff=staff,
            appointment_date=now(),
            status='completed'
        )

        # Create the billing record
        Billing.objects.create(
            appointment=appointment,
            payment_method='cash',  # Default payment method for walk-ins
            amount=amount_paid,
            discount=0,
            tax=0,
            total=amount_paid
        )
        print("success")
        return JsonResponse({'success': True, 'message': 'Walk-in appointment added successfully.'})
    print("error")
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


def update_appointment(request, appointment_id):
    if request.method == 'POST' or request.method == 'PUT':
        appointment = get_object_or_404(Appointment, id=appointment_id)

        # Extract form data
        customer_name = request.POST.get('walkin_customer_name')
        staff_id = request.POST.get('walkin_staff_name')
        service_id = request.POST.get('walkin_service')
        amount_paid = request.POST.get('walkin_amount_paid')

        # Validate required fields
        if not customer_name or not staff_id or not service_id or not amount_paid:
            return JsonResponse({'success': False, 'error': 'Please fill out all required fields.'})

        # Update appointment details
        first_name, last_name = customer_name.split(' ', 1) if ' ' in customer_name else (customer_name, '')
        customer, created = Customer.objects.get_or_create(
            first_name=first_name,
            last_name=last_name,
            defaults={'email': f'{customer_name.replace(" ", ".")}@example.com', 'phone_number': 'N/A'}
        )
        appointment.customer = customer
        appointment.staff = get_object_or_404(Staff, id=staff_id)
        appointment.service = get_object_or_404(Service, id=service_id)
        appointment.save()

        # Update billing record
        billing = getattr(appointment, 'billing', None)
        if billing:
            billing.amount = amount_paid
            billing.total = amount_paid
            billing.save()
        else:
            Billing.objects.create(
                appointment=appointment,
                payment_method='cash',
                amount=amount_paid,
                discount=0,
                tax=0,
                total=amount_paid
            )

        return JsonResponse({'success': True, 'message': 'Appointment updated successfully.'})

def delete_appointment(request, appointment_id):
    if request.method == 'POST':
        appointment = get_object_or_404(Appointment, id=appointment_id)
        print(appointment)
        appointment.delete()
        return JsonResponse({'success': True, 'message': 'Appointment deleted successfully.'})
# def mark_as_transacted(request, appointment_id):
#     if request.method == 'POST':
#         try:
#             # Fetch the appointment
#             appointment = get_object_or_404(Appointment, id=appointment_id)

#             # Ensure the appointment is in the correct status
#             if appointment.status != 'completed':
#                 return JsonResponse({'success': False, 'error': 'Only completed appointments can be marked as transacted.'})

#             # Update the appointment status
#             appointment.status = 'transacted'
#             appointment.save()

#             return JsonResponse({'success': True, 'message': 'Appointment marked as transacted.'})
#         except Exception as e:
#             # Log the exception for debugging
#             print(f"Error marking appointment as transacted: {e}")
#             return JsonResponse({'success': False, 'error': 'An unexpected error occurred.'})
#     else:
#         return JsonResponse({'success': False, 'error': 'Invalid request method.'})


def get_appointment_details(request, appointment_id):
    """
    Fetch details of an appointment for editing.
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)
    return JsonResponse({
        'id': appointment.id,
        'customer_name': f"{appointment.customer.first_name} {appointment.customer.last_name}",
        'staff_id': appointment.staff.id,
        'service_id': appointment.service.id,
        'amount_paid': appointment.billing.total if hasattr(appointment, 'billing') else 0,
    })

@login_required
def make_payment(request, appointment_pk):
    appointment = get_object_or_404(Appointment, pk=appointment_pk)

    if request.method == 'POST':
        form = BillingForm(request.POST)
        if form.is_valid():
            billing = form.save(commit=False)
            billing.appointment = appointment

            # Handle loyalty points redemption
            redeemed_points = int(request.POST.get('redeemed_points', 0))  # Get redeemed points from form
            if redeemed_points > 0:
                success = appointment.customer.redeem_loyalty_points(redeemed_points)  # Redeem points
                if success:
                    billing.amount -= redeemed_points  # Apply discount to the payment amount

            # Calculate total amount
            billing.total = billing.amount - (billing.discount or 0) + (billing.tax or 0)
            billing.save()
            return redirect('payment_confirmation')  # Redirect to payment confirmation page
    else:
        form = BillingForm()

    return render(request, 'billing/make_payment.html', {
        'form': form,
        'appointment': appointment,
        'customer': appointment.customer  # Pass customer to template for loyalty points display
    })

@login_required
def payment_confirmation(request):
    return render(request, 'billing/payment_confirmation.html')