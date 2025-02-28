from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import SuspiciousOperation
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from apps.curriculum.models import Programs
from apps.institutes.models import Institutes
from apps.user.common.account_utils import update_personal_information
from apps.user.common.location_utils import get_location_from_ip
from apps.user.common.user_notification import create_notification
from apps.user.models import Notification, User
from .forms import CoverImageForm, RequestPasswordChangeForm, ProfileImageForm, UpdatePersonalInfoForm
from django.http import Http404, JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from qsessions.models import Session
from django_otp.plugins.otp_email.models import EmailDevice
from django.utils.crypto import get_random_string
from .forms import SignupForm
from django.urls import reverse
from django.db import IntegrityError
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST

@login_required
def validate_password(request):
    if request.method == 'POST':
        # Ensure password is provided
        current_password = request.POST.get('oldpassword')
        if not current_password:
            return JsonResponse({'valid': False, 'error': 'Password is required'}, status=400)

        # Use the authenticate function securely
        user = authenticate(username=request.user.username, password=current_password)
        
        if user is not None:
            return JsonResponse({'valid': True})

        return JsonResponse({'valid': False})
    
    # Reject any other methods with an error message
    raise SuspiciousOperation("Invalid request method")

# Format phone number
def format_phone_number(number):
    number = ''.join(filter(str.isdigit, number))
    if len(number) == 11:
        return f"{number[:4]}-{number[4:7]}-{number[7:]}"
    return number

