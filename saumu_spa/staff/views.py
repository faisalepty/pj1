from django.shortcuts import render

# Create your views here.
# staff/views.py
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Staff

# staff/views.py
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def staff_detail(request, pk):
    # Fetch the staff member by ID
    staff = get_object_or_404(Staff, id=pk)

    # Return JSON response
    data = {
        'id': staff.id,
        'first_name': staff.first_name,
        'last_name': staff.last_name,
        'role': staff.role,
        'commission_rate': str(staff.commission_rate),
    }
    return JsonResponse(data)

def staff_list(request):
    # Query all staff members
    queryset = Staff.objects.all().order_by('id')

    # Apply role filter
    role_filter = request.GET.get('role', '')  # Default to no filter
    if role_filter:
        queryset = queryset.filter(role=role_filter)

    # Pagination
    page_number = request.GET.get('page', 1)
    entries_per_page = request.GET.get('entries', 10)  # Default to 10 entries per page
    paginator = Paginator(queryset, entries_per_page)

    try:
        page_obj = paginator.page(page_number)
    except (EmptyPage, PageNotAnInteger):
        page_obj = paginator.page(1)

    # Check if the request is an AJAX call
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = {
            'staff': [
                {
                    'id': s.id,
                    'first_name': s.first_name,
                    'last_name': s.last_name,
                    'role': s.role,
                    'commission_rate': str(s.commission_rate),
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

    # Render the template for non-AJAX requests
    return render(request, 'reports/staff_report.html', {'staff': page_obj, 'st': 'st'})

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def staff_create_update(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        staff_id = data.get('id')

        # Update existing staff member or create a new one
        if staff_id:
            staff = get_object_or_404(Staff, id=staff_id)
        else:
            staff = Staff()

        staff.first_name = data.get('first_name')
        staff.last_name = data.get('last_name')
        staff.role = data.get('role')
        staff.commission_rate = data.get('commission_rate')
        staff.save()

        return JsonResponse({'success': True, 'message': 'Staff saved successfully.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})



@csrf_exempt
def staff_delete(request):
    if request.method == 'DELETE':
        data = json.loads(request.body)
        staff_id = data.get('id')
        staff = get_object_or_404(Staff, id=staff_id)
        staff.delete()
        return JsonResponse({'success': True, 'message': 'Staff deleted successfully.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})