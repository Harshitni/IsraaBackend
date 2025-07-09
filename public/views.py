from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import UserPreference
from .serializers import UserPreferenceSerializer

class UserPreferenceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            preference = UserPreference.objects.get(user=request.user)
            serializer = UserPreferenceSerializer(preference)
            return Response(serializer.data)
        
        except UserPreference.DoesNotExist:
            return Response(None, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            preference = UserPreference.objects.get(user=request.user)
            serializer = UserPreferenceSerializer(preference, data=request.data, partial=True)

        except UserPreference.DoesNotExist:
            serializer = UserPreferenceSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
