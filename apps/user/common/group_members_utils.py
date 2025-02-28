from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from apps.user.models import GroupMember, User, UserGroup
from django.db.models import Q
from django.db.models import Count

@login_required
def get_faculty_and_staff_info(request):
    user = request.user
    user_groups = UserGroup.objects.all()

    # Get the most recent group with members based on the user's program and institute
    recent_group_with_members = UserGroup.objects.annotate(
        member_count=Count('groupmember')
    ).filter(
        member_count__gt=0,
        institute=user.institute
    ).order_by('-date_created').first()

    # Determine the group ID to use
    group_id = request.GET.get('group')
    if not group_id and recent_group_with_members:
        group_id = recent_group_with_members.group_id

    if group_id:
        request.session['recent_group'] = group_id 

    # Fetch group members and filter by the selected group
    group_members = GroupMember.objects.filter(group_id=group_id).select_related('user').prefetch_related('courses') if group_id else GroupMember.objects.none()   

    # Get search term
    search_term = request.GET.get('search', '').strip()
    search_terms = search_term.split()
    if len(search_terms) == 2:
        first_name_search = search_terms[0]
        last_name_search = search_terms[1]
    else:
        first_name_search = search_term
        last_name_search = ''

    faculty_and_staff = User.objects.filter(
        id__in=group_members.values('user_id'),
        # program=user.program
    ).filter(
        Q(first_name__icontains=first_name_search) & Q(last_name__icontains=last_name_search) |
        Q(first_name__icontains=search_term) |
        Q(last_name__icontains=search_term) |
        Q(email__icontains=search_term)
    ).distinct()

    # Pagination setup
    items_per_page = request.GET.get('items_per_page', 25)
    paginator = Paginator(faculty_and_staff.order_by('-id'), items_per_page)
    page_number = request.GET.get('page', 1)
    try:
        faculty_and_staff_paginated = paginator.page(page_number)
    except PageNotAnInteger:
        faculty_and_staff_paginated = paginator.page(1)
    except EmptyPage:
        faculty_and_staff_paginated = paginator.page(paginator.num_pages)

    # Fetch additional user info (make sure these fields exist on the User model)
    try:
        program_name = user.program.program_name
        program_code = user.program.program_code
        institute_name = user.institute.institute_name
    except AttributeError:
        program_name = program_code = institute_name = "N/A"

    page_number = faculty_and_staff_paginated.number
    start_index = (page_number - 1) * paginator.per_page + 1

    # Get all groups for selection
    all_groups = UserGroup.objects.filter(program=user.program, institute=user.institute).order_by('-date_created')

    # Safe retrieval of selected group based on user's program and institute
    selected_group = None
    if group_id:
      try:
        selected_group = UserGroup.objects.get(group_id=group_id, program=user.program, institute=user.institute)
      except UserGroup.DoesNotExist:
        selected_group = None  # Handle case where group doesn't exist
    
    # Return data for AJAX or full view
    return {
        'faculty_and_staff': faculty_and_staff_paginated,
        'total_users': faculty_and_staff.count(),
        'program_name': program_name,
        'program_code': program_code,
        'institute_name': institute_name,
        'all_groups': all_groups,
        'selected_group': selected_group,
        'user_groups': user_groups,
        'start_index': start_index,
        'group_members': group_members,
        'group_id': group_id,
    }