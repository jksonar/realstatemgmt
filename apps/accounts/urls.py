from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    TemplateRegisterView,
    TemplateLoginView,
    LogoutView,
    UserProfileView,
    UserProfileEditView,
    CustomPasswordChangeView,
    CustomPasswordResetView,
    CustomPasswordResetConfirmView,
    RoleListView,
    RoleCreateView,
    RoleUpdateView,
    RegisterView,
    LoginView,
    UserProfileAPIView,
)

urlpatterns = [
    # Authentication URLs
    path('login/', TemplateLoginView.as_view(), name='login'),
    path('register/', TemplateRegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Profile URLs
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/edit/', UserProfileEditView.as_view(), name='profile_edit'),
    
    # Password Management URLs
    path('password/change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password/change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
    path('password/reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password/reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('password/reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password/reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    
    # Role Management URLs
    path('roles/', RoleListView.as_view(), name='role_list'),
    path('roles/add/', RoleCreateView.as_view(), name='role_add'),
    path('roles/<int:pk>/edit/', RoleUpdateView.as_view(), name='role_edit'),
    
    # API URLs
    path('api/register/', RegisterView.as_view(), name='api-register'),
    path('api/login/', LoginView.as_view(), name='api-login'),
    path('api/profile/', UserProfileAPIView.as_view(), name='api-profile'),
]
