from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from allauth.socialaccount.models import SocialAccount
from django.urls import reverse

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # If the user is already authenticated, don't do anything
        if request.user.is_authenticated:
            return

        # If social account already exists, link to the existing user and login
        try:
            account = SocialAccount.objects.get(provider=sociallogin.account.provider, uid=sociallogin.account.uid)
            user = account.user
            # If the user already exists, redirect to home
            if user:
                raise ImmediateHttpResponse(redirect(reverse('home')))
        except SocialAccount.DoesNotExist:
            pass

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        return user
