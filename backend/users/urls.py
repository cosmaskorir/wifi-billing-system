# backend/users/urls.py

from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.views.decorators.csrf import csrf_exempt 
from .views import UserRegistrationView, CurrentUserView 

urlpatterns = [
    # 1. JWT Login - MUST BE WRAPPED
    path('login/', csrf_exempt(TokenObtainPairView.as_view()), name='token_obtain_pair'),
    
    # 2. User Registration - MUST BE WRAPPED (The Fix)
    path('register/', csrf_exempt(UserRegistrationView.as_view()), name='user-register'), 
    
    # 3. JWT Token Refresh
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # 4. User Details
    path('me/', CurrentUserView.as_view(), name='current-user-details'),

    # 5. Password Reset 
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
]