from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from .models import User
from django.utils.crypto import get_random_string
from django.http import Http404, HttpRequest
from django.contrib.auth import login, logout
from utils.email_service import send_email
from .forms import RegisterForm, ForgetPasswordForm, ResetPasswordForm,UserRegistrationForm,MobileLoginForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib import messages
import random
import sweetify
from melipayamak import Api
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth import authenticate


def send_otp_sms(phone_number, otp_code):
    """
    ارسال پیامک حاوی کد OTP از طریق ملی پیامک
    :param phone_number: شماره تلفن گیرنده
    :param otp_code: کد تایید
    :return: True در صورت ارسال موفق، False در صورت خطا
    """
    try:
        username = '09366800970'  # نام کاربری ملی پیامک
        password = 'cf1a166f-bf74-493e-983e-8755cc348133'  # رمز عبور ملی پیامک
        api = Api(username, password)
        sms_soap = api.sms('rest')

        _from = '500027100381222'  # شماره ارسال‌کننده در ملی پیامک
        text = f"کد تایید شما: {otp_code}"  # متن پیامک
        response = sms_soap.send(phone_number, _from, text)

        print(f"✅ پیامک ارسال شد: {response}")  # لاگ برای تست
        return True  # ارسال موفقیت‌آمیز بود

    except Exception as e:
        print(f"❌ خطا در ارسال پیامک: {e}")
        return False  # ارسال ناموفق بود

class OTPView(View):
    def get(self, request):
        return render(request, 'account_module/otp.html')

    def post(self, request):
        otp1 = request.POST.get('otp1', '')
        otp2 = request.POST.get('otp2', '')
        otp3 = request.POST.get('otp3', '')
        otp4 = request.POST.get('otp4', '')

        user_otp = f"{otp4}{otp3}{otp2}{otp1}"
        session_otp = str(request.session.get('otp_code'))

        if user_otp == session_otp:
            phone_number = request.session.get('phone_number')

            # حذف مقدار OTP از سشن بعد از تایید
            del request.session['otp_code']

            # بررسی اینکه آیا کاربر از صفحه فراموشی رمز آمده است؟
            if request.session.get('f-p'):
                return redirect(reverse('reset_password_page', kwargs={'phone_number': phone_number}))
            
            # در غیر این صورت، هدایت به صفحه تنظیم نام کاربری و رمز عبور
            return redirect(reverse('set_username_password'))

        sweetify.error(request, "کد تایید صحیح نیست!", timer=4000)
        return render(request, 'account_module/otp.html')
    
