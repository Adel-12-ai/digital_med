from django import forms

from .models import SMSVerification
from django.contrib.auth import get_user_model


User = get_user_model()


class SignUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('Email обязателен!')
        return email


class VerificationUserForm(forms.ModelForm):
    class Meta:
        model = SMSVerification
        fields = ['email', 'code']

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        code = cleaned_data.get('code')

        if not email or not code:
            raise forms.ValidationError('Email и код подтверждения обязательны!')
        return cleaned_data


