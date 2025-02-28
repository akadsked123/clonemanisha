from django.dispatch import receiver
from allauth.account.signals import (user_logged_in,user_logged_out,user_signed_up,password_set,password_changed,password_reset,email_confirmed,email_confirmation_sent,email_changed,email_added,email_removed,)
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from allauth.account.signals import user_logged_out
from django.utils.translation import gettext_lazy as _

# @receiver(user_logged_in)
# def handle_user_logged_in(request, user, **kwargs):
#     send_mail(
#         'Login Notification',
#         'You have logged in successfully.',
#         settings.DEFAULT_FROM_EMAIL,
#         [user.email],
#     )

# @receiver(user_logged_out)
# def handle_user_logged_out(request, user, **kwargs):
#     send_mail(
#         'Logout Notification',
#         'You have logged out successfully.',
#         settings.DEFAULT_FROM_EMAIL,
#         [user.email],
#     )

# @receiver(user_signed_up)
# def handle_user_signed_up(request, user, **kwargs):
#     send_mail(
#         'Signup Notification',
#         'You have signed up successfully.',
#         settings.DEFAULT_FROM_EMAIL,
#         [user.email],
#     )

# @receiver(password_set)
# def handle_password_set(request, user, **kwargs):
#     send_mail(
#         'Password Set Notification',
#         'Your password has been set successfully.',
#         settings.DEFAULT_FROM_EMAIL,
#         [user.email],
#     )

# @receiver(password_changed)
# def handle_password_changed(request, user, **kwargs):
#     send_mail(
#         'Password Change Notification',
#         'Your password has been changed successfully.',
#         settings.DEFAULT_FROM_EMAIL,
#         [user.email],
#     )

# @receiver(password_reset)
# def handle_password_reset(request, user, **kwargs):
#     send_mail(
#         'Password Reset Notification',
#         'Your password has been reset successfully.',
#         settings.DEFAULT_FROM_EMAIL,
#         [user.email],
#     )

# @receiver(email_confirmed)
# def handle_email_confirmed(request, email_address, **kwargs):
#     send_mail(
#         'Email Confirmed Notification',
#         'Your email address has been confirmed.',
#         settings.DEFAULT_FROM_EMAIL,
#         [email_address.email],
#     )

# @receiver(email_confirmation_sent)
# def handle_email_confirmation_sent(request, confirmation, signup, **kwargs):
#     send_mail(
#         'Email Confirmation Sent',
#         'A confirmation email has been sent to you.',
#         settings.DEFAULT_FROM_EMAIL,
#         [confirmation.email_address.email],
#     )

# @receiver(email_changed)
# def handle_email_changed(request, user, from_email_address, to_email_address, **kwargs):
#     send_mail(
#         'Email Change Notification',
#         f'Your email address has been changed from {from_email_address.email} to {to_email_address.email}.',
#         settings.DEFAULT_FROM_EMAIL,
#         [to_email_address.email],
#     )

# @receiver(email_added)
# def handle_email_added(request, user, email_address, **kwargs):
#     send_mail(
#         'Email Added Notification',
#         'A new email address has been added to your account.',
#         settings.DEFAULT_FROM_EMAIL,
#         [email_address.email],
#     )

# @receiver(email_removed)
# def handle_email_removed(request, user, email_address, **kwargs):
#     send_mail(
#         'Email Removed Notification',
#         'An email address has been removed from your account.',
#         settings.DEFAULT_FROM_EMAIL,
#         [email_address.email],
#     )

