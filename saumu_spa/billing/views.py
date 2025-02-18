# billing/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Billing
from appointments.models import Appointment
from .forms import BillingForm

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