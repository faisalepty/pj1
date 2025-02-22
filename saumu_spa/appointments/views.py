from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Appointment
from services.models import Service
from staff.models import Staff
from customers.models import Customer
from django.http import JsonResponse



def home(request):
    services = Service.objects.all()[:3]
    context = {'featured_services': services}
    return render(request, '3_home.html', {'featured_services': services})
from django.utils.timezone import make_aware
from datetime import datetime

def book_appointment(request):
    if request.method == 'POST':
        print("Request POST Data:", request.POST)  # Debugging: Log the POST data
    
        # Extract form data
        service_id = request.POST.get('service_id')
        date = request.POST.get('date')
        time = request.POST.get('time')

        # Validate required fields
        if not service_id or not date or not time:
            return JsonResponse({'success': False, 'error': 'Please fill out all required fields.'})

        try:
            # Combine date and time into a single datetime object
            appointment_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            appointment_datetime = make_aware(appointment_datetime)  # Make it timezone-aware
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid date or time format.'})

        # Fetch the selected service
        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'The selected service does not exist.'})

        # Handle registered users vs. guests
        if request.user.is_authenticated:
            customer = request.user.customer
        else:
            # Guest: Create a temporary customer record
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')
            print("first_name", first_name, "last_name", first_name, email, phone_number)

            if not first_name or not last_name or not email or not phone_number:
                return JsonResponse({'success': False, 'error': 'Please provide your details to proceed.'})

            customer, created = Customer.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone_number': phone_number,
                    'is_registered': False
                }
            )

        # Create the appointment without assigning staff
        Appointment.objects.create(
            customer=customer,
            service=service,
            appointment_date=appointment_datetime,
            status='pending'  # Default status for new appointments
        )

        # Return JSON response for AJAX
        return JsonResponse({
            'success': True,
            'appointment_date': appointment_datetime.strftime("%Y-%m-%d %H:%M"),
            'service_name': service.name
        })

    # If not a POST request, return an error
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})



# def book_appointment(request):
#     if request.method == 'POST':
#         # Process the form data and create an appointment
#         date = request.POST.get('date')
#         time = request.POST.get('time')
#         service_id = request.POST.get('service')

#         # Fetch the selected service
#         service = Service.objects.get(id=service_id)

#         # Automatically assign staff (for now, assign the first available staff)
#         staff = Staff.objects.filter(role__in=['barber', 'masseuse']).first()

#         # Combine date and time into a single datetime field
#         appointment_datetime = f"{date} {time}"

#         # Handle registered users vs. guests
#         if request.user.is_authenticated:
#             # Registered user: Use their profile
#             customer = request.user.customer
#         else:
#             # Guest: Create a temporary customer record
#             first_name = request.POST.get('first_name')
#             last_name = request.POST.get('last_name')
#             email = request.POST.get('email')
#             phone_number = request.POST.get('phone_number')
#             customer = Customer.objects.create(
#                 first_name=first_name,
#                 last_name=last_name,
#                 email=email,
#                 phone_number=phone_number
#             )

#         # Create the appointment
#         Appointment.objects.create(
#             customer=customer,
#             service=service,
#             staff=staff,
#             appointment_date=appointment_datetime,
#             status='pending'
#         )

#         # Redirect based on user type
#         if request.user.is_authenticated:
#             return redirect('appointment_confirmation')  # Redirect to confirmation page
#         else:
#             return redirect('register_prompt')  # Redirect to registration prompt

#     # Render the booking form
#     services = Service.objects.all()
#     return render(request, 'appointments/booking.html', {'services': services})

def appointment_confirmation(request):
    # For now, we'll just display a generic confirmation message
    return render(request, 'appointments/confirmation.html')


@login_required
def complete_appointment(request, appointment_pk):
    appointment = get_object_or_404(Appointment, pk=appointment_pk)
    if appointment.status != 'completed':
        appointment.status = 'completed'
        appointment.save()

        # Add loyalty points to the customer
        customer = appointment.customer
        customer.add_loyalty_points(10)  # Add 10 points per visit

    return redirect('customer_dashboard')