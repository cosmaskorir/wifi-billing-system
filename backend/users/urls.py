from django.urls import path
from .views import RegisterView, UserProfileView

urlpatterns = [
    # Endpoint: /api/users/register/
    path('register/', RegisterView.as_view(), name='register'),
    
    # Endpoint: /api/users/profile/
    path('profile/', UserProfileView.as_view(), name='profile'),
]