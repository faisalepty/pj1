# services/views.py
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.shortcuts import render
from .models import Service
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import timedelta

def get_service(request, service_id):
    # Fetch the service by ID or return a 404 response if it doesn't exist
    service = get_object_or_404(Service, id=service_id)
    data = {
        'id': service.id,
        'name': service.name,
        'category': service.category,
        'duration': str(service.duration),
        'price': str(service.price),
        'description': service.description or '',
    }
    return JsonResponse(data)

def service_list(request):
    queryset = Service.objects.all().order_by('id')

    # Apply category filter
    category_filter = request.GET.get('category', '')
    if category_filter:
        queryset = queryset.filter(category=category_filter)

    # Pagination
    page_number = request.GET.get('page', 1)
    entries_per_page = request.GET.get('entries', 10)
    paginator = Paginator(queryset, entries_per_page)

    try:
        page_obj = paginator.page(page_number)
    except (EmptyPage, PageNotAnInteger):
        page_obj = paginator.page(1)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = {
            'services': [
                {
                    'id': s.id,
                    'name': s.name,
                    'category': s.category,
                    'duration': str(s.duration),
                    'price': str(s.price),
                    'description': s.description or '',
                }
                for s in page_obj.object_list
            ],
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        }
        return JsonResponse(data)

    return render(request, 'reports/service_report.html', {'services': page_obj, 'sv': 'sv'})





@csrf_exempt
def create_update_service(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)

            # Extract service ID (if updating an existing service)
            service_id = data.get('id')

            # Convert duration string to timedelta
            duration_str = data.get('duration')
            if duration_str:
                try:
                    hours, minutes, seconds = map(int, duration_str.split(':'))
                    duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)
                except ValueError:
                    return JsonResponse({'success': False, 'error': 'Invalid duration format. Use HH:MM:SS.'})
            else:
                duration = None

            if service_id:
                # Update an existing service
                service = get_object_or_404(Service, id=service_id)
                service.name = data.get('name', service.name)
                service.category = data.get('category', service.category)
                service.duration = duration or service.duration
                service.price = data.get('price', service.price)
                service.description = data.get('description', service.description)
                service.save()
            else:
                # Create a new service
                Service.objects.create(
                    name=data.get('name'),
                    category=data.get('category'),
                    duration=duration,
                    price=data.get('price'),
                    description=data.get('description', '')
                )

            # Return success response
            return JsonResponse({'success': True})

        except Exception as e:
            # Log the error and return an error response
            print(f"Error in create_update_service: {e}")
            return JsonResponse({'success': False, 'error': str(e)})

    # Return error for invalid request methods
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def delete_service(request):
    print('success \n \n \n')
    if request.method == 'DELETE':
        print('success \n \n \n')
        try:
            print('success \n \n \n')
            data = json.loads(request.body)
            print('success \n \n \n', 'data', data)
            service_id = data.get('id')
            print('success \n \n \n', 'service_id', service_id )
            service = get_object_or_404(Service, id=service_id)
            print('seeeervice \n \n \n \n',service)
            service.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
            print('error \n \n \n')
    return JsonResponse({'success': False, 'error': 'Invalid request method'})













# services/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from .models import Service
from .forms import ServiceForm
from itertools import groupby


# Helper function to check if the user is an admin
def is_admin(user):
    return user.is_authenticated and user.is_staff

#
def service_list_client(request):
    # Fetch all services and order them by category
    services = Service.objects.all().order_by('category')
    categories = Service.CATEGORY_CHOICES

    # Group services by category

    grouped_services = {}
    for category, group in groupby(services, key=lambda x: x.get_category_display()):
        grouped_services[category] = list(group)

    return render(request, 'services/3_services.html', {'grouped_services': grouped_services, 'services': services, 'categories': categories})
# @user_passes_test(is_admin)
# def add_service(request):
#     if request.method == 'POST':
#         form = ServiceForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('service_list')
#     else:
#         form = ServiceForm()
#     return render(request, 'services/add_service.html', {'form': form})

# @user_passes_test(is_admin)
# def edit_service(request, pk):
#     service = get_object_or_404(Service, pk=pk)
#     if request.method == 'POST':
#         form = ServiceForm(request.POST, instance=service)
#         if form.is_valid():
#             form.save()
#             return redirect('service_list')
#     else:
#         form = ServiceForm(instance=service)
#     return render(request, 'services/edit_service.html', {'form': form})

# @user_passes_test(is_admin)
# def delete_service(request, pk):
#     service = get_object_or_404(Service, pk=pk)
#     if request.method == 'POST':
#         service.delete()
#         return redirect('service_list')
#     return render(request, 'services/delete_service.html', {'service': service})