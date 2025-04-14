from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from .models import User  # مطمئن شوید که مسیر مدل کاربر درست است

class MobileBackend(BaseBackend):
    def authenticate(self, request, mobile=None, password=None, **kwargs):
        try:
            user = User.objects.get(mobile=mobile)
            if check_password(password, user.password):  # بررسی رمز عبور هش شده
                return user
        except User.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
