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




from django.db import models
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from services.models import Service  # Replace 'yourapp' with your app name

# Clear existing data (optional)
Service.objects.all().delete()

# Hair Service data
hair_services = [
    {
        "name": "Hair cut (Adults)",
        "category": "haircut",
        "duration": timedelta(hours=1),  # Assuming 1 hour
        "price": Decimal("500.00"),
        "description": "A classic haircut tailored for adults, ensuring a sharp and polished look."
    },
    {
        "name": "Hair cut (Kids)",
        "category": "haircut",
        "duration": timedelta(hours=0.5),  # Assuming 30 minutes
        "price": Decimal("300.00"),
        "description": "A fun and quick haircut designed for kids, keeping them comfortable."
    },
    {
        "name": "Dye/Color",
        "category": "haircut",
        "duration": timedelta(hours=2),  # Assuming 2 hours
        "price": Decimal("1500.00"),
        "description": "Professional hair dyeing service to add vibrant color or refresh your style."
    },
    {
        "name": "Hair cut + Texturizing",
        "category": "haircut",
        "duration": timedelta(hours=2),  # Assuming 2 hours
        "price": Decimal("1500.00"),
        "description": "A combined haircut and texturizing service for added volume and style."
    },
    {
        "name": "Beards",
        "category": "haircut",
        "duration": timedelta(minutes=30),  # Assuming 30 minutes
        "price": Decimal("300.00"),
        "description": "Expert beard trimming and shaping for a well-groomed appearance."
    },
    {
        "name": "Outline",
        "category": "haircut",
        "duration": timedelta(minutes=30),  # Assuming 30 minutes
        "price": Decimal("300.00"),
        "description": "Precise outlining to define your haircut and enhance your look."
    }
]

# Hair Removal & Nail Care data
hair_removal_nail_care = [
    {
        "name": "Under arm (Waxing)",
        "category": "spa",
        "duration": timedelta(minutes=30),  # Default duration
        "price": Decimal("500.00"),
        "description": "Smooth underarm waxing for a clean and lasting result."
    },
    {
        "name": "Brazilian (Waxing)",
        "category": "spa",
        "duration": timedelta(minutes=45),  # Default duration
        "price": Decimal("2500.00"),
        "description": "Full Brazilian waxing for a complete and comfortable hair removal experience."
    },
    {
        "name": "Full legs (Waxing)",
        "category": "spa",
        "duration": timedelta(minutes=60),  # Default duration
        "price": Decimal("1500.00"),
        "description": "Full leg waxing for silky-smooth skin from thigh to ankle."
    },
    {
        "name": "Half legs (Waxing)",
        "category": "spa",
        "duration": timedelta(minutes=30),  # Default duration
        "price": Decimal("800.00"),
        "description": "Half leg waxing for a quick and effective hair removal solution."
    },
    {
        "name": "Upper lips & chin (Waxing)",
        "category": "spa",
        "duration": timedelta(minutes=30),  # Default duration
        "price": Decimal("500.00"),
        "description": "Gentle waxing for upper lips and chin to remove unwanted hair."
    },
    {
        "name": "Spa pedicure",
        "category": "spa",
        "duration": timedelta(minutes=60),  # Default duration
        "price": Decimal("1500.00"),
        "description": "A relaxing pedicure with exfoliation, massage, and polish for healthy feet."
    },
    {
        "name": "Spa manicure",
        "category": "spa",
        "duration": timedelta(minutes=60),  # Default duration
        "price": Decimal("1500.00"),
        "description": "A luxurious manicure with nail care, cuticle treatment, and polish."
    },
    {
        "name": "Cut & File",
        "category": "spa",
        "duration": timedelta(minutes=30),  # Default duration
        "price": Decimal("400.00"),
        "description": "Basic nail trimming and filing for a neat and tidy appearance."
    }
]

# Massage & Body Treatments data
massage_body_treatments = [
    {
        "name": "Deep tissue massage",
        "category": "massage",
        "duration": timedelta(hours=1),
        "price": Decimal("3500.00"),
        "description": "A deep pressure massage to relieve muscle tension and improve mobility."
    },
    {
        "name": "Swedish massage",
        "category": "massage",
        "duration": timedelta(hours=1),
        "price": Decimal("2500.00"),
        "description": "A gentle, relaxing massage to enhance circulation and reduce stress."
    },
    {
        "name": "Back/Head massage",
        "category": "massage",
        "duration": timedelta(minutes=30),
        "price": Decimal("2000.00"),
        "description": "A targeted massage for back and head relief in a short session."
    },
    {
        "name": "Aromatherapy massage",
        "category": "massage",
        "duration": timedelta(hours=1),
        "price": Decimal("3000.00"),
        "description": "A soothing massage with essential oils to promote relaxation and well-being."
    },
    {
        "name": "Hot stone massage",
        "category": "massage",
        "duration": timedelta(hours=1, minutes=30),
        "price": Decimal("4000.00"),
        "description": "A luxurious massage with heated stones to melt away tension."
    },
    {
        "name": "Reflexology massage",
        "category": "massage",
        "duration": timedelta(minutes=45),
        "price": Decimal("1500.00"),
        "description": "A foot-focused massage to stimulate energy flow and reduce stress."
    },
    {
        "name": "Body scrub",
        "category": "massage",
        "duration": timedelta(minutes=30),  # Default duration
        "price": Decimal("2500.00"),
        "description": "An exfoliating scrub to remove dead skin and leave your body refreshed."
    },
    {
        "name": "Full facial",
        "category": "massage",
        "duration": timedelta(minutes=60),  # Default duration
        "price": Decimal("3500.00"),
        "description": "A comprehensive facial treatment to cleanse, hydrate, and rejuvenate skin."
    },
    {
        "name": "Face scrub & steam",
        "category": "massage",
        "duration": timedelta(minutes=30),  # Default duration
        "price": Decimal("2000.00"),
        "description": "A gentle scrub and steam session to purify and soften your skin."
    }
]

# Combine all services
all_services = hair_services + hair_removal_nail_care + massage_body_treatments

# Create Service objects in the database
for service_data in all_services:
    service = Service(**service_data)
    service.save()

print("Services have been successfully added to the database!")