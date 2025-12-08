from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Function to redirect root URL to dashboard
def root_redirect(request):
    return redirect('/api/dashboard/')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Redirect homepage to dashboard
    path('', root_redirect, name='root'),

    # --- JWT AUTHENTICATION ENDPOINTS ---
    # This is the critical fix. It exposes the correct login API for React.
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # --- APP ENDPOINTS ---
    path('api/users/', include('users.urls')),
    path('api/plans/', include('plans.urls')),
    path('api/billing/', include('billing.urls')),
    path('api/mpesa/', include('mpesa.urls')),
    path('api/dashboard/', include('dashboard.urls')),
]