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
                    'service': b.appointment.service.name,
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
                    'created_at': b.created_at.date(),
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
from appointments.models import Appointment, TaskAssignment
from customers.models import Customer
from staff.models import Staff
from services.models import Service, AdditionalTask



@csrf_exempt
def update_billing(request):
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


# def create_update_billing(request):
#     if request.method == 'POST':
#         try:
#             # Parse request data
#             data = json.loads(request.body)
#             customer_name = data.get('customer_name')
#             services = data.get('services')  # List of services
#             additional_charges = float(data.get('additional_charges', 0))

#             # Validate required fields
#             if not customer_name or not services:
#                 return JsonResponse({'success': False, 'error': 'Please fill out all required fields.'})

#             # Create or update customer
#             first_name, last_name = customer_name.split(' ', 1) if ' ' in customer_name else (customer_name, '')
#             customer, created = Customer.objects.get_or_create(
#                 first_name=first_name,
#                 last_name=last_name,
#                 defaults={'email': f'{customer_name.replace(" ", ".")}@example.com', 'phone_number': 'N/A'}
#             )

#             # Process each service
#             total_amount = 0
#             for service_data in services:
#                 service = get_object_or_404(Service, id=service_data['service_id'])
#                 staff = get_object_or_404(Staff, id=service_data['staff_id'])
#                 amount_paid = float(service_data['amount_paid'])

#                 # Calculate total amount
#                 total_amount += amount_paid

#                 # Create appointment
#                 appointment = Appointment.objects.create(
#                     customer=customer,
#                     service=service,
#                     staff=staff,
#                     appointment_date=now(),
#                     status='completed'
#                 )

#                 # Create billing record
#                 Billing.objects.create(
#                     appointment=appointment,
#                     payment_method='cash',
#                     amount=amount_paid,
#                     discount=float(service_data['discount']),
#                     tax=0,
#                     total=amount_paid
#                 )

#             # Add additional charges
#             total_amount += additional_charges

#             return JsonResponse({'success': True, 'message': 'Billing records saved successfully.'})
#         except Exception as e:
#             return JsonResponse({'success': False, 'error': str(e)})
#     return JsonResponse({'success': False, 'error': 'Invalid request method.'})

# billing/views.py


def get_additional_tasks(request, service_id):
    try:
        service = Service.objects.get(id=service_id)
        tasks = service.additional_tasks.all()
        task_data = [
            {
                'id': task.id,
                'name': task.name,
                'fixed_price': str(task.fixed_price),
            }
            for task in tasks
        ]
        return JsonResponse({'success': True, 'tasks': task_data})
    except Service.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Service not found.'})

from decimal import Decimal

# @csrf_exempt
# def create_update_billing(request):
#     if request.method == 'POST':
#         try:
#             # Parse request data
#             data = json.loads(request.body)
#             customer_name = data.get('customer_name')
#             services = data.get('services')  # List of services
#             additional_charges = Decimal(data.get('additional_charges', '0'))  # Convert to Decimal

#             # Validate required fields
#             if not customer_name or not services:
#                 return JsonResponse({'success': False, 'error': 'Please fill out all required fields.'})

#             # Create or update customer
#             first_name, last_name = customer_name.split(' ', 1) if ' ' in customer_name else (customer_name, '')
#             customer, created = Customer.objects.get_or_create(
#                 first_name=first_name,
#                 last_name=last_name,
#                 defaults={'email': f'{customer_name.replace(" ", ".")}@example.com', 'phone_number': 'N/A'}
#             )

#             # Process each service
#             total_amount = Decimal('0')  # Initialize as Decimal
#             for service_data in services:
#                 service = get_object_or_404(Service, id=service_data['service_id'])
#                 staff = get_object_or_404(Staff, id=service_data['staff_id'])
#                 amount_paid = Decimal(service_data['amount_paid'])  # Convert to Decimal

#                 # Calculate total amount
#                 total_amount += amount_paid

#                 # Create appointment
#                 appointment = Appointment.objects.create(
#                     customer=customer,
#                     service=service,
#                     staff=staff,
#                     appointment_date=now(),
#                     status='completed'
#                 )

#                 # Handle additional tasks
#                 additional_tasks = service.additional_tasks.all()
#                 for task in additional_tasks:
#                     task_staff_id = service_data.get(f'task_{task.id}_staff_id')
#                     if task_staff_id:
#                         task_staff = get_object_or_404(Staff, id=task_staff_id)
#                         # Deduct fixed price for the task from the total amount
#                         task_fixed_price = Decimal(task.fixed_price)  # Convert to Decimal
#                         # amount_paid -= task_fixed_price  # Subtract Decimal from Decimal
#                         # Record additional task assignment
#                         TaskAssignment.objects.create(
#                             appointment=appointment,
#                             staff=task_staff,
#                             additional_task=task
#                         )

