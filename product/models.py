from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from account.models import User
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from django.utils.timezone import now
from ckeditor_uploader.fields import RichTextUploadingField
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db.models import Sum
# Create your models here.
class SuperCategory(models.Model):
    title = models.CharField(max_length=300, db_index=True, verbose_name='عنوان ابر دسته‌بندی')
    url_title = models.CharField(max_length=300, db_index=True, verbose_name='عنوان ابر دسته‌بندی در url')
    image = models.ImageField(upload_to="images/supercategory", null=True, blank=True, verbose_name="تصویر محصول")
    is_active = models.BooleanField(verbose_name='فعال / غیرفعال')
    is_delete = models.BooleanField(verbose_name='حذف شده / نشده')

    def __str__(self):
        return f'( {self.title} - {self.url_title} )'

    class Meta:
        verbose_name = 'ابر دسته‌بندی'
        verbose_name_plural = 'ابر دسته‌بندی ها'

class ProductCategory(models.Model):
    super_category = models.ForeignKey(SuperCategory, related_name='categories', on_delete=models.CASCADE, verbose_name='ابر دسته‌بندی', null=True, blank=True)
    title = models.CharField(max_length=300, db_index=True, verbose_name='عنوان')
    url_title = models.CharField(max_length=300, db_index=True, verbose_name='عنوان در url')
    is_active = models.BooleanField(verbose_name='فعال / غیرفعال')
    is_delete = models.BooleanField(verbose_name='حذف شده / نشده')
    

    def __str__(self):
        return f'( {self.title} - {self.super_category.title} )'

    class Meta:
        verbose_name = 'دسته بندی'
        verbose_name_plural = 'دسته بندی ها'

class product_brand(models.Model):
    title = models.CharField(max_length=300 , verbose_name = ' نام برند ' ,db_index=True)
    url_title = models.CharField(max_length = 300 , verbose_name=' نام در url ',db_index=True )
    is_active = models.BooleanField(default=False, verbose_name='فعال / غیرفعال')

    class Meta:
        verbose_name = ' برند '
        verbose_name_plural = 'برند ها '

    def __str__(self):
        return self.title

class Color(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=("نام رنگ"))
    code = models.CharField(
        max_length=7,
        unique=True,
        verbose_name=("کد رنگ (HEX)"),
        help_text=("برای رنگ‌های متداول در فروشگاه لباس می‌توانید از این کدها استفاده کنید:<br>"
                    "#000000 (مشکی), #FFFFFF (سفید), #808080 (خاکستری), #C0C0C0 (نقره‌ای),<br>"
                    "#FF0000 (قرمز), #800000 (زرشکی), #FFA500 (نارنجی), #FFFF00 (زرد),<br>"
                    "#008000 (سبز), #00FFFF (فیروزه‌ای), #0000FF (آبی), #800080 (بنفش), #FFC0CB (صورتی)"),
    )

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = ("رنگ")
        verbose_name_plural = ("رنگ‌ها")


