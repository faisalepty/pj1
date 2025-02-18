# billing/forms.py
from django import forms
from .models import Billing

class BillingForm(forms.ModelForm):
    class Meta:
        model = Billing
        fields = ['payment_method', 'amount', 'discount', 'tax']