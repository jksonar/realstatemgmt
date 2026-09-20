import logging
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

class UserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)

    def __call__(self, request):
        if request.user.is_authenticated:
            self.logger.info(f'User {request.user.username} accessed {request.path}')
        response = self.get_response(request)
        return response

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # URLs that don't require authentication
        exempt_urls = [
            settings.LOGIN_URL,
            '/accounts/register/',
            '/admin/',
            '/accounts/password_reset/',
            '/accounts/password_reset/done/',
            '/accounts/reset/',
            '/accounts/reset/done/',
            '/static/',
            '/media/',
        ]
        
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            # Allow access to exempt URLs
            if not any(request.path.startswith(url) for url in exempt_urls):
                return redirect(settings.LOGIN_URL)
        
        response = self.get_response(request)
        return response
