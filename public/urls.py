from django.urls import path
from .views import UserPreferenceView

urlpatterns = [
    path('user_preferences/', UserPreferenceView.as_view(), name='user_preferences'),
]
