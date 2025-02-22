from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Customer
from appointments.models import Appointment
from billing.models import Billing
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

# def register(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()  # Save the new user
#             login(request, user)  # Log the user in
#             return redirect('home')  # Redirect to the home page
#     else:
#         form = UserCreationForm()

#     return render(request, 'customers/register.html', {'form': form})

# def user_login(request):
#     if request.method == 'POST':
#         form = AuthenticationForm(request, data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)  # Log the user in
#             return redirect('home')  # Redirect to the home page
#     else:
#         form = AuthenticationForm()

#     return render(request, 'customers/login.html', {'form': form})

# customers/views.py
from django.contrib.auth import authenticate, login as auth_login
from django.http import JsonResponse

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)  # Log the user in
            return JsonResponse({'success': True, 'message': 'Login successful!'})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid credentials. Please try again.'})

# customers/views.py
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import Customer

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')

        print('username:', username,'first_name:', first_name, 'email:', email )

        # Check if the username or email is already registered
        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'error': 'Username is already taken.'})
        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'error': 'Email is already registered.'})

        # Create the User object
        user = User.objects.create_user(
            username=first_name,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # Create the Customer object linked to the User
        customer = Customer.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            loyalty_points=0  # Default loyalty points
        )

        # Automatically log the user in
        auth_login(request, user)

        return JsonResponse({'success': True, 'message': 'Registration successful!'})



@login_required
def user_logout(request):
    logout(request)  # Log the user out
    return redirect('home')  # Redirect to the home page





@login_required
def customer_dashboard(request):
    # Fetch the customer associated with the logged-in user
    customer = get_object_or_404(Customer, email=request.user.email)

    # Fetch all appointments for the customer
    appointments = Appointment.objects.filter(customer=customer).order_by('-appointment_date')

    # Calculate total loyalty points
    loyalty_points = customer.loyalty_points

    # Fetch all payments made by the customer
    payments = Billing.objects.filter(appointment__customer=customer).order_by('-created_at')

    return render(request, 'customers/2_customer_dashboard.html', {
        'customer': customer,
        'appointments': appointments,
        'loyalty_points': loyalty_points,
        'payments': payments,
    })

def register_prompt(request):
    return render(request, 'customers/register_prompt.html')