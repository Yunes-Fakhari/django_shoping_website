from django.contrib import admin
from .models import User  # مدل سفارشی شما

# ثبت مدل سفارشی User در ادمین
admin.site.register(User)
