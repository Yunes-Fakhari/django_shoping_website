from django.contrib import admin
from .models import FavoriteItem,FavoriteList
# Register your models here.
from django_daisy.mixins import NavTabMixin
class FavoriteItemInline(admin.TabularInline,NavTabMixin):  # یا admin.StackedInline
    model = FavoriteItem
    extra = 1  # تعداد خطوط خالی برای اضافه کردن آیتم‌های جدید

@admin.register(FavoriteList)
class FavoriteListAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    inlines = [FavoriteItemInline]
from django.contrib.auth.models import User as DefaultUser
from django.contrib import admin

try:
    admin.site.unregister(DefaultUser)
except admin.sites.NotRegistered:
    pass  # اگر ثبت نشده، خطا را نادیده بگیرید    