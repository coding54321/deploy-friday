# main/adapters.py

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import redirect
from allauth.core.exceptions import ImmediateHttpResponse
from main.models import User  # 사용자 모델을 import

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
        return user
