from django.shortcuts import get_object_or_404
from apps.timetable.models import ResultInstructor
from apps.user.models import User, UserGroup

# This function is to set up instructors in the group.
def get_users_list(request):
    if request.user.user_type == 4:
        group_id = request.GET.get('group')
        
        if not group_id:
            return {
                'user_options': [],
            }

        user_institute = request.user.institute
        users = User.objects.all()

        if user_institute:
            users = users.filter(institute=user_institute)

        group = get_object_or_404(UserGroup, group_id=group_id)
        existing_members = group.groupmember_set.values_list('user_id', flat=True)
        users = users.exclude(id__in=existing_members).only('id', 'first_name', 'middle_name', 'last_name', 'profile_image')
        # Order users by first name
        users = users.order_by('first_name')
        user_options = [
            {
          'value': user.id,
          'program': user.program.program_code if user.program else None,
          'text': user.get_full_name(),
          'profile': user.profile_image.url if user.profile_image and user.profile_image.url else f"https://ui-avatars.com/api/?name={user.first_name.replace(' ', '')}{user.middle_name.replace(' ', '') if user.middle_name else ''}{user.last_name.replace(' ', '')}&background=random"
            }
            for user in users
        ]
        return {
            'user_options': user_options,
        }

# This function is for scheduling instructors. It adds instructors to the generated schedule when they were not included in the initial setup.
def get_new_user_list(request, result_identification):
    if request.user.user_type == 4:
        user_institute = request.user.institute
        users = User.objects.only('id', 'first_name', 'middle_name', 'last_name', 'profile_image')

        if user_institute:
            users = users.filter(institute=user_institute)

        # Exclude users associated with the given result_identification
        result_instructors = ResultInstructor.objects.filter(result_identification=result_identification).only('instructor_id')
        instructor_ids = result_instructors.values_list('instructor_id', flat=True)
        users = users.exclude(id__in=instructor_ids)

        # Order users by first name
        users = users.order_by('first_name')

        user_options = [
            {
                'value': user.id,
                'text': user.get_full_name(),
                'program': user.program.program_code if user.program else None,
                'profile': user.profile_image.url if user.profile_image and user.profile_image.url else f"https://ui-avatars.com/api/?name={user.first_name.replace(' ', '')}{user.middle_name.replace(' ', '') if user.middle_name else ''}{user.last_name.replace(' ', '')}&background=random"
            }
            for user in users
        ]

        return {
            'user_options': user_options,
        }