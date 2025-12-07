from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

# Get the custom user model defined in settings.AUTH_USER_MODEL
User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new customer.
    Enforces password validation and hashing.
    """
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True, 
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'password', 'password_confirm', 'location')
        extra_kwargs = {
            'email': {'required': True}
        }

    def validate(self, attrs):
        # Check if passwords match
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        # Remove password_confirm as it's not a model field
        validated_data.pop('password_confirm')
        
        # specific logic to handle password hashing
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            phone_number=validated_data['phone_number'],
            location=validated_data.get('location', ''),
            password=validated_data['password']
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for viewing user profiles.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone_number', 'role', 'location', 'date_joined')
        read_only_fields = ('id', 'role', 'date_joined')