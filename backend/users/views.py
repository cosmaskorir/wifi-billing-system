# Assuming you use a custom view for registration
from rest_framework import generics, permissions
from .serializers import UserRegistrationSerializer, UserSerializer
from .models import User

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = (permissions.AllowAny,) # Allow unauthenticated registration

class CurrentUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # The object is always the currently logged-in user
        return self.request.user