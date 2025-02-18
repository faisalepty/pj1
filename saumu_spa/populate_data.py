import random
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.contrib.auth.models import User  # Import the User model
from customers.models import Customer
from services.models import Service
from staff.models import Staff
from appointments.models import Appointment
from billing.models import Billing

# Helper function to generate random dates
def random_date(start, end):
    return make_aware(start + timedelta(seconds=random.randint(0, int((end - start).total_seconds()))))

# Clear existing data
User.objects.all().delete()  # Delete all users
Customer.objects.all().delete()
Service.objects.all().delete()
Staff.objects.all().delete()
Appointment.objects.all().delete()
Billing.objects.all().delete()

# Generate 50 Customers
customers = []
for i in range(1, 51):
    # Create a User object for the customer
    username = f"customer{i}"
    email = f"customer{i}@example.com"
    password = "defaultpassword"  # Set a default password (you can customize this)
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=f"Customer{i}",
        last_name=f"Last{i}"
    )

    # Create a Customer object linked to the User
    customer = Customer.objects.create(
        user=user,  # Link the Customer to the User
        first_name=f"Customer{i}",
        last_name=f"Last{i}",
        email=email,  # Unique email for each customer
        phone_number=f"+2547123456{i:02d}",  # Unique phone number for each customer
        loyalty_points=random.randint(0, 500)  # Random loyalty points between 0 and 500
    )
    customers.append(customer)

# Generate 50 Services
services = []
categories = ['haircut', 'massage', 'spa']
for i in range(1, 51):
    service = Service.objects.create(
        name=f"Service{i}",
        category=random.choice(categories),
        duration=timedelta(minutes=random.choice([30, 60, 90])),
        price=random.uniform(10.0, 200.0),  # Random price between $10 and $200
        description=f"Description for Service{i}" if random.random() > 0.5 else ""
    )
    services.append(service)

# Generate 10 Staff Members
staff_members = []
roles = ['Barber', 'Masseuse', 'Spa Specialist']
for i in range(1, 11):
    staff = Staff.objects.create(
        first_name=f"Staff{i}",
        last_name=f"Last{i}",
        role=random.choice(roles),
        availability="Available"
    )
    staff_members.append(staff)

# Generate 50 Appointments
appointments = []
statuses = ['pending', 'confirmed', 'completed', 'cancelled']
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 12, 31)
for i in range(1, 51):
    appointment_datetime = random_date(start_date, end_date)  # Combined date and time
    appointment = Appointment.objects.create(
        customer=random.choice(customers),
        service=random.choice(services),
        staff=random.choice(staff_members),
        appointment_date=appointment_datetime,  # Use combined datetime field
        status=random.choice(statuses),
        notes=f"Notes for appointment {i}" if random.random() > 0.5 else ""  # Optional notes
    )
    appointments.append(appointment)

# Generate 50 Billing Records
payment_methods = ['mpesa', 'cash']
for appointment in appointments:
    # Check if a Billing record already exists for this appointment
    if not hasattr(appointment, 'billing'):
        billing = Billing.objects.create(
            appointment=appointment,
            payment_method=random.choice(payment_methods),
            amount=appointment.service.price,
            discount=random.uniform(0.0, 10.0),  # Random discount between $0 and $10
            tax=random.uniform(0.0, 5.0),  # Random tax between $0 and $5
            total=appointment.service.price - random.uniform(0.0, 10.0) + random.uniform(0.0, 5.0),
            created_at=random_date(start_date, end_date)
        )

print("Database populated successfully!")