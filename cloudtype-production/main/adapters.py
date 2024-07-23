from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import render, redirect
from django.urls import reverse
from allauth.exceptions import ImmediateHttpResponse
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        if sociallogin.is_existing:
            return

        user = sociallogin.user
        if not user.email:
            return

        try:
            existing_user = User.objects.get(email=user.email)
            sociallogin.connect(request, existing_user)
        except User.DoesNotExist:
            pass

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        user.save()

        if not sociallogin.is_existing:
            raise ImmediateHttpResponse(render(request, 'social_signup.html', {'form': SocialSignupForm()}))

        return user
