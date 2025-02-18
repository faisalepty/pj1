# reports/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from billing.models import Billing
from appointments.models import Appointment
from django.db.models import Count, Sum
from datetime import timedelta
from django.utils.timezone import now, make_aware
from django.http import HttpResponse
import csv

def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
def sales_report(request):
    # Default time range: last 5 years (timezone-aware)
    end_date = now()  # Use timezone-aware current time
    start_date = end_date - timedelta(days=1825)  # Use a wider range (e.g., 5 years)

    # Handle date filters from the form
    if request.method == 'POST':
        raw_start_date = request.POST.get('start_date')
        raw_end_date = request.POST.get('end_date')

        # Parse dates only if they are provided as strings
        if raw_start_date:
            start_date = make_aware(datetime.strptime(raw_start_date, '%Y-%m-%d'))
        if raw_end_date:
            end_date = make_aware(datetime.strptime(raw_end_date, '%Y-%m-%d'))

    # Debugging: Print the date range
    print(f"Start Date: {start_date}, End Date: {end_date}")

    # Query payments within the selected time range
    payments = Billing.objects.filter(created_at__range=[start_date, end_date])

    # Calculate total revenue
    total_revenue = payments.aggregate(total=Sum('total'))['total'] or 0

    # Most popular services
    popular_services = Appointment.objects.filter(
        appointment_date__range=[start_date, end_date]
    ).values('service__name').annotate(count=Count('service')).order_by('-count')[:5]

    # Peak booking times
    peak_times = Appointment.objects.filter(
        appointment_date__range=[start_date, end_date]
    ).values('appointment_date').annotate(count=Count('id')).order_by('-count')[:5]

    # Customer retention rates
    repeat_customers = Appointment.objects.filter(
        appointment_date__range=[start_date, end_date]
    ).values('customer').annotate(count=Count('id')).filter(count__gt=1).count()

    context = {
        'payments': payments,
        'total_revenue': total_revenue,
        'popular_services': popular_services,
        'peak_times': peak_times,
        'repeat_customers': repeat_customers,
        'start_date': start_date,
        'end_date': end_date,
    }

    # Export to CSV
    if 'export_csv' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Service', 'Total Revenue'])
        for payment in payments:
            writer.writerow([payment.appointment.service.name, payment.total])
        return response

    return render(request, 'reports/sales_report.html', context)