from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from django.shortcuts import redirect

@receiver(user_signed_up)
def social_signup_redirect(request, user, **kwargs):
    # Check if this is a social login (Google)
    if hasattr(user, 'socialaccount_set'):
        # Store a flag in session so we know they need to pick a role
        request.session['social_signup_pending'] = True
        # We don't return a redirect here; allauth uses SOCIALACCOUNT_ADAPTER
