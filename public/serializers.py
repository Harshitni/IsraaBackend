from rest_framework import serializers
from .models import UserPreference
from django.utils import timezone

class UserPreferenceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UserPreference
        exclude = ['created_at', 'updated_at', 'user']

    def create(self, validated_data):
        validated_data['created_at'] = timezone.now()
        validated_data['updated_at'] = timezone.now()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['updated_at'] = timezone.now()
        return super().update(instance, validated_data)

