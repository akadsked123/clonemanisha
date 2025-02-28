from allauth_2fa.adapter import OTPAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.core.exceptions import ValidationError

class UserAccountAdapter(DefaultAccountAdapter):
    def clean_email(self, email):
        if not email.endswith('@dnsc.edu.ph'):
            raise ValidationError("Invalid email address. Only DNSC email accounts are allowed.")
        return super().clean_email(email)
    pass

class CustomAccountAdapter(OTPAdapter, UserAccountAdapter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_email(self, email):
        return UserAccountAdapter.clean_email(self, email)

    def get_login_redirect_url(self, request):
        otp_url = OTPAdapter.get_login_redirect_url(self, request)
        user_url = UserAccountAdapter.get_login_redirect_url(self, request)
        return otp_url or user_url