#                 # Create billing record
#                 Billing.objects.create(
#                     appointment=appointment,
#                     payment_method='cash',
#                     amount=amount_paid,
#                     discount=Decimal(service_data['discount']),  # Convert to Decimal
#                     tax=Decimal('0'),  # Convert to Decimal
#                     total=amount_paid
#                 )

#             # Add additional charges
#             total_amount += additional_charges

#             return JsonResponse({'success': True, 'message': 'Billing records saved successfully.'})
#         except Exception as e:
#             return JsonResponse({'success': False, 'error': str(e)})
#     return JsonResponse({'success': False, 'error': 'Invalid request method.'})


@csrf_exempt
def create_update_billing(request):
    if request.method == 'POST':
        try:
            # Parse request data
            data = json.loads(request.body)
            billing_id = data.get('id')  # ID for updating
            customer_name = data.get('customer_name')
            services = data.get('services')  # List of services
            additional_charges = Decimal(data.get('additional_charges', '0'))  # Convert to Decimal

            # Validate required fields
            if not services:
                return JsonResponse({'success': False, 'error': 'Please fill out all required fields.'})
            if not customer_name:
                customer = Customer.objects.get(first_name="faisal")
            else:
                # Create or update customer
                first_name, last_name = customer_name.split(' ', 1) if ' ' in customer_name else (customer_name, '')
                customer, created = Customer.objects.get_or_create(
                    first_name=first_name,
                    last_name=last_name,
                    defaults={'email': f'{customer_name.replace(" ", ".")}@example.com', 'phone_number': 'N/A'}
                )

            total_amount = Decimal('0')  # Initialize as Decimal

            if billing_id:  # Update existing billing records
                billing_records = Billing.objects.filter(id=billing_id)
                if not billing_records.exists():
                    return JsonResponse({'success': False, 'error': 'Billing record not found.'})

                # Clear existing appointments and task assignments
                Appointment.objects.filter(billing__id=billing_id).delete()
                TaskAssignment.objects.filter(appointment__billing__id=billing_id).delete()

            for service_data in services:
                service = get_object_or_404(Service, id=service_data['service_id'])
                staff = get_object_or_404(Staff, id=service_data['staff_id'])
                amount_paid = Decimal(service_data['amount_paid'])  # Convert to Decimal

                # Calculate total amount
                total_amount += amount_paid

                # Create appointment
                appointment = Appointment.objects.create(
                    customer=customer,
                    service=service,
                    staff=staff,
                    appointment_date=now(),
                    status='completed'
                )

                # Handle additional tasks
                additional_tasks = service.additional_tasks.all()
                for task in additional_tasks:
                    task_staff_id = service_data.get(f'task_{task.id}_staff_id')
                    if task_staff_id:
                        task_staff = get_object_or_404(Staff, id=task_staff_id)
                        # Deduct fixed price for the task from the total amount
                        task_fixed_price = Decimal(task.fixed_price)  # Convert to Decimal
                        # Record additional task assignment
                        TaskAssignment.objects.create(
                            appointment=appointment,
                            staff=task_staff,
                            additional_task=task
                        )

                # Create or update billing record
                if billing_id:
                    billing = Billing.objects.get(id=billing_id)
                    billing.appointment = appointment
                    billing.payment_method = 'cash'
                    billing.amount = amount_paid
                    billing.discount = Decimal(service_data['discount'])  # Convert to Decimal
                    billing.tax = Decimal('0')  # Convert to Decimal
                    billing.total = amount_paid
                    billing.save()
                else:
                    Billing.objects.create(
                        appointment=appointment,
                        payment_method='cash',
                        amount=amount_paid,
                        discount=Decimal(service_data['discount']),  # Convert to Decimal
                        tax=Decimal('0'),  # Convert to Decimal
                        total=amount_paid
                    )

            # Add additional charges
            total_amount += additional_charges

            return JsonResponse({'success': True, 'message': 'Billing records saved successfully.'})
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


