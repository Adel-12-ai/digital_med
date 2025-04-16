from django import forms

from .models import SMSVerification, Appointment
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


# Форма для приема к врачу
from django import forms
from .models import Appointment

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['clinic', 'doctor', 'service', 'date', 'time', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Опишите симптомы или особые пожелания...'}),
        }



