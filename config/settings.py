import os
from pathlib import Path
from environ import Env
from datetime import timedelta
from PIL import ImageFile
import dj_database_url

import pymysql
pymysql.install_as_MySQLdb()

env = Env()
Env.read_env()
ENVIRONMENT = env('ENVIRONMENT', default='production')

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env('SECRET_KEY')

if ENVIRONMENT == 'development':
    DEBUG = True
else:
    DEBUG = False

INTERNAL_IPS = (
    '127.0.0.1',
    'localhost.8000',
    '192.168.1.2'
)

SIDE_ID = 3

INSTALLED_APPS = [
    # 'multi_captcha_admin',
    'admin_interface',
    'colorfield',
    'debug_toolbar', #remove this during production
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    # 'django.contrib.sessions', replaced by qsessions
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'qsessions',
    'corsheaders',
    'djoser',
    'templates',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.microsoft',
    # 'django.contrib.humanize',
    # 'allauth.usersessions',
    'django_otp',
    # 'django_otp.plugins.otp_totp',
    # 'django_otp.plugins.otp_static',
    'allauth_2fa',
    'django_otp.plugins.otp_email',
    'two_factor',
    # 'two_factor.plugins.phonenumber',
    # 'two_factor.plugins.email',
    'crispy_forms',
    'django_browser_reload',
    'static',
    'tinymce',
    'compressor',
    'apps.curriculum',
    'apps.dashboard',
    'apps.user',
    'apps.timetable',
    'apps.institutes',
    'apps.programs',
    'apps.faculty',
    'apps.algorithm',
    'rest_framework',
    'rest_framework.authtoken',
    'django_celery_results',
    'channels',
]

# MULTI_CAPTCHA_ADMIN = {
#     'engine': 'recaptcha2',
# }

# RECAPTCHA_PRIVATE_KEY = env('RECAPTCHA_PRIVATE_KEY')
# RECAPTCHA_PUBLIC_KEY = env('RECAPTCHA_PUBLIC_KEY')

# social account providers
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE":[
            "profile",
            "email"
        ],
        "AUTH_PARAMS": {"access_type": "online"}
    }
}

CORS_ALLOWED_ORIGINS = [
    'http://localhost:8080',
    'https://fonts.googleapis.com',
    'https://fonts.gstatic.com',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # 'django.contrib.sessions.middleware.SessionMiddleware', replaced by qsessions
    'qsessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
     'allauth_2fa.middleware.AllauthTwoFactorMiddleware',
    #  'allauth.usersessions.middleware.UserSessionsMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django_browser_reload.middleware.BrowserReloadMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django_auto_logout.middleware.auto_logout',
    'django.middleware.locale.LocaleMiddleware',    
]
APPEND_SLASH = True
ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            str(BASE_DIR / 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django_auto_logout.context_processors.auto_logout_client',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': env('ENGINE'),
        'NAME': env('NAME'),
        'USER': env('USER'),
        'PASSWORD': env('PASSWORD'),
        'HOST': env('HOST'), 
        'PORT': env('PORT'),
        'OPTIONS': {
            'sql_mode': 'STRICT_TRANS_TABLES',
        },
    }
}

DATABASES["default"] = dj_database_url.parse(env('DATABASE_URL'))

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Manila'

USE_I18N = True

USE_TZ = True
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_URL='/media/'
MEDIA_ROOT = BASE_DIR /'media'

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATIC_ROOT = BASE_DIR / 'staticfiles'

COMPRESS_URL = STATIC_URL
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_ENABLED = True
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend"
)
AUTO_LOGOUT = {
    'IDLE_TIME': timedelta(minutes=30),
    'MESSAGE': 'The session has expired. Please login again to continue.',
    'REDIRECT_TO_LOGIN_IMMEDIATELY': True,
}
AUTH_USER_MODEL = 'user.User'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_ADAPTER = 'apps.user.common.account_adapters.UserAccountAdapter'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ALLOWED_HOSTS = ["*"]
ACCOUNT_FORMS = {
    'signup': 'apps.user.forms.SignupForm',
    'change_password': 'apps.user.forms.RequestPasswordChangeForm',
}
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True
ACCOUNT_CHANGE_EMAIL = False
ACCOUNT_CONFIRM_EMAIL_ON_GET = False
ACCOUNT_EMAIL_CONFIRMATION_HMAC = True
ACCOUNT_EMAIL_NOTIFICATIONS = True

ACCOUNT_RATE_LIMITS = {
    "reset_password": "3/d/key",
    "confirm_email": "1/30m/key",
    "login_failed": "3/1h/ip",
    "reset_password_from_key" : "3/30m/ip",
    "manage_email" : "10/m/user",
    "change_password": "3/1w/user",
    "reauthenticate": "10/m/user",
    "signup": "20/m/ip",
    "login": "30/m/ip",
    
}
ACCOUNT_LOGIN_BY_CODE_ENABLED = False
ACCOUNT_LOGIN_BY_CODE_MAX_ATTEMPTS = 3
ACCOUNT_LOGIN_BY_CODE_TIMEOUT = 180
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = False
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = '/accounts/login/'

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = 'DNSC AcadSked <noreply@dnsc.edu.ph>'

ACCOUNT_EMAIL_TEMPLATE_EXTENSION = 'html'
SESSION_ENGINE = 'qsessions.backends.db'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEOIP_PATH = os.path.join(BASE_DIR, 'geoip', 'GeoLite2-City.mmdb')

# OTP Token Expiration
OTP_EMAIL_TOKEN_VALIDITY = 120
OTP_EMAIL_SUBJECT = 'OTP Token'
# OTP_EMAIL_BODY_TEMPLATE=None
# OTP_EMAIL_BODY_HTML_TEMPLATE_PATH=None
# OTP_EMAIL_BODY_TEMPLATE_PATH=None
# OTP_EMAIL_BODY_HTML_TEMPLATE_PATH=None
# OTP_EMAIL_COOLDOWN_DURATION=60
# OTP_EMAIL_THROTTLE_FACTOR=0

ImageFile.LOAD_TRUNCATED_IMAGES = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ]
}

API_BASE_URL = 'http://127.0.0.1:8000'

# Celery Configuration Options
# if ENVIRONMENT == 'development':
#   CELERY_BROKER_URL = 'redis://localhost:6379/0'
# else:
#   CELERY_BROKER_URL = env('CELERY_BROKER_URL')
CELERY_BROKER_URL = 'redis://localhost:6379/0'
# CELERY_BROKER_URL = env('CELERY_BROKER_URL')
ACCEPT_CONTENT = ['application/json']
RESULT_SERIALIZER = 'json'
TASK_SERIALIZER = 'json'
CELERY_ENABLE_UTC = True
TIMEZONE = 'Asia/Manila'
CELERY_BACKEND = 'django-db'
RESULT_BACKEND = 'django-db'
# if ENVIRONMENT == 'development':
#   CELERY_TASK_ALWAYS_EAGER = True
# else:
#   CELERY_TASK_TRACK_STARTED = False
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

ASGI_APPLICATION = 'config.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
STATICSTORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'