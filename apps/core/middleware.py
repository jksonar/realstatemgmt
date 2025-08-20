import logging

class UserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)

    def __call__(self, request):
        if request.user.is_authenticated:
            self.logger.info(f'User {request.user.username} accessed {request.path}')
        response = self.get_response(request)
        return response
