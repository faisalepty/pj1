# Generated migration file (e.g., 0002_auto_create_users_for_staff.py)
from django.db import migrations
from django.contrib.auth.models import User

def create_users_for_staff(apps, schema_editor):
    Staff = apps.get_model('staff', 'Staff')  # Replace 'your_app_name' with your app name
    username_counter = {}  # Dictionary to track usernames and ensure uniqueness

    for staff in Staff.objects.all():
        # Generate a base username using first_name and last_name
        base_username = f"{staff.first_name.lower()}_{staff.last_name.lower()}"
        username = base_username

        # Ensure the username is unique by checking the database
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1

        # Create a User instance for the staff member
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",  # Default email
            password='defaultpassword',  # Default password (you can change this later)
            first_name=staff.first_name,
            last_name=staff.last_name
        )

        # Link the User instance to the Staff instance
        staff.user = user
        staff.save()

class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0001_initial'),  # Replace with your previous migration file
    ]

    operations = [
        migrations.RunPython(create_users_for_staff),
    ]