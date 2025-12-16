import os
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
# REPLACE WITH YOUR ACTUAL KEY
SECRET_KEY = 'django-insecure-@1t3-h@#h2r&y%7_8m0m-0c8-!k^2q*n#^t!&i3!z+p28p#0v9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Add your local and production domain names here
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']


# Application definition

INSTALLED_APPS = [
    # --- UNFOLD THEME (Must be first!) ---
    'unfold',
    
    # Core Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-Party Apps
    'rest_framework',
    'rest_framework_simplejwt', 
    'corsheaders',              
    'django_rest_passwordreset', # FIX: Added this for password reset functionality

    # Local Apps
    'users.apps.UsersConfig',
    'plans.apps.PlansConfig',
    'billing.apps.BillingConfig',
    'mpesa.apps.MpesaConfig',
    'routers.apps.RoutersConfig',
    'support.apps.SupportConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
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


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation (default)
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.User'


# ====================================================================
# --- UNFOLD THEME CONFIGURATION (For Admin Sidebar) ---
# ====================================================================

UNFOLD = {
    "SITE_TITLE": "ISP Customer Portal Admin",
    "SITE_HEADER": "ISP Network Control",
    
    # Points to the custom grouping logic we created in unfold_callbacks.py
    "DASHBOARD_CALLBACK": "config.unfold_callbacks.custom_dashboard_callback", 
    
    # Defines the order of groups on the sidebar
    "EXTENSIONS": {
        "model_admin": {
            "ordering": (
                "BILLING", 
                "SUPPORT", 
                "NETWORK",
                "AUTHENTICATION_AND_AUTHORIZATION",
                "ROUTERS", 
            )
        }
    }
}

# ====================================================================
# --- CORS & CSRF SECURITY FIXES ---
# ====================================================================

# 1. CORS Allowed Origins (Must include the URL where your React app is running)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_ALL_ORIGINS = False 

# 2. CSRF Trusted Origins (Required for POST/PUT requests from the frontend)
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# ====================================================================
# --- REST FRAMEWORK / JWT SETTINGS ---
# ====================================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# ====================================================================
# --- MPESA CONFIGURATION ---
# ====================================================================

# Replace these placeholder values with your actual Safaricom/Daraja API credentials
MPESA_CONSUMER_KEY = os.environ.get('MPESA_CONSUMER_KEY', 'your_consumer_key')
MPESA_CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET', 'your_consumer_secret')
MPESA_SHORTCODE = os.environ.get('MPESA_SHORTCODE', '174379')
MPESA_PASSKEY = os.environ.get('MPESA_PASSKEY', 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919') 
MPESA_CALLBACK_URL = os.environ.get('MPESA_CALLBACK_URL', 'https://your-public-ngrok-url/api/mpesa/callback/') 


# ====================================================================
# --- AFRICA'S TALKING SMS CONFIGURATION (Optional) ---
# ====================================================================

AT_USERNAME = os.environ.get('AT_USERNAME', 'sandbox') 
AT_API_KEY = os.environ.get('AT_API_KEY', 'YOUR_AFRICAS_TALKING_API_KEY') 
AT_SENDER_ID = os.environ.get('AT_SENDER_ID', 'AFRICASTKNG') 

# ====================================================================
# --- EMAIL SETTINGS (For Password Reset) ---
# ====================================================================

# Use console backend for development (prints email to terminal)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'