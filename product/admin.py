from django.contrib import admin
from django import forms
from django.forms.widgets import FileInput
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.utils.html import format_html
from decimal import Decimal

from django_daisy.mixins import NavTabMixin
from auditlog.registry import auditlog
from auditlog.models import LogEntry

from .models import (
    Product,
    ProductSpecification,
    ProductVariant,  # مدل ورایانت
    StockTransaction,
    ProductCategory,
    SuperCategory,
    Color,
    Size,
    ProductTag,
    product_brand,
    ProductVisit,
    ProductGallery,
    ProductComment,
    SpecificationTitle
)

# -------------------------------------------------------------------------
# ویجت اختصاصی برای فیلد عکس؛ از FileInput استفاده می‌کنیم تا دکمه پاک کردن نمایش داده نشود.
# همچنین پیش‌نمایش تصویر دقیقا زیر فیلد آپلود اضافه می‌شود.
# -------------------------------------------------------------------------
class AdminImageWidget(FileInput):
    def render(self, name, value, attrs=None, renderer=None):
        input_html = super().render(name, value, attrs=attrs, renderer=renderer)
        if value and hasattr(value, 'url'):
            image_html = mark_safe(
                f'<br><img src="{value.url}" style="max-width: 300px; max-height: 300px;" />'
            )
            return mark_safe(input_html + image_html)
        return input_html

# -------------------------------------------------------------------------
# فرم سفارشی ادمین برای مدل Product جهت استفاده از ویجت اختصاصی در فیلد image
# -------------------------------------------------------------------------
class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'image': AdminImageWidget,  # اختصاص ویجت جدید به فیلد image
        }

# -------------------------------------------------------------------------
# فرم سفارشی اینلاین برای مدل ProductGallery جهت استفاده از همان ویجت
# -------------------------------------------------------------------------
class ProductGalleryInlineForm(forms.ModelForm):
    class Meta:
        model = ProductGallery
        fields = '__all__'
        widgets = {
            'image': AdminImageWidget,  # استفاده از ویجت برای نمایش پیش‌نمایش عکس
        }

# -------------------------------------------------------------------------
# اینلاین مربوط به مشخصات محصول
# -------------------------------------------------------------------------
class ProductSpecificationInline(admin.TabularInline, NavTabMixin):
    model = ProductSpecification
    extra = 1

# -------------------------------------------------------------------------
# اینلاین مربوط به ورایانت‌های محصول (ترکیب رنگ، سایز و موجودی)
# -------------------------------------------------------------------------
class ProductVariantInline(admin.TabularInline, NavTabMixin):
    model = ProductVariant
    extra = 1

# -------------------------------------------------------------------------
# اینلاین مربوط به گالری تصاویر محصول
# -------------------------------------------------------------------------
class ProductGalleryInline(admin.TabularInline, NavTabMixin):
    model = ProductGallery
    form = ProductGalleryInlineForm  # استفاده از فرم سفارشی برای اعمال ویجت
    extra = 1

# -------------------------------------------------------------------------
# تنظیمات ادمین برای مدل Product
# -------------------------------------------------------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm  # استفاده از فرم سفارشی که ویجت عکس را مدیریت می‌کند.
    
    list_display = [
        'title',
        'price',
        'get_final_price',
        'discount_percent',
        'is_active',
        'is_delete',
        'quantity',
        'get_profit_margin',
        'export_button'
    ]
    list_editable = ['price', 'is_active', 'discount_percent']
    readonly_fields = ('quantity',)
    
    # ترتیب فیلدها در فرم ادمین؛ فیلد image با ویجت اختصاصی ما رندر می‌شود.
    fields = (
        'title',
        'category',
        'image',  # فیلد عکس؛ پیش‌نمایش تصویر دقیقاً زیر این فیلد اضافه می‌شود.
        'brand',
        'price',
        'discount_percent',
        'quantity',
        'short_description',
        'description',
        'slug',
        'is_active',
        'is_delete',
        'warranty_months',
        'shipping_cost',
        'exchange_days',
        'created_at',
        'is_new',
        'is_featured',
    )
    
    # inlines شامل مشخصات، ورایانت‌ها و گالری تصاویر محصول
    inlines = [ProductSpecificationInline, ProductVariantInline, ProductGalleryInline]
    
    def export_button(self, obj):
        url = reverse('export_products')
        return format_html(f'<a class="button" href="{url}">خروجی اکسل</a>')
    export_button.short_description = "عملیات"
    
    def get_final_price(self, obj):
        price = Decimal(str(obj.price))
        discount_percent = obj.discount_percent
        if discount_percent > 0:
            discount_amount = (price * discount_percent) / Decimal(100)
            final_price = price - discount_amount
            return max(final_price, Decimal(0))
        return price
    get_final_price.short_description = "قیمت نهایی (بعد از تخفیف)"
    
    def get_profit_margin(self, obj):
        profit_margin = obj.calculate_profit_margin()
        return f"{profit_margin}%" if profit_margin is not None else "نامشخص"
    get_profit_margin.short_description = "درصد سود"

# -------------------------------------------------------------------------
# تنظیمات ادمین برای مدل ProductComment
# -------------------------------------------------------------------------
@admin.register(ProductComment)
class ProductCommentAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['product__title', 'user__username', 'comment_text']
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = "تایید نظرات انتخاب‌شده"

# -------------------------------------------------------------------------
# تنظیمات ادمین برای مدل StockTransaction
# -------------------------------------------------------------------------
@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_type', 'product', 'quantity', 'timestamp', 'description_display', 'last_log')
    list_filter = ('transaction_type', 'product')
    search_fields = ('product__title', 'description')

    def last_log(self, obj):
        last_log = LogEntry.objects.filter(object_pk=obj.pk).order_by('-timestamp').first()
        if last_log:
            return f"{last_log.action} - {last_log.timestamp.strftime('%Y-%m-%d %H:%M')}"
        return "بدون لاگ"
    last_log.short_description = "آخرین تغییر"
    
    def description_display(self, obj):
        if obj.description:
            if len(obj.description) > 10:
                return obj.description[:10] + "..."
            return obj.description
        return "بدون توضیحات"
    description_display.short_description = "توضیحات"

# -------------------------------------------------------------------------
# ثبت سایر مدل‌ها در ادمین
# -------------------------------------------------------------------------
auditlog.register(StockTransaction)
admin.site.register(ProductCategory)
admin.site.register(SpecificationTitle)
admin.site.register(SuperCategory)
admin.site.register(Color)
admin.site.register(Size)
admin.site.register(ProductTag)
admin.site.register(product_brand)
admin.site.register(ProductVisit)
# رجیستر جداگانه‌ی ProductGallery حذف می‌شود چون اکنون به عنوان اینلاین در ProductAdmin نمایش داده می‌شود.