def staff_sales(request, pk=None):
    # # Ensure the user is logged in as a staff member
    # if not request.user.is_authenticated or not hasattr(request.user, 'staff'):
    #     return render(request, 'errors/403.html', status=403)
    if pk:
        staff = Staff.objects.get(pk=pk)
        context = {'staff': staff, 'sts1': 'sts1'}
    else:
        staff = Staff.objects.get(user=request.user)  # Get the logged-in staff member
        context = {'staff': staff, 'sts': 'sts'}

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Handle AJAX request for dynamic updates
        queryset = get_staff_appointments_and_tasks(staff, request.GET)

        # Pagination
        page_number = request.GET.get('page', 1)
        entries_per_page = request.GET.get('entries', 10)
        paginator = Paginator(queryset, entries_per_page)

        try:
            page_obj = paginator.page(page_number)
        except (EmptyPage, PageNotAnInteger):
            page_obj = paginator.page(1)

        # Prepare data for AJAX response
        data = {
            'appointments': [
                {
                    'id': item['appointment'].id,
                    'customer_name': f"{item['appointment'].customer.first_name} {item['appointment'].customer.last_name}",
                    'staff_name': f"{staff.first_name} {staff.last_name}",
                    'payment_method': item['appointment'].billing.payment_method if hasattr(item['appointment'], 'billing') else 'N/A',
                    'amount_paid': str(item['amount_paid']),
                    'date': item['appointment'].created_at.date(),
                    'status': item['appointment'].status,
                    'is_additional_task': item['is_additional_task'],
                    'main_task': item['appointment'].service.name if item['is_additional_task'] else "",
                    'task_name': item['task_name'] if item['is_additional_task'] else item['appointment'].service.name,
                }
                for item in page_obj.object_list
            ],
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        }
        print(data)
        return JsonResponse(data)

    # Render the initial page
    return render(request, 'reports/staff_sales.html', context)


def get_staff_appointments_and_tasks(staff, filters):
    """
    Fetch all appointments and additional tasks for the given staff member.
    """
    # Base query for primary services
    appointments = Appointment.objects.filter(staff=staff).order_by('-appointment_date')

    # Apply filters
    status_filter = filters.get('status', '')
    if status_filter:
        appointments = appointments.filter(status=status_filter)

    # Combine primary services and additional tasks
    results = []
    for appointment in appointments:
        # Add primary service
        amount_paid = calculate_payment(appointment, staff)
        results.append({
            'appointment': appointment,
            'amount_paid': amount_paid,
            'is_additional_task': False,
            'task_name': None,
        })

        # Add additional tasks
        additional_tasks = TaskAssignment.objects.filter(
            
            staff=staff,
            additional_task__isnull=False
        )
        count=0
    for task_assignment in additional_tasks:
        task_amount_paid = task_assignment.additional_task.fixed_price
        print(task_amount_paid, '\n \n \n')
        results.append({
            'appointment': task_assignment.appointment,
            'amount_paid': task_amount_paid,
            'is_additional_task': True,
            'task_name': task_assignment.additional_task.name,
        })
        print(count)

    return results


def calculate_payment(appointment, staff):
    """
    Calculate payment for the staff based on the appointment.
    """
    # Check if billing exists
    billing = getattr(appointment, 'billing', None)
    if not billing:
        return Decimal('0')  # Return 0 if no billing record exists

    # Example logic: 40% of total amount for primary service
    return billing.total * Decimal('0.4')






# def get_staff_dashboard_data(user):
#     """
#     Fetch dashboard metrics for the logged-in staff member.
#     """
#     today = timezone.now().date()
#     start_of_month = today.replace(day=1)
#     start_of_day = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
#     end_of_day = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.max.time()))

#     # Base query for appointments and billing (filtered by staff)
#     if hasattr(user, 'staff'):  # Check if the user is a staff member
#         appointments = Appointment.objects.filter(staff=user.staff)
#     else:
#         return {}  # Return empty data if the user is not a staff member

#     additional_tasks_g = TaskAssignment.objects.filter(
#         staff__user=user,
#         additional_task__isnull=False
#     ).aggregate(total=Sum('additional_task__fixed_price'))['total'] or 0

#     additional_tasks = int(additional_tasks_g if additional_tasks_g is not None else 0)

#     additional_tasks1 = TaskAssignment.objects.filter(
#         staff__user=user,
#         additional_task__isnull=False
#     )
#     print('additional_tasks \n \n \n:', additional_tasks1)

#     additional_monthly_tasks_g = TaskAssignment.objects.filter(
#         staff__user=user,
#         appointment__created_at__range=(start_of_month, end_of_day),
#         additional_task__isnull=False
#     ).aggregate(total=Sum('additional_task__fixed_price'))['total'] or 0
#     additional_monthly_tasks = int(additional_monthly_tasks_g if additional_monthly_tasks_g is not None else 0)