class Size(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=("نام سایز"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = ("سایز")
        verbose_name_plural = ("سایزها")

class SpecificationTitle(models.Model):
    title = models.CharField(max_length=100, verbose_name="عنوان مشخصه")

    class Meta:
        verbose_name = "عنوان مشخصه"
        verbose_name_plural = "عناوین مشخصه"

    def __str__(self):
        return self.title
    

class Product(models.Model):
    title = models.CharField(max_length=300, verbose_name="نام محصول")
    category = models.ManyToManyField('ProductCategory', related_name="product_categories", verbose_name="دسته بندی‌ها")
    image = models.ImageField(upload_to="images/product", null=True, blank=True, verbose_name="تصویر محصول")
    brand = models.ForeignKey('product_brand', on_delete=models.CASCADE, verbose_name="برند", null=True, blank=True)
    price = models.IntegerField(verbose_name="قیمت")
    quantity = models.PositiveIntegerField(default=0, verbose_name="موجودی")
    short_description = models.CharField(max_length=360, db_index=True, null=True, verbose_name="توضیحات کوتاه")
    description = RichTextUploadingField(verbose_name="توضیحات اصلی")
    slug = models.SlugField(default="", null=False, db_index=True, blank=True, max_length=200, unique=True, verbose_name="عنوان در URL")
    is_active = models.BooleanField(default=False, verbose_name="فعال / غیرفعال")
    is_delete = models.BooleanField(verbose_name="حذف شده / نشده")
    
    # فیلدهای جدید
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), verbose_name="درصد تخفیف")
    warranty_months = models.PositiveIntegerField(default=0, verbose_name="تعداد ماه گارانتی")
    shipping_cost = models.IntegerField(default=0, verbose_name="هزینه ارسال")
    exchange_days = models.PositiveIntegerField(default=10, verbose_name="مدت تعویض (روز)")

    created_at = models.DateTimeField(default=timezone.now, verbose_name="تاریخ ایجاد")
    is_new = models.BooleanField(default=True, verbose_name="محصول جدید")
    is_featured = models.BooleanField(default=False, verbose_name="محصول ویژه")

    def get_main_image_url(self):
        if self.image:
            return self.image.url
        else:
            return '/static/images/default-product.jpg'

    def get_final_price(self):
        """
        محاسبه قیمت نهایی بعد از اعمال تخفیف
        """
        if self.discount_percent > 0:
            discount_amount = (self.price * self.discount_percent) / 100
            final_price = self.price - discount_amount
            return int(final_price)
        return self.price

    def calculate_profit_margin(self):
        """
        محاسبه درصد سود (بعد از تخفیف، اگر اعمال شده باشد)
        """
        last_transaction = StockTransaction.objects.filter(
            product=self, transaction_type="in"
        ).order_by("-timestamp").first()

        if not last_transaction:
            return None

        purchase_price = last_transaction.purchase_price
        final_price = self.get_final_price()

        if purchase_price > 0:
            profit_margin = ((final_price - purchase_price) / purchase_price) * Decimal("100")
            return round(profit_margin, 2)
        return None

    def check_and_update_status(self):
        """
        بررسی می‌کند که آیا محصول جدید بیش از یک ماه از ایجادش گذشته است یا نه.
        اگر بیشتر از یک ماه گذشته باشد، مقدار `is_new` را `False` می‌کند.
        """
        one_month_ago = timezone.now() - timedelta(days=30)
        if self.created_at < one_month_ago:
            self.is_new = False
            self.save()
    def get_absolute_url(self):
        return reverse('product_detail', args=[self.slug])
    def __str__(self):
        return f"{self.title} ({self.get_final_price()})"

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants", verbose_name="محصول")
    color = models.ForeignKey(Color, on_delete=models.CASCADE, verbose_name="رنگ")
    size = models.ForeignKey(Size, on_delete=models.CASCADE, verbose_name="سایز")
    quantity = models.PositiveIntegerField(default=0, verbose_name="موجودی")
    # در صورت نیاز می‌توانید فیلدهای اضافی مانند قیمت اختصاصی برای این ورایانت یا وزن و سایر ویژگی‌ها را اضافه کنید.
    # به عنوان مثال:
    # variant_price = models.IntegerField(verbose_name="قیمت این نوع محصول", null=True, blank=True)
    def clean(self):
        """
        بررسی می‌کند که مجموع تعداد ورایانت‌های یک محصول از موجودی کلی محصول تجاوز نکند.
        """
        if self.product:
            # گرفتن تمام ورایانت‌های مربوط به این محصول
            variants = ProductVariant.objects.filter(product=self.product)
            # در صورت ویرایش، رکورد فعلی را از مجموع حذف می‌کنیم
            if self.pk:
                variants = variants.exclude(pk=self.pk)
            aggregated = variants.aggregate(total_qty=Sum('quantity'))
            existing_total = aggregated.get('total_qty') or 0
            new_total = existing_total + self.quantity

            if new_total > self.product.quantity:
                raise ValidationError(
                    f"در انبار محصولات ما فقط {self.product.quantity} عدد موجود است. مجموع تعداد این محصول (در حال حاضر {new_total} عدد) باید کمتر از {self.product.quantity} باشد."
                )

    def save(self, *args, **kwargs):
        # اطمینان از اجرای clean قبل از ذخیره
        self.full_clean()
        super().save(*args, **kwargs)
    class Meta:
        unique_together = (("product", "color", "size"),)
        verbose_name = "ورایانت محصول"
        verbose_name_plural = "ورایانت‌های محصول"

    def __str__(self):
        return f"{self.product.title} - {self.color.name} - {self.size.name} (موجودی: {self.quantity})"
class ProductComment(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='محصول'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='کاربر'
    )
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin_responses',
        verbose_name='ادمین پاسخ‌دهنده'
    )
    comment_text = models.TextField(verbose_name='متن نظر')
    admin_response = models.TextField(verbose_name='پاسخ ادمین', null=True, blank=True)
    is_approved = models.BooleanField(default=False, verbose_name='تایید شده')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')

    class Meta:
        verbose_name = 'نظر محصول'
        verbose_name_plural = 'نظرات محصولات'

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"        

class ProductSpecification(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='specifications',
        verbose_name="محصول"
    )
    specification_title = models.ForeignKey(
        SpecificationTitle,
        on_delete=models.CASCADE,
        verbose_name="عنوان مشخصه"
    )
    value = models.CharField(max_length=255, verbose_name="مقدار مشخصه")

    class Meta:
        verbose_name = "مشخصه محصول"
        verbose_name_plural = "مشخصات محصولات"
        unique_together = ('product', 'specification_title')

    def __str__(self):
        return f"{self.product.title} - {self.specification_title.title}: {self.value}"    


class StockTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('in', 'ورود'),
        ('out', 'خروج'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="محصول")
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPES, verbose_name="نوع عملیات")
    quantity = models.PositiveIntegerField(verbose_name="تعداد")
    purchase_price = models.DecimalField(default=0,max_digits=10, decimal_places=2, verbose_name="قیمت خرید")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="زمان عملیات")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    def clean(self):
        if self.quantity == 0 :
                raise ValidationError("مقدار 0 برای تعداد قابل قبول نیست.")
        if self.purchase_price < 0:
            raise ValidationError({'purchase_price': 'قیمت خرید نمی‌تواند منفی باشد.'})
        if self.transaction_type == 'out':
        # اگر موجودی صفر باشد
            if self.product.quantity == 0:
                raise ValidationError("این محصول در انبار موجود نیست.")
            # اگر موجودی کمتر از مقدار مورد نیاز باشد
            elif self.product.quantity < self.quantity:
                raise ValidationError("موجودی کافی نیست.")
        elif self.transaction_type == 'in':
            if self.purchase_price==0:
                raise ValidationError("شما حتما باید قیمت خرید را ثبت کنید.")
    def save(self, *args, **kwargs):
        if self.pk:  
            previous_transaction = StockTransaction.objects.get(pk=self.pk)
            previous_quantity = previous_transaction.quantity
            previous_transaction_type = previous_transaction.transaction_type
            previous_purchase_price = previous_transaction.purchase_price

            if previous_transaction_type == 'in':
                self.product.quantity -= previous_quantity
            elif previous_transaction_type == 'out':
                self.product.quantity += previous_quantity

            if self.transaction_type == 'in':
                self.product.quantity += self.quantity
            elif self.transaction_type == 'out':
                self.product.quantity -= self.quantity

            if self.purchase_price != previous_purchase_price:
                self._update_price_and_profit_margin(is_edit=True, previous_purchase_price=previous_purchase_price)

        else: 
            if self.transaction_type == 'in':
                self.product.quantity += self.quantity
                if self.purchase_price != 0:
                    self._update_price_and_profit_margin(is_edit=False)
            elif self.transaction_type == 'out':
                self.product.quantity -= self.quantity

        self.product.save()
        super().save(*args, **kwargs)


    def _update_price_and_profit_margin(self, is_edit=False, previous_purchase_price=None):
        """
        محاسبه قیمت میانگین وزنی و به روزرسانی قیمت محصول
        """
        if is_edit:  # اگر تراکنش در حال ویرایش باشد
            total_quantity = self.product.quantity
            if total_quantity > 0:
                # محاسبه میانگین وزنی قیمت خرید
                current_total_value = (self.product.quantity - self.quantity) * Decimal(previous_purchase_price)  # مقدار فعلی کل
                new_total_value = self.quantity * self.purchase_price  # مقدار جدید
                weighted_average_price = (current_total_value + new_total_value) / total_quantity

                # تنظیم قیمت محصول با اضافه کردن 10 درصد
                self.product.price = weighted_average_price * Decimal('1.1')

                # محاسبه درصد سود
                self._calculate_profit_margin(previous_purchase_price)

        else:  # اگر تراکنش جدید باشد
            total_quantity = self.product.quantity
            if total_quantity > 0:
                # محاسبه میانگین وزنی قیمت خرید
                current_total_value = self.product.quantity * Decimal(self.product.price) / Decimal('1.1')  # مقدار فعلی کل
                new_total_value = self.quantity * self.purchase_price  # مقدار جدید
                weighted_average_price = (current_total_value + new_total_value) / total_quantity

                # تنظیم قیمت محصول با اضافه کردن 10 درصد
                self.product.price = weighted_average_price * Decimal('1.1')

                # محاسبه درصد سود
                self._calculate_profit_margin(self.purchase_price)


    def _calculate_profit_margin(self, previous_purchase_price):
        """
        محاسبه درصد سود محصول بر اساس قیمت خرید قبلی و قیمت جدید
        """
        # دریافت قیمت فروش فعلی محصول
        sale_price = self.product.price

        # محاسبه درصد سود
        if previous_purchase_price > 0:
            profit_margin = ((sale_price - previous_purchase_price) / previous_purchase_price) * Decimal('100')
            self.product.profit_margin = round(profit_margin, 2)
        else:
            self.product.profit_margin = None 

    def __str__(self):
        return f"{self.transaction_type} - {self.product.title} - {self.quantity}"
    class Meta:
        verbose_name = 'انبار محصولات'
        verbose_name_plural = 'انبار محصولات'


class ProductTag(models.Model):
    caption = models.CharField(max_length=300, db_index=True, verbose_name='عنوان')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_tags',verbose_name=' تگ های موجود ')

    class Meta:
        verbose_name = 'تگ محصول'
        verbose_name_plural = 'تگ های محصولات'

    def __str__(self):
        return self.caption
    

class ProductVisit(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='محصول')
    ip = models.CharField(max_length=30, verbose_name='آی پی کاربر')
    user = models.ForeignKey(User, null=True, blank=True, verbose_name='کاربر', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.product.title} / {self.ip}'

    class Meta:
        verbose_name = 'بازدید محصول'
        verbose_name_plural = 'بازدیدهای محصول'

class ProductGallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='محصول')
    image = models.ImageField(upload_to='images/product-gallery', verbose_name=' تصویر محصول ')

    def __str__(self):
        return self.product.title

    class Meta:
        verbose_name = ' تصویر گالری'
        verbose_name_plural = ' گالری تصاویر'



class Discount (models.Model):
    title = models.CharField(max_length=300 , verbose_name = ' تخفبف  ')
