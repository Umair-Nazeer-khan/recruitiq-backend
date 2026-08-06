# fairhire/apps/auth_app/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import HRUser


class RegisterSerializer(serializers.ModelSerializer):
    """
    Used by Flutter Register screen.
    POST /api/v1/auth/register/
    Body: { name, email, password }
    """
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model  = HRUser
        fields = ['id', 'name', 'email', 'password', 'role']
        extra_kwargs = {'role': {'read_only': True}}

    def create(self, validated_data):
        return HRUser.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """
    Used by Flutter Login screen.
    POST /api/v1/auth/login/
    Body: { email, password, fcm_token (optional) }
    """
    email     = serializers.EmailField()
    password  = serializers.CharField(write_only=True)
    fcm_token = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid email or password.')
        if not user.is_active:
            raise serializers.ValidationError('Account is disabled.')
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    """Returns user profile data."""
    class Meta:
        model  = HRUser
        fields = ['id', 'name', 'email', 'role', 'created_at']
