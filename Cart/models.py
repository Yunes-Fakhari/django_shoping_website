from django.db import models
from account.models import User
from product.models import Product,Color,Size
# Create your models here.
STATUS_CHOICES = (
        ('نامشخص', 'نامشخص'),
        ('در حال پردازش', 'در حال پردازش'),
        ('در حال آماده سازی محصولات', 'در حال آماده سازی محصولات'),
        ('در حال ارسال به دست شما', 'در حال ارسال به دست شما'),
        ('به شهر شما رسیدیم', 'به شهر شما رسیدیم'),
    )
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')
    is_paid = models.BooleanField(verbose_name='نهایی شده / نشده', default=False)
    payment_date = models.DateField(null=True, blank=True, verbose_name='تاریخ پرداخت')
    final_price = models.IntegerField(
        verbose_name="قیمت کل",
        blank=True,
        null=True,
        help_text="قیمت کل سبد خرید، محاسبه شده بر اساس قیمت هر آیتم ضرب در تعداد"
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='نامشخص',
        verbose_name='وضعیت سفارش'
    )
    def __str__(self):
        return str(self.user)

    def calculate_total_price(self):
        total = sum(item.unit_price * item.count for item in self.items.all())
        return total

    def save(self, *args, **kwargs):
        # محاسبه قیمت کل سبد خرید
        if self.pk:  # اگر شیء قبلاً ذخیره شده باشد
            self.final_price = self.calculate_total_price()
        else:
            self.final_price = 0

        # اگر خرید پرداخت شده باشد و وضعیت هنوز "نامشخص" است،
        # آن را به "در حال پردازش" تغییر می‌دهیم
        if self.is_paid and self.status == 'نامشخص':
            self.status = 'در حال پردازش'
        super().save(*args, **kwargs)
    class Meta:
        verbose_name = 'سبد خرید'
        verbose_name_plural = 'سبدهای خرید کاربران'


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="سبد خرید"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="محصول")
    color = models.CharField(max_length=50, verbose_name='رنگ')
    size = models.CharField(max_length=50, verbose_name='سایز')
    count = models.PositiveIntegerField(verbose_name='تعداد', default=1)
    unit_price = models.IntegerField(
        verbose_name='قیمت واحد',
        default=0,
        help_text="قیمت واحد ثبت شده هنگام خرید"
    )
    @property
    def final_price(self):
        # در اینجا می‌توانید محاسبات دلخواه را انجام دهید.
        # به صورت پیش‌فرض، اگر قیمت نهایی همان unit_price باشد:
        return self.unit_price
    def __str__(self):
        return f"{self.product.title} - {self.size} - {self.color} - {self.count}"

    class Meta:
        verbose_name = "آیتم سبد خرید"
        verbose_name_plural = "آیتم‌های سبد خرید"

class CartDetail(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, verbose_name='سبد خرید')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='محصول')
    color = models.CharField(default="رنگ محصول",max_length=50, verbose_name='رنگ')
    size = models.CharField(default="سایز محصول",max_length=50, verbose_name='سایز')
    count = models.IntegerField(verbose_name='تعداد')
    
    def get_total_price(self):
        return self.count * self.final_price
    
    class Meta:
        verbose_name = 'جزئیات سبد خرید'
        verbose_name_plural = 'لیست جزئیات سبدهای خرید'