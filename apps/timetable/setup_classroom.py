from django.db import IntegrityError
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.curriculum.models import Rooms
from apps.timetable.item_per_page_utils import validate_items_per_page
from apps.user.utils import get_template_by_user_type
from django.core.paginator import Paginator

@login_required
def classrooms(request):
    template = get_template_by_user_type(request.user, 'classrooms')
    classrooms = Rooms.objects.all()
    
    items_per_page = request.GET.get('items_per_page', 25)
    page_number = request.GET.get('page', 1)
    
    validated_items_per_page = validate_items_per_page(items_per_page, request, page_number)
    if isinstance(validated_items_per_page, HttpResponseRedirect):
        return validated_items_per_page
    
    paginator = Paginator(classrooms.order_by('-room_id'), validated_items_per_page)
    paginated_classroom = paginator.get_page(page_number)
    
    total_classroom = classrooms.count()
    page_number = paginated_classroom.number
    start_index = (page_number - 1) * paginator.per_page + 1

    if request.method == 'POST':
        if 'DeleteClassroomSubmit' in request.POST:
            room_id = request.POST.get('room_id')
            room = get_object_or_404(Rooms, room_id=room_id)
            room_name = room.room_name
            room.delete()
            messages.success(request, f"{room_name.upper()} has been deleted successfully.")
            page_number = request.GET.get('page', 1)
            return redirect(f"{request.path}?page={page_number}&items_per_page={items_per_page}")
    
        if 'UpdateClassroomSubmit' in request.POST:
            room_id = request.POST.get('room_id')
            room = get_object_or_404(Rooms, room_id=room_id)
            
            room_name = request.POST.get('classroom_name')
            building = request.POST.get('building')
            is_lab = request.POST.get('is_lab') == 'on'
            
            room.room_name = room_name
            room.building = building
            room.is_lab = is_lab
            room.save()
            
            messages.success(request, f"{room.room_name.upper()} has been updated successfully.")
            return redirect(f"{request.path}?page={page_number}&items_per_page={items_per_page}")
        
        if 'AddClassroomSubmit' in request.POST:
          room_name = request.POST.get('classroom_name')
          building = request.POST.get('building')
          is_lab = request.POST.get('is_lab') == 'on'
          
          try:
              Rooms.objects.create(room_name=room_name, building=building, is_lab=is_lab)
              messages.success(request, f"{room_name.upper()} added successfully.")
          except IntegrityError:
              messages.error(request, f"Room {room_name.upper()} already exists.")
          
          return redirect(f"{request.path}?page={page_number}&items_per_page={items_per_page}")
        
        if 'DeleteAllClassroomSubmit' in request.POST:
            room_ids = request.POST.get('room_ids', '')
            room_ids = [int(id) for id in room_ids.split(',') if id.isdigit()]

            if room_ids:
                rooms = Rooms.objects.filter(room_id__in=room_ids)
                deleted_count = 0
                for room in rooms:
                    room_name = room.room_name
                    room.delete()
                    deleted_count += 1

                if deleted_count > 0:
                    messages.success(request, f"{deleted_count} classroom(s) have been deleted successfully.")

            return redirect(f"{request.path}?page={page_number}&items_per_page={items_per_page}")
            
    if template and request.user.user_type in [4]:
        return render(request, template, {
            'classrooms': paginated_classroom,
            'total_classroom': total_classroom,
            'start_index': start_index,
            'items_per_page': items_per_page,
            })
    
    raise Http404
