"""
Django settings for ISP Management System.
"""
from pathlib import Path
from datetime import timedelta
import os
import dj_database_url
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ==============================================
# 2. CORE SECURITY SETTINGS
# ==============================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-key-change-this-in-prod')

# SECURITY WARNING: don't run with debug turned on in production!
# We default to True for dev, but Render sets this to False automatically
DEBUG = 'RENDER' not in os.environ

# Allowed Hosts: '*' allows Render/Vercel to host the app
ALLOWED_HOSTS = ['*']


# ==============================================
# 3. INSTALLED APPS
# ==============================================

INSTALLED_APPS = [
    # --- Modern Admin Interface (Unfold) ---
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",

    # --- Standard Django Apps ---
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # --- Third-Party Libraries ---
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',               # Handles React <-> Django communication
    'django_rest_passwordreset', # Handles Forgot Password logic

    # --- Local Project Apps ---
    'users.apps.UsersConfig',
    'plans.apps.PlansConfig',
    'billing.apps.BillingConfig',
    'mpesa.apps.MpesaConfig',
    'dashboard.apps.DashboardConfig',
    'routers.apps.RoutersConfig'
]


# ==============================================
# 4. MIDDLEWARE
# ==============================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    
    # --- WhiteNoise: Serves Static Files (CSS/Images) in Production ---
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', # Must be before CommonMiddleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# ==============================================
# 5. DATABASE (Auto-Switching)
# ==============================================

# Use SQLite locally, but switch to PostgreSQL if DATABASE_URL is found (Render)
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}


# ==============================================
# 6. AUTHENTICATION & USER MODEL
# ==============================================

AUTH_USER_MODEL = 'users.User'

AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# ==============================================
# 7. API & JWT SETTINGS
# ==============================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}


# ==============================================
# 8. INTERNATIONALIZATION
# ==============================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True


# ==============================================
# 9. STATIC FILES (CSS, JS, Images)
# ==============================================

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles' # Folder where Render collects files

# WhiteNoise Storage: Compresses and caches static files for speed
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# ==============================================
# 10. CORS (Frontend Access)
# ==============================================

CORS_ALLOW_ALL_ORIGINS = True 


# ==============================================
# 11. MODERN ADMIN CONFIG (Django-Unfold)
# ==============================================

UNFOLD = {
    "SITE_TITLE": "ISP Management",
    "SITE_HEADER": "WiFi Admin Dashboard",
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Main Management",
                "separator": True,
                "items": [
                    {
                        "title": "Users & Customers",
                        "icon": "people",
                        "link": "/admin/users/user/",
                    },
                    {
                        "title": "WiFi Packages",
                        "icon": "router",
                        "link": "/admin/plans/wifipackage/",
                    },
                    {
                        "title": "Subscriptions",
                        "icon": "subscriptions",
                        "link": "/admin/billing/subscription/",
                    },
                    {
                        "title": "Payments",
                        "icon": "attach_money",
                        "link": "/admin/billing/payment/",
                    },
                ],
            },
        ],
    },
}


# ==============================================
# 12. M-PESA & CELERY CONFIG
# ==============================================

# M-Pesa (Safaricom Daraja)
MPESA_CONSUMER_KEY = os.getenv('MPESA_CONSUMER_KEY')
MPESA_CONSUMER_SECRET = os.getenv('MPESA_CONSUMER_SECRET')
MPESA_PASSKEY = os.getenv('MPESA_PASSKEY')
MPESA_SHORTCODE = os.getenv('MPESA_SHORTCODE', '174379')
MPESA_CALLBACK_URL = os.getenv('MPESA_CALLBACK_URL')

# Celery (Background Tasks - Redis)
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_TIMEZONE = TIME_ZONE


# ==============================================
# 13. EMAIL CONFIGURATION (Gmail)
# ==============================================
# ⚠️ ACTION REQUIRED: REPLACE THESE WITH YOUR REAL DETAILS ⚠️

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# 1. Your Gmail Address
EMAIL_HOST_USER = 'your-real-email@gmail.com' 

# 2. Your App Password (NOT your login password)
# Get this from Google Account -> Security -> 2-Step Verification -> App Passwords
EMAIL_HOST_PASSWORD = 'xxxx xxxx xxxx xxxx' 

DEFAULT_FROM_EMAIL = f'ISP Support <{EMAIL_HOST_USER}>'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'