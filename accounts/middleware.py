from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages

class BlockedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the user is authenticated and blocked
        if request.user.is_authenticated and hasattr(request.user, 'is_blocked') and request.user.is_blocked:
            logout(request)
            messages.error(request, "Your account has been blocked by the admin.")
            return redirect('accounts:login')  # Redirect to login page 

        response = self.get_response(request)
        return response