#     # Revenue for the current month
#     current_month_payout_g = Billing.objects.filter(
#         appointment__staff__user=user,
#         created_at__range=(start_of_month, end_of_day),
#     ).aggregate(total=Sum('total'))['total']

#     current_month_payout = (int(current_month_payout_g if current_month_payout_g is not None else 0) * 0.4) + additional_monthly_tasks or 0

#     print('additional_tasks \n \n \n:', current_month_payout)
#     # Total clients for the current month
#     current_month_clients = Billing.objects.filter(
#         appointment__staff__user=user,
#         created_at__range=(start_of_month, end_of_day)
#     ).distinct().count()

#     # Total revenue
#     current_month_revenue_g = Billing.objects.filter(
#         appointment__staff__user=user,
#         created_at__range=(start_of_month, end_of_day),
#     ).aggregate(total=Sum('total'))['total']

#     current_month_revenue = int(current_month_revenue_g if current_month_revenue_g is not None else 0)



#     # Total clients
#     total_clients = Billing.objects.filter(
#         appointment__staff__user=user).distinct().count()

#     # Revenue and profit data for the last 7 months
#     def get_staff_revenue_and_profit_last_seven_months():
#         data = []
#         today = timezone.now().date()

#         for i in range(6, -1, -1):
#             start_of_month = (today.replace(day=1) - relativedelta(months=i))
#             end_of_month = (start_of_month + relativedelta(months=1) - timedelta(days=1))

#             start_of_month = timezone.make_aware(timezone.datetime.combine(start_of_month, timezone.datetime.min.time()))
#             end_of_month = timezone.make_aware(timezone.datetime.combine(end_of_month, timezone.datetime.max.time()))

#             total_revenue = Billing.objects.filter(
#                 appointment__staff__user=user,
#                 created_at__range=(start_of_month, end_of_month),
#             ).aggregate(total=Sum('total'))['total'] or 0


#             current_month_revenue_d = Billing.objects.filter(
#             appointment__staff__user=user,
#             created_at__range=(start_of_month, end_of_month),
#         ).aggregate(total=Sum('total'))['total'] or 0


#             total_d = Billing.objects.filter(
#     appointment__staff__user=user,
#     created_at__range=(start_of_month, end_of_month),
# ).aggregate(total=Sum('total'))['total'] or 0

#             total_tasks_d = TaskAssignment.objects.filter(
#     staff__user=user,
#     appointment__created_at__range=(start_of_month, end_of_month),
#     additional_task__isnull=False
# ).aggregate(total=Sum('additional_task__fixed_price'))['total']

#             additional_monthly_tasks_d = int(total_tasks_d if total_tasks_d is not None else 0)

#             current_month_payout_d = (int(total_d) * 0.4) + additional_monthly_tasks_d or 0


       

#             total_profit = int(total_revenue) * 0.6

#             data.append({
#                 'month': start_of_month.strftime('%b'),
#                 'revenue': float(current_month_revenue_d) ,
#                 'payout': float(current_month_payout_d)
#             })

#         return data

#     # Service performance data (top 5 services by revenue)
#     def get_staff_service_performance():
#         service_performance = Billing.objects.filter(
#             appointment__staff__user=user
#         ).values('appointment__service__name')[:5].annotate(
#             total_revenue=Sum('total')
#         )

#         data = [
#             {
#                 'service': item['appointment__service__name'],
#                 'revenue': float(item['total_revenue'])
#             }
#             for item in service_performance
#         ]

#         return data

#     revenue_data = get_staff_revenue_and_profit_last_seven_months()
#     service_performance = get_staff_service_performance()

#     return {
#         'current_month_revenue': round(current_month_revenue, 2),
#         'current_month_clients': current_month_clients,
#         'current_month_payout': round(current_month_payout, 2),
#         'total_clients': total_clients,
#         'revenue_data': revenue_data,
#         'service_performance': service_performance,
#     }

# Define the helper function for percentage change
def calculate_percentage_change(current, previous):
    if previous == 0 and current == 0:
        return 0
    if previous == 0:
        return 100 if current > 0 else 0
    change = ((current - previous) / previous) * 100
    return round(change, 2)

