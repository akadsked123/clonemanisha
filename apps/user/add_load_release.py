from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from .models import AdminLoadRelease, REPLoadRelease, User, UserGroup
from django.contrib import messages

@require_http_methods(["GET", "POST"])
def add_load_Admin_REP_release(request, selected_instructor_id, group_id):
    instructor = get_object_or_404(User, id=selected_instructor_id)
    selected_group = get_object_or_404(UserGroup, group_id=group_id)
    data_processed = False

    if request.method == 'POST':
        if "AddLoadReleaseButton" in request.POST:
            print("POST data:", request.POST)
            for key, value in request.POST.items():
                print(f'Processing key: {key}, value: {value}')
                if key.startswith('admin_load_id_'):
                    load_id = value
                    if load_id == 'new':
                        new_id = key.split('_')[-1]
                        description = request.POST.get(f'admin_description_new_{new_id}')
                        hour = request.POST.get(f'admin_hour_new_{new_id}')
                        unit = request.POST.get(f'admin_unit_new_{new_id}')
                        print(f'Processing new admin load: {new_id}, {description}, {hour}, {unit}')
                        if description:
                            AdminLoadRelease.objects.create(
                                user=instructor,
                                description=description,
                                hour=hour,
                                unit=unit,
                                group_id=selected_group
                            )
                            data_processed = True
                    else:
                        description = request.POST.get(f'admin_description_{load_id}')
                        hour = request.POST.get(f'admin_hour_{load_id}')
                        unit = request.POST.get(f'admin_unit_{load_id}')
                        print(f'Processing admin load: {load_id}, {description}, {hour}, {unit}')
                        if description:
                            admin_load = get_object_or_404(AdminLoadRelease, id=load_id)
                            admin_load.description = description
                            admin_load.hour = hour
                            admin_load.unit = unit
                            admin_load.save()
                            data_processed = True

            for key, value in request.POST.items():
                print(f'Processing key: {key}, value: {value}')
                if key.startswith('rep_load_id_'):
                    load_id = value
                    if load_id == 'new':
                        new_id = key.split('_')[-1]
                        description = request.POST.get(f'rep_description_new_{new_id}')
                        hour = request.POST.get(f'rep_hour_new_{new_id}')
                        unit = request.POST.get(f'rep_unit_new_{new_id}')
                        print(f'Processing new rep load: {new_id}, {description}, {hour}, {unit}')
                        if description:
                            REPLoadRelease.objects.create(
                                user=instructor,
                                description=description,
                                hour=hour,
                                unit=unit,
                                group_id=selected_group
                            )
                            data_processed = True
                    else:
                        description = request.POST.get(f'rep_description_{load_id}')
                        hour = request.POST.get(f'rep_hour_{load_id}')
                        unit = request.POST.get(f'rep_unit_{load_id}')
                        print(f'Processing rep load: {load_id}, {description}, {hour}, {unit}')
                        if description:
                            rep_load = get_object_or_404(REPLoadRelease, id=load_id)
                            rep_load.description = description
                            rep_load.hour = hour
                            rep_load.unit = unit
                            rep_load.save()
                            data_processed = True

            if data_processed:
                messages.success(request, 'Successfully saved.')
            else:
                messages.info(request, 'No changes were made.')
            return redirect(request.path)

    admin_loads = AdminLoadRelease.objects.filter(user=instructor)
    rep_loads = REPLoadRelease.objects.filter(user=instructor)

    return render(request, './account/load_release.html', {
        'user_type': request.user.user_type,
        'admin_loads': admin_loads,
        'rep_loads': rep_loads,
        'selected_instructor_id': selected_instructor_id,
        'group_id': group_id,
        'instructor': instructor,
        'selected_group': selected_group
    })