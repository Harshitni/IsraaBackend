from rest_framework import serializers
from .models import AuthUsers
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUsers
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            try:
                user = AuthUsers.objects.get(email=email)
            except AuthUsers.DoesNotExist:
                raise serializers.ValidationError("Invalid email or password")

            # Authenticate using username fetched from the user instance
            user = authenticate(username=user.username, password=password)
            if not user:
                raise serializers.ValidationError("Invalid email or password")

            if not user.is_active:
                raise serializers.ValidationError("User is inactive")

            tokens = RefreshToken.for_user(user)
            return {
                "access": str(tokens.access_token),
                "refresh": str(tokens),
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                }
            }

        raise serializers.ValidationError("Both email and password are required")