def get_staff_dashboard_data(user):
    """
    Fetch dashboard metrics for the logged-in staff member.
    """
    today = timezone.now()
    start_of_day = timezone.make_aware(timezone.datetime.combine(today.date(), timezone.datetime.min.time()))
    end_of_day = timezone.make_aware(timezone.datetime.combine(today.date(), timezone.datetime.max.time()))
    start_of_yesterday = timezone.make_aware(timezone.datetime.combine((today - timedelta(days=1)).date(), timezone.datetime.min.time()))
    end_of_yesterday = timezone.make_aware(timezone.datetime.combine((today - timedelta(days=1)).date(), timezone.datetime.max.time()))

    start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month = start_of_month - timedelta(days=1)
    start_of_last_month = last_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_of_last_month = start_of_month - timedelta(seconds=1)

    # Base query for appointments and billing (filtered by staff)
    if hasattr(user, 'staff'):  # Check if the user is a staff member
        appointments = Appointment.objects.filter(staff=user.staff)
    else:
        return {}  # Return empty data if the user is not a staff member

    additional_tasks_g = TaskAssignment.objects.filter(
        staff__user=user,
        additional_task__isnull=False
    ).aggregate(total=Sum('additional_task__fixed_price'))['total'] or 0

    additional_tasks = int(additional_tasks_g if additional_tasks_g is not None else 0)

    additional_tasks1 = TaskAssignment.objects.filter(
        staff__user=user,
        additional_task__isnull=False
    )
    print('additional_tasks \n \n \n:', additional_tasks1)

    additional_monthly_tasks_g = TaskAssignment.objects.filter(
        staff__user=user,
        appointment__created_at__range=(start_of_month, end_of_day),
        additional_task__isnull=False
    ).aggregate(total=Sum('additional_task__fixed_price'))['total'] or 0
    additional_monthly_tasks = int(additional_monthly_tasks_g if additional_monthly_tasks_g is not None else 0)

    # Last month's additional tasks for payout comparison
    additional_last_month_tasks_g = TaskAssignment.objects.filter(
        staff__user=user,
        appointment__created_at__range=(start_of_last_month, end_of_last_month),
        additional_task__isnull=False
    ).aggregate(total=Sum('additional_task__fixed_price'))['total'] or 0
    additional_last_month_tasks = int(additional_last_month_tasks_g if additional_last_month_tasks_g is not None else 0)

    # Revenue for the current month
    current_month_payout_g = Billing.objects.filter(
        appointment__staff__user=user,
        created_at__range=(start_of_month, end_of_day),
    ).aggregate(total=Sum('total'))['total']
    current_month_payout = (int(current_month_payout_g if current_month_payout_g is not None else 0) * 0.4) + additional_monthly_tasks or 0

    # Last month's payout
    last_month_payout_g = Billing.objects.filter(
        appointment__staff__user=user,
        created_at__range=(start_of_last_month, end_of_last_month),
    ).aggregate(total=Sum('total'))['total']
    last_month_payout = (int(last_month_payout_g if last_month_payout_g is not None else 0) * 0.4) + additional_last_month_tasks or 0

    print('additional_tasks \n \n \n:', current_month_payout)

    # Total clients for the current month (using Appointment instead of Billing)
    current_month_clients = Appointment.objects.filter(
        staff=user.staff,
        created_at__range=(start_of_month, end_of_day)
    ).count()

    # Last month's clients
    last_month_clients = Appointment.objects.filter(
        staff=user.staff,
        created_at__range=(start_of_last_month, end_of_last_month)
    ).count()

    # Total revenue for the current month
    current_month_revenue_g = Billing.objects.filter(
        appointment__staff__user=user,
        created_at__range=(start_of_month, end_of_day),
    ).aggregate(total=Sum('total'))['total']
    current_month_revenue = int(current_month_revenue_g if current_month_revenue_g is not None else 0)

    # Last month's revenue
    last_month_revenue_g = Billing.objects.filter(
        appointment__staff__user=user,
        created_at__range=(start_of_last_month, end_of_last_month),
    ).aggregate(total=Sum('total'))['total']
    last_month_revenue = int(last_month_revenue_g if last_month_revenue_g is not None else 0)

    # Total clients (using Appointment instead of Billing)
    total_clients = Appointment.objects.filter(
        staff=user.staff
    ).count()

    # Total clients for yesterday
    total_clients_yesterday = Appointment.objects.filter(
        staff=user.staff,
        created_at__range=(start_of_yesterday, end_of_yesterday)
    ).count()

    # Calculate changes
    current_month_revenue_change = calculate_percentage_change(current_month_revenue, last_month_revenue)
    current_month_clients_change = current_month_clients - last_month_clients
    current_month_clients_change_abs = abs(current_month_clients_change) if current_month_clients_change != 0 else 0
    current_month_payout_change = calculate_percentage_change(current_month_payout, last_month_payout)
    total_clients_change = calculate_percentage_change(total_clients, total_clients_yesterday)

    # Revenue and profit data for the last 7 months
    def get_staff_revenue_and_profit_last_seven_months():
        data = []
        today = timezone.now().date()

        for i in range(6, -1, -1):
            start_of_month = (today.replace(day=1) - relativedelta(months=i))
            end_of_month = (start_of_month + relativedelta(months=1) - timedelta(days=1))

            start_of_month = timezone.make_aware(timezone.datetime.combine(start_of_month, timezone.datetime.min.time()))
            end_of_month = timezone.make_aware(timezone.datetime.combine(end_of_month, timezone.datetime.max.time()))

            total_revenue = Billing.objects.filter(
                appointment__staff__user=user,
                created_at__range=(start_of_month, end_of_month),
            ).aggregate(total=Sum('total'))['total'] or 0

            current_month_revenue_d = Billing.objects.filter(
                appointment__staff__user=user,
                created_at__range=(start_of_month, end_of_month),
            ).aggregate(total=Sum('total'))['total'] or 0

            total_d = Billing.objects.filter(
                appointment__staff__user=user,
                created_at__range=(start_of_month, end_of_month),
            ).aggregate(total=Sum('total'))['total'] or 0

            total_tasks_d = TaskAssignment.objects.filter(
                staff__user=user,
                appointment__created_at__range=(start_of_month, end_of_month),
                additional_task__isnull=False
            ).aggregate(total=Sum('additional_task__fixed_price'))['total']

            additional_monthly_tasks_d = int(total_tasks_d if total_tasks_d is not None else 0)

            current_month_payout_d = (int(total_d) * 0.4) + additional_monthly_tasks_d or 0

            total_profit = int(total_revenue) * 0.6

            data.append({
                'month': start_of_month.strftime('%b'),
                'revenue': float(current_month_revenue_d),
                'payout': float(current_month_payout_d)
            })

        return data

    # Service performance data (top 5 services by revenue)
    def get_staff_service_performance():
        service_performance = Billing.objects.filter(
            appointment__staff__user=user
        ).values('appointment__service__name')[:5].annotate(
            total_revenue=Sum('total')
        )

        data = [
            {
                'service': item['appointment__service__name'],
                'revenue': float(item['total_revenue'])
            }
            for item in service_performance
        ]

        return data

    revenue_data = get_staff_revenue_and_profit_last_seven_months()
    service_performance = get_staff_service_performance()

    return {
        'current_month_revenue': round(current_month_revenue, 2),
        'current_month_clients': current_month_clients,
        'current_month_payout': round(current_month_payout, 2),
        'total_clients': total_clients,
        'revenue_data': revenue_data,
        'service_performance': service_performance,
        'current_month_revenue_change': current_month_revenue_change,
        'current_month_clients_change': current_month_clients_change,
        'current_month_clients_change_abs': current_month_clients_change_abs,
        'current_month_payout_change': current_month_payout_change,
        'total_clients_change': total_clients_change,
    }

