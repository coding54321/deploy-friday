from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import redirect
from django.urls import reverse

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        if sociallogin.is_existing:
            return redirect(reverse('home'))

    def save_user(self, request, sociallogin, form=None):
        user = sociallogin.user
        if not user.pk:
            user.name = request.POST.get('name', '')
            user.telephone = request.POST.get('phone', '')
            user.save()
        return user
