# services/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from .models import Service
from .forms import ServiceForm
from itertools import groupby


# Helper function to check if the user is an admin
def is_admin(user):
    return user.is_authenticated and user.is_staff

#@user_passes_test(is_admin)
def service_list(request):
    # Fetch all services and order them by category
    services = Service.objects.all().order_by('category')
    categories = Service.CATEGORY_CHOICES

    # Group services by category

    grouped_services = {}
    for category, group in groupby(services, key=lambda x: x.get_category_display()):
        grouped_services[category] = list(group)

    return render(request, 'services/3_services.html', {'grouped_services': grouped_services, 'services': services, 'categories': categories})
@user_passes_test(is_admin)
def add_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('service_list')
    else:
        form = ServiceForm()
    return render(request, 'services/add_service.html', {'form': form})

@user_passes_test(is_admin)
def edit_service(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect('service_list')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'services/edit_service.html', {'form': form})

@user_passes_test(is_admin)
def delete_service(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.delete()
        return redirect('service_list')
    return render(request, 'services/delete_service.html', {'service': service})