# def staff_dashboard(request, pk=None):
#     # Get dashboard data for the logged-in staff member
#     if pk:
#         staff = Staff.objects.get(pk=pk)
#         dashboard_data = get_staff_dashboard_data(staff.user)
#     else:
#         staff = None
#         dashboard_data = get_staff_dashboard_data(request.user)

#     # Pass the data to the template
#     return render(request, 'reports/staff_dashboard.html', {
#         'current_month_revenue': dashboard_data.get('current_month_revenue', 0),
#         'current_month_clients': dashboard_data.get('current_month_clients', 0),
#         'current_month_payout': dashboard_data.get('current_month_payout', 0),
#         'total_clients': dashboard_data.get('total_clients', 0),
#         'revenue_data': dashboard_data.get('revenue_data', []),
#         'service_performance': dashboard_data.get('service_performance', []),
#         'staff': staff,
#         'x': 'x',
#         'd': "d"
#     })




def staff_dashboard(request, pk=None):
    # Get dashboard data for the logged-in staff member
    if pk:
        staff = Staff.objects.get(pk=pk)
        dashboard_data = get_staff_dashboard_data(staff.user)
    else:
        staff = None
        dashboard_data = get_staff_dashboard_data(request.user)

    # Pass the data to the template
    return render(request, 'reports/staff_dashboard.html', {
        'current_month_revenue': dashboard_data.get('current_month_revenue', 0),
        'current_month_clients': dashboard_data.get('current_month_clients', 0),
        'current_month_payout': dashboard_data.get('current_month_payout', 0),
        'total_clients': dashboard_data.get('total_clients', 0),
        'revenue_data': dashboard_data.get('revenue_data', []),
        'service_performance': dashboard_data.get('service_performance', []),
        'staff': staff,
        'x': 'x',
        'd': "d",
        'current_month_revenue_change': dashboard_data.get('current_month_revenue_change', 0),
        'current_month_clients_change': dashboard_data.get('current_month_clients_change', 0),
        'current_month_clients_change_abs': dashboard_data.get('current_month_clients_change_abs', 0),
        'current_month_payout_change': dashboard_data.get('current_month_payout_change', 0),
        'total_clients_change': dashboard_data.get('total_clients_change', 0),
    })

















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
        ).filter(appointment__status__in=['completed', 'transacted']).aggregate(total=Sum('total'))['total'] or 0

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





