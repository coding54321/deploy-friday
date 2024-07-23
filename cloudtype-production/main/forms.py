from django import forms
from django.contrib.auth import get_user_model
from allauth.account.forms import LoginForm

User = get_user_model()

class UserSignupForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(), label="비밀번호")
    password2 = forms.CharField(widget=forms.PasswordInput(), label="비밀번호 확인")

    class Meta:
        model = User
        fields = ['name', 'user_id', 'telephone']
        labels = {
            'name': "이름",
            'user_id':"아이디",
            'telephone':'전화번호',
            
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 != password2:
            self.add_error('password2', '비밀번호가 일치하지 않습니다.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

    def try_save(self, request, commit=True):
        try:
            user = self.save(commit=commit)
            return user, None  # 두 개의 값을 반환
        except Exception as e:
            print(f"An error occurred: {e}")
            return None, self.get_invalid_response(request)

class CustomLoginForm(LoginForm):
    login = forms.CharField(
        label="아이디",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '아이디'}),
    )
    password = forms.CharField(
        label="비밀번호",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '비밀번호'}),
    )

class SocialSignupForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'telephone']