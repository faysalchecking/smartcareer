from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile

class UserSerializer(serializers.ModelSerializer):
    """Serialize user information"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']

class UserProfileSerializer(serializers.ModelSerializer):
    """Serialize user profile with user details"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['user', 'role', 'phone', 'address', 'is_active']

class LoginSerializer(serializers.Serializer):
    """Validate login credentials. Accepts email and password."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, data):
        email = data['email'].strip().lower()
        password = data['password']

        candidates = User.objects.filter(email__iexact=email)
        if candidates.count() != 1:
            # Zero or several matches are treated the same way, so the response
            # does not reveal which emails exist.
            raise serializers.ValidationError('Invalid email or password.')

        user = authenticate(username=candidates.get().username, password=password)
        if user is None or not user.is_active:
            raise serializers.ValidationError('Invalid email or password.')

        data['user'] = user
        return data

class LoginResponseSerializer(serializers.Serializer):
    """Response serializer for login"""
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    user = UserSerializer()

class MeSerializer(serializers.Serializer):
    """Response serializer for current user"""
    user = UserSerializer()
    role = serializers.CharField()
    phone = serializers.CharField()
    address = serializers.CharField()