# Define the helper function for percentage change
def calculate_percentage_change(current, previous):
    if previous == 0 and current == 0:
        return 0
    if previous == 0:
        return 100 if current > 0 else 0
    change = ((current - previous) / previous) * 100
    return round(change, 2)

def dashboard(request):
    # Fetch all appointments with related billing and customer/staff details
    appointments = Appointment.objects.select_related('customer', 'staff', 'billing').filter(
        status__in=['completed', 'transacted']
    )
    for appointment in appointments:
        print(appointment.service, appointment.customer, appointment.status, '\n \n \n', appointment.completion_percentage)

    # Fetch all staff members and services for the dropdowns
    staff_list = Staff.objects.all()
    services = Service.objects.all()

    today = timezone.now()
    start_of_day = timezone.make_aware(timezone.datetime.combine(today.date(), timezone.datetime.min.time()))
    end_of_day = timezone.make_aware(timezone.datetime.combine(today.date(), timezone.datetime.max.time()))
    start_of_yesterday = timezone.make_aware(timezone.datetime.combine((today - timedelta(days=1)).date(), timezone.datetime.min.time()))
    end_of_yesterday = timezone.make_aware(timezone.datetime.combine((today - timedelta(days=1)).date(), timezone.datetime.max.time()))

    start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month = start_of_month - timedelta(days=1)
    start_of_last_month = last_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_of_last_month = start_of_month - timedelta(seconds=1)

    # Today's metrics
    todays_revenue = Billing.objects.filter(
        created_at__range=(start_of_day, end_of_day), appointment__status='transacted'
    ).aggregate(total=Sum('total'))['total'] or 0
    todays_profit = round(Decimal(todays_revenue) * Decimal('0.6'), 2) if todays_revenue else 0
    appointments_today = Appointment.objects.filter(
        created_at__range=(start_of_day, end_of_day)
    ).count()

    # Yesterday's metrics
    yesterdays_revenue = Billing.objects.filter(
        created_at__range=(start_of_yesterday, end_of_yesterday), appointment__status='transacted'
    ).aggregate(total=Sum('total'))['total'] or 0
    yesterdays_profit = round(Decimal(yesterdays_revenue) * Decimal('0.6'), 2) if yesterdays_revenue else 0
    appointments_yesterday = Appointment.objects.filter(
        created_at__range=(start_of_yesterday, end_of_yesterday)
    ).count()

    # Current month metrics
    current_month_revenue_g = Billing.objects.filter(
        created_at__range=(start_of_month, end_of_day),
    ).aggregate(total=Sum('total'))['total']
    current_month_revenue = int(current_month_revenue_g if current_month_revenue_g is not None else 0)
    current_month_profit = round(Decimal(current_month_revenue) * Decimal('0.6'), 2) if current_month_revenue else 0

    # Last month metrics
    last_month_revenue = Billing.objects.filter(
        created_at__range=(start_of_last_month, end_of_last_month),
    ).aggregate(total=Sum('total'))['total'] or 0
    last_month_profit = round(Decimal(last_month_revenue) * Decimal('0.6'), 2) if last_month_revenue else 0

    # Total metrics
    total_revenue = Billing.objects.filter(appointment__status__in=['transacted', 'completed']).aggregate(total=Sum('total'))['total'] or 0
    total_profit = round(Decimal(total_revenue) * Decimal('0.6'), 2) if total_revenue else 0
    total_appointments = Appointment.objects.count()

    # Calculate percentage changes for most metrics
    todays_revenue_change = calculate_percentage_change(todays_revenue, yesterdays_revenue)
    todays_profit_change = calculate_percentage_change(todays_profit, yesterdays_profit)
    total_revenue_change = calculate_percentage_change(total_revenue, yesterdays_revenue)
    current_month_revenue_change = calculate_percentage_change(current_month_revenue, last_month_revenue)
    current_month_profit_change = calculate_percentage_change(current_month_profit, last_month_profit)
    total_appointments_change = calculate_percentage_change(total_appointments, appointments_yesterday)

    # Calculate raw change for clients (appointments_today_change) and its absolute value
    appointments_today_change = appointments_today - appointments_yesterday
    appointments_today_change_abs = abs(appointments_today_change) if appointments_today_change != 0 else 0

    # Get revenue data for the last 7 months
    revenue_data = get_revenue_and_profit_last_seven_months()

    # Get service performance data
    service_performance = get_service_performance()

    # Pass the data to the template
    return render(request, 'reports/admin_dashboard.html', {
        'appointments': appointments,
        'staff_list': staff_list,
        'services': services,
        'current_month_revenue': current_month_revenue,
        'current_month_profit': current_month_profit,
        'todays_revenue': todays_revenue,
        'total_revenue': round(total_revenue, 2),
        'todays_profit': todays_profit,
        'total_profit': total_profit,
        'appointments_today': appointments_today,
        'total_appointments': total_appointments,
        'revenue_data': revenue_data,
        'service_performance': service_performance,
        'd': 'd',
        'todays_revenue_change': todays_revenue_change,
        'todays_profit_change': todays_profit_change,
        'appointments_today_change': appointments_today_change,
        'appointments_today_change_abs': appointments_today_change_abs,
        'total_revenue_change': total_revenue_change,
        'current_month_revenue_change': current_month_revenue_change,
        'current_month_profit_change': current_month_profit_change,
        'total_appointments_change': total_appointments_change,
    })

