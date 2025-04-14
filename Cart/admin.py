from django import forms
from django_daisy.admin import admin
from .models import Cart, CartDetail, CartItem
from product.models import Product
from django_daisy.mixins import NavTabMixin

@admin.register(CartDetail)
class CartDetailAdmin(admin.ModelAdmin):
    list_display = (
        'cart_user',
        'product_title',
        'color',
        'size',
        'count',
        'final_price_display',
        'total_price_display',
    )

    def cart_user(self, obj):
        return obj.cart.user
    cart_user.short_description = 'کاربر'

    def product_title(self, obj):
        return obj.product.title
    product_title.short_description = 'محصول'

    def final_price_display(self, obj):
        final_price = obj.product.get_final_price()
        return "{:,} تومان".format(final_price)
    final_price_display.short_description = 'قیمت واحد'

    def total_price_display(self, obj):
        total_price = obj.product.get_final_price() * obj.count
        return "{:,} تومان".format(total_price)
    total_price_display.short_description = 'قیمت نهایی'


# این اینلاین فقط آیتم‌های سبد خرید موجود در مدل CartItem را نشان می‌دهد.
class CartItemInline(admin.TabularInline, NavTabMixin):
    model = CartItem
    extra = 0
    fields = ('product_title', 'color', 'size', 'count', 'unit_price', 'total_price')
    readonly_fields = ('product_title', 'unit_price', 'total_price')

    def product_title(self, obj):
        return obj.product.title
    product_title.short_description = 'محصول'

    def unit_price(self, obj):
        price = obj.product.get_final_price()
        return "{:,} تومان".format(price)
    unit_price.short_description = 'قیمت واحد'

    def total_price(self, obj):
        total = obj.product.get_final_price() * obj.count
        return "{:,} تومان".format(total)
    total_price.short_description = 'قیمت نهایی'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_paid', 'payment_date']
    # به جای نمایش محصولات یا CartDetail، این اینلاین، آیتم‌های CartItem را نشان می‌دهد.
    inlines = [CartItemInline]