class RegisterView(View):
    def get(self, request):
        register_form = RegisterForm()
        return render(request, 'account_module/register.html', {'register_form': register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            phone_number = register_form.cleaned_data.get('phone_number')

            # بررسی اینکه شماره تلفن قبلاً ثبت شده است یا نه
            if User.objects.filter(mobile=phone_number).exists():
                messages.error(request, "این شماره تلفن قبلاً ثبت شده است!")
                return render(request, 'account_module/register.html', {'register_form': register_form})

            # تولید کد OTP تصادفی (4 رقمی)
            otp_code = random.randint(1000, 9999)
            request.session['otp_code'] = otp_code  # ذخیره کد در سشن کاربر
            request.session['phone_number'] = phone_number  # ذخیره شماره تلفن در سشن
            print(otp_code)

            # ارسال کد OTP از طریق تابع `send_otp_sms`
            if send_otp_sms(phone_number,otp_code):
                messages.success(request, "کد تأیید ارسال شد!")
            else:
                messages.error(request, "خطا در ارسال کد تأیید!")
                return render(request, 'account_module/register.html', {'register_form': register_form})

            # هدایت کاربر به صفحه تأیید OTP
            return redirect(reverse('otp_verification_page'))

        # نمایش فرم با خطاها
        return render(request, 'account_module/register.html', {'register_form': register_form})
    
class SetUsernamePasswordView(View):
    def get(self, request):
        form = UserRegistrationForm()
        return render(request, 'account_module/set_username_password.html', {'form': form})

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            phone_number = request.session.get('phone_number')  # گرفتن شماره از سشن

            # بررسی اینکه آیا نام کاربری قبلاً ثبت شده است یا نه
            if User.objects.filter(username=username).exists():
                messages.error(request, "این نام کاربری قبلاً استفاده شده است!")
                return render(request, 'account_module/set_username_password.html', {'form': form})

            # ایجاد یوزر جدید
            user = User.objects.create_user(
                username=username,
                password=password,
                mobile=phone_number,
                date_joined=timezone.now()
            )
            user.save()
            
            # ورود خودکار کاربر
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            messages.success(request, "حساب کاربری شما با موفقیت ساخته شد.")
            
            if 'otp_code' in request.session:
                request.session.pop('otp_code', None)

            return redirect('home_page')  # هدایت به صفحه خانه

        return render(request, 'account_module/set_username_password.html', {'form': form})
class ResendOTPView(View):
    def post(self, request):
        phone_number = request.session.get("phone_number")

        if not phone_number:
            sweetify.error(request, "شماره‌ای یافت نشد!", button='باشه', timer=3000)
            return redirect("otp_verification_page")  # تغییر از render به redirect

        # تولید OTP جدید
        new_otp = random.randint(1000, 9999)
        request.session["otp_code"] = new_otp

        # ارسال پیامک
        if send_otp_sms(phone_number, new_otp):
            sweetify.success(request, "کد جدید ارسال شد!", button='باشه', timer=3000)
        else:
            sweetify.error(request, "خطا در ارسال کد تایید!", button='باشه', timer=3000)

        return redirect("otp_verification_page")  # تغییر از render به redirect
        
class ActivateAccountView(View):
    def get(self, request, email_active_code):
        user: User = User.objects.filter(email_active_code__iexact=email_active_code).first()
        if user is not None:
            if not user.is_active:
                user.is_active = True
                user.email_active_code = get_random_string(72)
                user.save()
                # todo: show success message to user
                return redirect(reverse('login_page'))
            else:
                # todo: show your account was activated message to user
                pass

        raise Http404
    

class LoginView(View):
    def get(self, request):
        form = MobileLoginForm()
        return render(request, 'account_module/login.html', {'form': form})

    def post(self, request):
        form = MobileLoginForm(request.POST)
        error_messages = []
        success_message = None

        if form.is_valid():
            mobile = form.cleaned_data['mobile']
            password = form.cleaned_data['password']
            user = authenticate(mobile=mobile, password=password)
            
            if user:
                login(request, user)
                success_message = "ورود موفقیت‌آمیز بود!"
                return render(request, 'home_module/index_page.html', {
                    'success_message': success_message
                })
            else:
                error_messages.append('رمز عبور اشتباه است!')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(error)

        return render(request, 'account_module/login.html', {
            'error_messages': error_messages,
            'form': form
        })

class ForgetPasswordView(View):
    def get(self, request):
        return render(request, 'account_module/forget_password.html')

    def post(self, request):
        phone_number = request.POST.get('phone_number')
        print(phone_number)
        # بررسی آیا شماره تلفن ثبت شده است؟
        if not User.objects.filter(mobile=phone_number).exists():
            sweetify.error(request, "چنین شماره‌ای در سایت ثبت نشده است!", timer=4000)
            return render(request, 'account_module/forget_password.html')

        # تولید و ذخیره کد تایید در سشن
        otp_code = random.randint(1000, 9999)
        request.session['otp_code'] = otp_code
        request.session['phone_number'] = phone_number
        request.session['f-p'] = True  # علامت‌گذاری که کاربر از صفحه فراموشی رمز عبور آمده است
        print(request.session['phone_number'],request.session['phone_number'],request.session['f-p'])
        # ارسال کد تایید به شماره تلفن
        if send_otp_sms(phone_number, otp_code):
            sweetify.success(request, "کد تأیید ارسال شد!", timer=4000)
        else:
            sweetify.error(request, "خطا در ارسال کد تأیید!", timer=4000)
            return render(request, 'account_module/forget_password.html')

        return redirect(reverse('otp_verification_page'))


class ResetPasswordView(View):
    def get(self, request, phone_number):
        # بررسی وجود مقدار 'f-p' در سشن
        if not request.session.get('f-p'):
            return render(request, 'account_module/404.html')

        del request.session['f-p']
        return render(request, 'account_module/reset_password.html', {'phone_number': phone_number})

    def post(self, request, phone_number):
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            sweetify.error(request, "رمزهای وارد شده یکسان نیستند!", timer=4000)
            return render(request, 'account_module/reset_password.html', {'phone_number': phone_number})

        try:
            user = User.objects.get(mobile=phone_number)
            user.set_password(new_password)  # هش کردن رمز عبور جدید
            user.save()
            


            sweetify.success(request, "رمز عبور با موفقیت تغییر کرد!", timer=4000)
            return redirect(reverse('login_page'))

        except User.DoesNotExist:
            sweetify.error(request, "کاربر یافت نشد!", timer=4000)
            return redirect(reverse('forget_password_page'))

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect(reverse('login_page'))
