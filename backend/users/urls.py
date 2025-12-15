from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RegisterView

app_name = 'users'

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'user', UserViewSet)  # This creates /api/users/user/

urlpatterns = [
    # Public Endpoint: Customers use this to sign up
    path('register/', RegisterView.as_view(), name='register'),

    # Admin Endpoints: Router handles /user/ listing and editing
    path('', include(router.urls)),
]