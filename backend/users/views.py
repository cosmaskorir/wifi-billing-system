from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

# Get the custom User model
User = get_user_model()

# ============================================
# 1. SERIALIZERS (Data Validation & Formatting)
# ============================================

class UserSerializer(ModelSerializer):
    """
    Standard serializer for viewing/editing users in the Dashboard.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'is_active', 'date_joined']
        read_only_fields = ['date_joined']


class RegisterSerializer(ModelSerializer):
    """
    Special serializer for Registration that handles Password Hashing.
    """
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'phone_number')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Create a new user instance
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            phone_number=validated_data.get('phone_number', '')
        )
        return user


# ============================================
# 2. VIEWS (API Endpoints)
# ============================================

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Admins to view and edit users.
    Endpoint: /api/users/user/
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]  # Only logged-in users can see this


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for public sign-ups.
    Endpoint: /api/users/register/
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]  # Anyone can access this (no login required)
    serializer_class = RegisterSerializer