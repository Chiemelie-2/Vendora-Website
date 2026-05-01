from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import resolve_url

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_connect_redirect_url(self, request, socialaccount):
        return resolve_url('accounts:signup_profile')

    def get_login_redirect_url(self, request):
        # This sends Google users to Step 3 (Role Selection)
        return reverse('accounts:signup_profile')
