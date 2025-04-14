from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from .models import User
from django.contrib.auth import authenticate


class RegisterForm(forms.Form):
    phone_number = forms.CharField(
        label="شماره تلفن",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'شماره تلفن خود را وارد کنید'}),
        validators=[RegexValidator(r'^09\d{9}$', 'شماره تلفن معتبر نیست')],
        required=True
    )
    
class UserRegistrationForm(forms.Form):
    username = forms.CharField(max_length=100, required=True, label="نام کاربری")
    password = forms.CharField(widget=forms.PasswordInput, required=True, label="پسورد")
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=True, label="تأیید پسورد")
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password != password_confirm:
            raise ValidationError("پسوردها با یکدیگر مطابقت ندارند.")
        
        return cleaned_data

class MobileLoginForm(forms.Form):
    mobile = forms.CharField(
        label="شماره موبایل",
        max_length=11,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^09\d{9}$',
                message=".شماره موبایل باید با 09 شروع شود"
            )
        ],
        widget=forms.NumberInput(attrs={
            'pattern': '09\d{9}',
            'title': '.شماره باید با 09 شروع شود',
            'inputmode': 'numeric'
        })
    )
    
    password = forms.CharField(
        label="رمز عبور", 
        widget=forms.PasswordInput,
        required=True
    )

    def clean_mobile(self):
        mobile = self.cleaned_data['mobile']
        if not User.objects.filter(mobile=mobile).exists():
            raise forms.ValidationError("این شماره ثبت نشده است!")
        return mobile

class ForgetPasswordForm(forms.Form):
    mobile = forms.CharField(label="شماره موبایل", max_length=20, required=True)

    def clean_mobile(self):
        mobile = self.cleaned_data.get("mobile")
        if not User.objects.filter(mobile=mobile).exists():
            raise forms.ValidationError("این شماره در سیستم ثبت نشده است!")
        return mobile


class ResetPasswordForm(forms.Form):
    password = forms.CharField(
        label='کلمه عبور',
        widget=forms.PasswordInput(),
        validators=[
            validators.MaxLengthValidator(100),
        ]
    )

    confirm_password = forms.CharField(
        label='تکرار کلمه عبور',
        widget=forms.PasswordInput(),
        validators=[
            validators.MaxLengthValidator(100),
        ]
    )
