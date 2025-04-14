from django.db import models
from django.utils.translation import gettext_lazy as _
from account.models import User
from product.models import Product
class FavoriteList(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="favorite_list",
        verbose_name="کاربر"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاریخ ایجاد"))

    def __str__(self):
        return f"لیست علاقه‌مندی‌های {self.user.username}"

    class Meta:
        verbose_name = "لیست علاقه‌مندی"
        verbose_name_plural = "لیست‌های علاقه‌مندی"


class FavoriteItem(models.Model):
    favorite_list = models.ForeignKey(
        FavoriteList,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("لیست علاقه‌مندی")
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="favorited_items",
        verbose_name=_("محصول")
    )
    added_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاریخ افزودن"))

    def __str__(self):
        return f"{self.product.title} در لیست علاقه‌مندی‌های {self.favorite_list.user.username}"

    class Meta:
        verbose_name = _("آیتم علاقه‌مندی")
        verbose_name_plural = _("آیتم‌های علاقه‌مندی")