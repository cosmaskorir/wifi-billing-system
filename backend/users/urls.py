from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RegisterView

router = DefaultRouter()
router.register(r'user', UserViewSet)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    
    # Add this line for password reset:
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    
    path('', include(router.urls)),
]