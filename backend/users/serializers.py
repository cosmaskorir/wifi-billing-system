from rest_framework import serializers
from .models import User 
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
import re # Import the regular expression module
from django.db import IntegrityError

# --- 1. Registration Serializer ---
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'password')
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'phone_number': {'required': True},
        }

    def validate_phone_number(self, value):
        # 1. Strip spaces and non-digit characters for cleaning
        clean_number = re.sub(r'\D', '', value)

        # 2. Enforce 254 format:
        if clean_number.startswith('0'):
            # Change 07... to 2547...
            clean_number = '254' + clean_number[1:]
        
        # 3. Check if the final number matches the expected international length and format
        if not re.match(r'^2547\d{8}$', clean_number):
            raise serializers.ValidationError(
                "Phone number must be a valid Kenyan mobile number in the format 2547xxxxxxx or 07xxxxxxxxx."
            )
        
        # 4. Check for uniqueness before passing to the model save
        if User.objects.filter(phone_number=clean_number).exists():
             raise serializers.ValidationError(
                "This phone number is already registered."
            )

        return clean_number

    def validate_password(self, value):
        try:
            password_validation.validate_password(value, self.instance)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def create(self, validated_data):
        # Use .create_user to ensure the password is hashed correctly
        try:
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                phone_number=validated_data['phone_number'], 
                password=validated_data['password']
            )
            return user
        except IntegrityError:
             # Should be caught by validate_phone_number, but kept for robustness
             raise serializers.ValidationError({"phone_number": "This phone number is already registered."})

# --- 2. User/Profile Detail Serializer (The missing part) ---
class UserSerializer(serializers.ModelSerializer):
    """
    Serializer used for displaying or updating user profile details (e.g., in /api/auth/me/).
    """
    class Meta:
        model = User
        # Include all necessary fields, excluding the password
        fields = ('id', 'username', 'email', 'phone_number', 'first_name', 'last_name', 'is_active')
        read_only_fields = ('username', 'is_active')