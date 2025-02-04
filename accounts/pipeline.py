from accounts.models import *
from social_core.pipeline.partial import partial
from django.contrib import messages

@partial
def save_user_details(strategy, details, user=None, *args, **kwargs):
    if user:
        return {'is_new': False}

    email = details.get('email')
    first_name = details.get('first_name', 'User')  # Default to 'User'
    last_name = details.get('last_name', '')        # Default to empty

    if not email:
        return strategy.redirect('accounts:login')  # Redirect if email is missing

    user = Accounts.objects.create_user(
        email=email,
        first_name=first_name,
        last_name=last_name,
    )

    return {
        'is_new': True,
        'user': user
    }


def activate_user(user, *args, **kwargs):
    user.is_active = True
    user.save()

def check_if_user_blocked(strategy, user, *args, **kwargs):
    if user.is_blocked:
        # Add an error message
        messages.error(strategy.request, "Your account is blocked. Please contact support.")
        return strategy.redirect('accounts:home')  # Redirect to an error page for blocked users

    return {
        'is_blocked': False,
        'user': user
    }