@login_required
def profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.user.id != user.id:
        user = request.user
        url = reverse('user:profile', args=[user.id])
        return redirect(url)
    
    # Initialize session details and forms
    session_details = []
    page_obj = None
    personal_info_form = UpdatePersonalInfoForm(instance=user)
    profile_form = ProfileImageForm(instance=user)
    cover_form = CoverImageForm(instance=user)
    password_form = RequestPasswordChangeForm(user=request.user)

    if request.method == 'POST':
        # Handle session deletion
        if 'deleteSessionSubmit' in request.POST:
          session_key = request.POST.get('session_key')
          if session_key and session_key != request.session.session_key:
              try:
                  session = Session.objects.get(session_key=session_key)
                  messages.info(request, "You have successfully logged out the session from another device.")
                  session.delete()
                  return redirect('user:profile', user_id=user.id)
              except Session.DoesNotExist:
                  messages.error(request, "The specified session could not be found.")

        # Update personal information
        if 'personalInfoSubmit' in request.POST:
          update_personal_information(request, user)
          return redirect('user:profile', user_id=user.id)

        # Handle OTP sending and password change
        if 'send_otp' in request.POST:
            password_form = RequestPasswordChangeForm(data=request.POST, user=user)
            if password_form.is_valid():
                send_otp = password_form.cleaned_data.get('send_otp')

                if send_otp:
                    # Generate a secure token for the password change request
                    token = get_random_string(32)
                    request.session['password_change_token'] = token

                    # Generate and send OTP
                    device, created = EmailDevice.objects.get_or_create(user=user, confirmed=True)
                    if created:
                        print(f"EmailDevice created for user: {user.email}")
                    if device.generate_challenge():
                        print("OTP challenge generated and sent.")
                        messages.success(request, 'OTP has been sent to your email.')
                        return redirect('user:profile', user_id=user_id)
                    else:
                        print("Failed to generate OTP challenge.")
                        messages.error(request, 'Failed to send OTP. Please try again.')
        
        elif 'changePasswordSubmit' in request.POST:
            password_form = RequestPasswordChangeForm(data=request.POST, user=user)
            if password_form.is_valid():
                otp_code = password_form.cleaned_data.get('otp')
                token = request.session.get('password_change_token')

                if otp_code and token:
                    device = EmailDevice.objects.filter(user=user).first()
                    if device and device.verify_token(otp_code):
                        if token == request.session.get('password_change_token'):
                            password_form.save()
                            del request.session['password_change_token']
                            messages.success(request, 'Your password has been changed successfully. You can now log in with your new credentials.')
                            return redirect('user:profile', user_id=user.id)
                        else:
                            messages.error(request, 'This code is expired. Resend for a new one.')
                    else:
                        messages.error(request, 'This code doesn’t work. Check it’s correct or try a new one.')
                else:
                    messages.error(request, 'OTP or token is missing.')

    # Handle GET request to fetch session details
    if request.method == 'GET' or 'session_key' not in request.POST:
        sessions = user.session_set.filter(expire_date__gt=timezone.now()).order_by('-created_at')
        paginator = Paginator(sessions, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        session_details = []

        for session in page_obj:
            location = None
            if session.ip:
                location = get_location_from_ip(session.ip)
            session_details.append({
                'session_key': session.session_key,
                'created_at': session.created_at,
                'expire_date': session.expire_date,
                'ip': session.ip,
                'user_agent': session.user_agent,
                'device': str(session.device()),
                'location': location,
            })

    # Format
    gender_choices = list(personal_info_form.fields['gender'].choices)[1:]
    selected_gender = personal_info_form.instance.gender
    phone_number = user.phone_number
    formatted_phone_number = format_phone_number(phone_number) if phone_number else ''

    return render(request, 'account/profile.html', {
        'personal_info_form': personal_info_form,
        'profile_form': profile_form,
        'cover_form': cover_form,
        'gender_choices': gender_choices,
        'selected_gender': selected_gender,
        'user_type': request.user.user_type,
        'formatted_phone_number': formatted_phone_number,
        'password_form': password_form,
        'session_details': session_details,
        'page_obj': page_obj,
    })

def signup(request):
    if request.method == 'POST':
        signup_form = SignupForm(request.POST, prefix='signup')
        if signup_form.is_valid():
            email = signup_form.cleaned_data.get('email')
            if User.objects.filter(email=email).exists():
                signup_form.add_error('email', "The email address you're trying to use is already associated with an account.")
                messages.error(request, "The email address you're trying to use is already associated with an account.")
                return render(request, 'account/signup.html', {
                    'signup_form': signup_form,
                    'form_prefix': 'signup',
                })
            try:
                user = signup_form.save(request)
                user.first_name = signup_form.cleaned_data.get('first_name', '')
                user.last_name = signup_form.cleaned_data.get('last_name', '')
                user.middle_name = signup_form.cleaned_data.get('middle_name', '')
                user.suffix = signup_form.cleaned_data.get('suffix', '')
                user.save()
                
                # Create a notification for the new user
                admin_user = User.objects.get(email="acadsked@gmail.com")
                create_notification(
                    recipient=user,
                    message="Your account has been successfully created. Welcome!",
                    status=1,
                    sender=admin_user,
                    notification_url=f'/user/notification/{user.username}'
                )
                create_notification(
                    recipient=user,
                    message=f'Required: The program chair cannot assign a schedule if your faculty information, including your assigned program, is missing. Please go to <a href="/user/my-profile/{user.id}/" class="font-semibold underline">My Profile</a> to add the information.',
                    status=1,
                    sender=admin_user,
                    notification_url=f'/user/notification/{user.username}'
                )
                
                return redirect('verify-account')
            except IntegrityError:
                signup_form.add_error('email', 'An error occurred while processing your request. Please try again.')
                messages.error(request, 'An error occurred while processing your request. Please try again.')
                return render(request, 'account/signup.html', {
                    'signup_form': signup_form,
                    'form_prefix': 'signup',
                })
        else:
            messages.error(request, "There were errors in the form. Please correct them and try again.")
    else:
        signup_form = SignupForm(prefix='signup')

    return render(request, 'account/signup.html', {
        'signup_form': signup_form,
        'form_prefix': 'signup',
    })

def verify_account(request):
    return render(request, 'account/verification_sent.html')



def time_since(dt):
    now = datetime.now(dt.tzinfo)
    diff = now - dt

    periods = [
        (diff.days // 365, "year", "years"),
        (diff.days // 30, "month", "months"),
        (diff.days // 7, "week", "weeks"),
        (diff.days, "day", "days"),
        (diff.seconds // 3600, "hour", "hours"),
        (diff.seconds // 60, "minute", "minutes"),
        (diff.seconds, "second", "seconds"),
    ]

    for period, singular, plural in periods:
        if period:
            return f"{period} {singular if period == 1 else plural} ago"
    return "just now"

@login_required
def notification(request, username):
    user = get_object_or_404(User, username=username)
    if request.user.id != user.id:
        user = request.user
        url = reverse('user:notification', args=[user.id])
        return redirect(url)

    notifications_list = Notification.objects.filter(recipient=user).select_related('sender')
    total_notifications = notifications_list.count()

    paginator = Paginator(notifications_list, 24)
    page = request.GET.get('page')
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate the offset
    pagination_offset = (page_obj.number - 1) * paginator.per_page

    try:
        notifications = paginator.page(page)
    except PageNotAnInteger:
        notifications = paginator.page(1)
    except EmptyPage:
        notifications = paginator.page(paginator.num_pages)

    notification_details = []
    for notification in notifications:
        sender = notification.sender
        notification_details.append({
            'profile_image_url': sender.profile_image.url if sender and sender.profile_image else None,
            'email': sender.email if sender else None,
            'first_name': sender.first_name if sender else None,
            'middle_name': sender.middle_name if sender else None,
            'last_name': sender.last_name if sender else None,
            'full_name': f"{sender.first_name} {sender.last_name}".strip() if sender else None,
            'message': notification.message,
            'status': notification.get_status_display(),
            'date_time': time_since(notification.date_time),
            'is_read': notification.is_read,
        })

    return render(request, 'account/notification.html', {
        'user_type': request.user.user_type,
        'notifications': notification_details,
        'total_notifications': total_notifications,
        'page': page,
        'page_obj': notifications,
        'pagination_offset': pagination_offset,
        'paginator': paginator,
    })

@login_required
@require_POST
def mark_all_as_read(request):
    if request.method == 'POST':
      user = request.user
      Notification.objects.filter(recipient=user, is_read=False).update(is_read=True, status=2, read_at=timezone.now())
      return JsonResponse({'status': 'success'})
    raise SuspiciousOperation("Invalid request method")