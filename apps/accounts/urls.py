from django.urls import path
from .views import (
    TemplateRegisterView,
    TemplateLoginView,
    LogoutView,
    UserProfileView,
    RegisterView,
    LoginView,
)

urlpatterns = [
    path('register/', TemplateRegisterView.as_view(), name='register'),
    path('login/', TemplateLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    # API routes
    path('api/register/', RegisterView.as_view(), name='api-register'),
    path('api/login/', LoginView.as_view(), name='api-login'),
]