# def dashboard(request):
#     # Fetch all appointments with related billing and customer/staff details
#     appointments = Appointment.objects.select_related('customer', 'staff', 'billing').filter(
#     status__in=['completed', 'transacted']
# )
#     for appointment in appointments:
#         print(appointment.service , appointment.customer, appointment.status,'\n \n \n \n', appointment.completion_percentage)
#     # Fetch all staff members and services for the dropdowns
#     staff_list = Staff.objects.all()
#     services = Service.objects.all()



#     today = timezone.now().date()
#     start_of_month = today.replace(day=1)
#     start_of_day = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
#     end_of_day = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.max.time()))

#     todays_revenue = Billing.objects.filter(
#         created_at__range=(start_of_day, end_of_day), appointment__status='transacted'
#     ).aggregate(total=Sum('total'))['total'] or 0
#     total_revenue = Billing.objects.filter(appointment__status__in=['transacted', 'completed']).aggregate(total=Sum('total'))['total'] or 0

#     todays_profit = round(int(todays_revenue) * 0.6, 2)
#     total_profit = round(int(total_revenue) * 0.6, 2)
    
#     current_month_revenue_g = Billing.objects.filter(
        
#         created_at__range=(start_of_month, end_of_day),
#     ).aggregate(total=Sum('total'))['total']

#     current_month_revenue = int(current_month_revenue_g if current_month_revenue_g is not None else 0)

#     current_month_profit = current_month_revenue * 0.6
#       # Count appointments created today
#     appointments_today = Appointment.objects.filter(
#         created_at__range=(start_of_day, end_of_day)
#     ).count()

#     # Count all appointments in the database
#     total_appointments = Appointment.objects.count()

#       # Get revenue data for the last 7 months
#     revenue_data = get_revenue_and_profit_last_seven_months()

#        # Get service performance data
#     service_performance = get_service_performance()
#     # Pass the data to the template
#     return render(request, 'reports/admin_dashboard.html', {
#         'appointments': appointments,
#         'staff_list': staff_list,  # Add staff list to the context
#         'services': services,
#         'current_month_revenue': current_month_revenue,
#         'current_month_profit': current_month_profit,
#         'todays_revenue': todays_revenue,
#         'total_revenue': round(total_revenue, 2),
#         'todays_profit': todays_profit,
#         'total_profit': total_profit,
#         'appointments_today': appointments_today,
#         'total_appointments': total_appointments,
#         'revenue_data': revenue_data,
#         'service_performance': service_performance,
#         'd': 'd',

#              # Add services list to the context
#     })


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
                    'date': appt.created_at.date(),
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