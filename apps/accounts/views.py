from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib.auth.views import LoginView as AuthLoginView, LogoutView as AuthLogoutView, PasswordChangeView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.views.generic.edit import FormView, UpdateView
from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import CustomUser, Role
from .serializers import UserSerializer
from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm,
    CustomPasswordChangeForm, CustomPasswordResetForm, CustomSetPasswordForm, RoleForm
)

class TemplateLoginView(AuthLoginView):
    template_name = 'login.html'
    form_class = CustomAuthenticationForm
    success_url = reverse_lazy('dashboard')

class TemplateRegisterView(FormView):
    template_name = 'register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

class LoginView(TokenObtainPairView):
    pass

class LogoutView(AuthLogoutView):
    next_page = reverse_lazy('login')

# API View for user profile
class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

# Template Views for User Profile
class UserProfileView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'accounts/profile.html'
    context_object_name = 'user'
    
    def get_object(self):
        return self.request.user

class UserProfileEditView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully')
        return super().form_valid(form)

# Password Management Views
class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('password_change_done')

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

# Role-Based Access Control Views
class RoleListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Role
    template_name = 'accounts/role_list.html'
    context_object_name = 'roles'
    permission_required = 'accounts.manage_users'

class RoleCreateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Role
    form_class = RoleForm
    template_name = 'accounts/role_form.html'
    success_url = reverse_lazy('role_list')
    permission_required = 'accounts.manage_users'
    
    def form_valid(self, form):
        messages.success(self.request, 'Role created successfully')
        return super().form_valid(form)

class RoleUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Role
    form_class = RoleForm
    template_name = 'accounts/role_form.html'
    success_url = reverse_lazy('role_list')
    permission_required = 'accounts.manage_users'
    
    def form_valid(self, form):
        messages.success(self.request, 'Role updated successfully')
        return super().form_valid(form)