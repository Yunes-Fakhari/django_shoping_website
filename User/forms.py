from django import forms
from account.models import User
from django.core import validators
from django.core.exceptions import ValidationError
# forms.py
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import User
import re
# forms.py
from django import forms
import re
from iranian_cities.fields import Province as OstanField , County as ShahrestanField
# لیست ثابت استان‌های ایران
IRAN_PROVINCES = [
    ("آذربایجان شرقی", "آذربایجان شرقی"),
    ("آذربایجان غربی", "آذربایجان غربی"),
    ("اردبیل", "اردبیل"),
    ("اصفهان", "اصفهان"),
    ("البرز", "البرز"),
    ("ایلام", "ایلام"),
    ("بوشهر", "بوشهر"),
    ("تهران", "تهران"),
    ("چهارمحال و بختیاری", "چهارمحال و بختیاری"),
    ("خراسان رضوی", "خراسان رضوی"),
    ("خراسان شمالی", "خراسان شمالی"),
    ("خراسان جنوبی", "خراسان جنوبی"),
    ("خوزستان", "خوزستان"),
    ("زنجان", "زنجان"),
    ("سمنان", "سمنان"),
    ("سیستان و بلوچستان", "سیستان و بلوچستان"),
    ("فارس", "فارس"),
    ("همدان", "همدان"),
    ("قزوین", "قزوین"),
    ("قم", "قم"),
    ("کردستان", "کردستان"),
    ("کرمان", "کرمان"),
    ("کرمانشاه", "کرمانشاه"),
    ("کهگیلویه و بویراحمد", "کهگیلویه و بویراحمد"),
    ("گلستان", "گلستان"),
    ("گیلان", "گیلان"),
    ("لرستان", "لرستان"),
    ("مرکزی", "مرکزی"),
    ("مازندران", "مازندران"),
    ("هرمزگان", "هرمزگان"),
    ("یزد", "یزد"),
]
class ProfileUpdateForm(forms.Form):
    fullname = forms.CharField(
        label=_("نام کامل"),
        max_length=255,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "id": "fullname",
            "placeholder": "نام کامل",
        })
    )
    email = forms.EmailField(
        label=_("ایمیل"),
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "id": "email",
            "placeholder": "ایمیل",
        })
    )
    mobile = forms.CharField(
        label=_("موبایل"),
        max_length=11,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "id": "mobile",
            "placeholder": "شماره موبایل",
        })
    )
    gender = forms.ChoiceField(
        label=_("جنسیت"),
        choices=[
            ("مرد", _("مرد")),
            ("زن", _("زن")),

        ],
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "gender"
        })
    )
    location = forms.ChoiceField(
        label=_("استان"),
        choices=IRAN_PROVINCES,
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "location"
        })
    )
    photo = forms.ImageField(
        label=_("عکس نمایه"),
        required=False,
        widget=forms.ClearableFileInput(attrs={
            "class": "form-control",
            "id": "photo",
            "accept": "application/pdf"
        })
    )
    address = forms.CharField(
        label=_("آدرس"),
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "id": "address",
            "placeholder": "آدرس",
        })
    )
    legendry_code = forms.CharField(
        label=_("کد ملی"),
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "id": "legendry_code",
            "placeholder": "کد ملی",
        })
    )
    post_code = forms.CharField(
        label=_("کد پستی"),
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "id": "post_code",
            "placeholder": "کد پستی",
        })
    )

    # اعتبارسنجی نام کامل: فقط حروف فارسی و فاصله مجاز هستند
    def clean_fullname(self):
        fullname = self.cleaned_data.get("fullname", "")
        if not re.match(r'^[\u0600-\u06FF\s]+$', fullname):
            raise forms.ValidationError(_("نام کامل باید به فارسی وارد شود."))
        return fullname

    # اعتبارسنجی شماره موبایل: باید فقط ارقام باشد، 11 رقمی و با '09' شروع شود
    def clean_mobile(self):
        mobile = self.cleaned_data.get("mobile", "")
        if not mobile.isdigit():
            raise forms.ValidationError(_("شماره موبایل باید تنها شامل ارقام باشد."))
        if len(mobile) != 11:
            raise forms.ValidationError(_("شماره موبایل باید 11 رقم باشد."))
        if not mobile.startswith("09"):
            raise forms.ValidationError(_("شماره موبایل باید با '09' شروع شود."))
        return mobile

    # اعتبارسنجی کد ملی: فقط ارقام و دقیقا 10 رقم
    def clean_legendry_code(self):
        legendry_code = self.cleaned_data.get("legendry_code", "")
        if legendry_code:
            if not legendry_code.isdigit():
                raise forms.ValidationError(_("کد ملی باید تنها شامل ارقام باشد."))
            if len(legendry_code) != 10:
                raise forms.ValidationError(_("کد ملی باید 10 رقم باشد."))
        return legendry_code

    # اعتبارسنجی کد پستی: فقط ارقام و دقیقا 10 رقم
    def clean_post_code(self):
        post_code = self.cleaned_data.get("post_code", "")
        if post_code:
            if not post_code.isdigit():
                raise forms.ValidationError(_("کد پستی باید تنها شامل ارقام باشد."))
            if len(post_code) != 10:
                raise forms.ValidationError(_("کد پستی باید 10 رقم باشد."))
        return post_code

class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        label='کلمه عبور فعلی',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control'
            }
        ),
        validators=[
            validators.MaxLengthValidator(100),
        ]
    )
    password = forms.CharField(
        label='کلمه عبور',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control'
            }
        ),
        validators=[
            validators.MaxLengthValidator(100),
        ]
    )
    confirm_password = forms.CharField(
        label='تکرار کلمه عبور',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control'
            }
        ),
        validators=[
            validators.MaxLengthValidator(100),
        ]
    )

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if password == confirm_password:
            return confirm_password

        raise ValidationError('کلمه عبور و تکرار کلمه عبور مغایرت دارند')
