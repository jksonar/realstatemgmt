from django.urls import path, include
from .views import RegisterView, LoginView, UserProfileView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('password_reset/', include('django.contrib.auth.urls')),
    path('profile/', UserProfileView.as_view(), name='profile'),
]
