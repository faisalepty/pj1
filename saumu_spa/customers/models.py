# customers/models.py
from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    loyalty_points = models.PositiveIntegerField(default=0)  # Total loyalty points balance
    created_at = models.DateTimeField(auto_now_add=True)
    is_registered = models.BooleanField(default=False, blank=True, null=True)  # Flag to track registration status

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def add_loyalty_points(self, points):
        """Add loyalty points to the customer's balance."""
        self.loyalty_points += points
        self.save()

    def redeem_loyalty_points(self, points):
        """Redeem loyalty points for a discount."""
        if self.loyalty_points >= points:
            self.loyalty_points -= points
            self.save()
            return True
        return False