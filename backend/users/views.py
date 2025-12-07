from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    Endpoint for new users to register.
    Public access.
    """
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Endpoint for users to view or update their own profile.
    Requires Authentication (JWT).
    """
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        # Returns the currently logged-in user
        return self.request.user