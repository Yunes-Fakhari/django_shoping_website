from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect , get_object_or_404
from django.http import HttpResponse , Http404 , HttpRequest
from django.db.models import Count
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.views.generic.base import View
from pages.models import SiteBanner
from utils.http_services import get_client_ip
from utils.convertors import group_list
from .models import Product, ProductCategory, product_brand, ProductVisit , ProductGallery,SuperCategory,ProductSpecification,ProductComment,ProductVariant,Color,Size
from .forms import ProductCommentForm
# from django.db.models import Avg  , Min # use for average
from django.contrib import messages
from django.urls import reverse
#Instead of using template views, we can use list views.
#The structure of the same structure and our model is passed to it as the model itself or the name of the model.
#When we use the list view, the context is known as the list object by default. We can use the command code of the context object to give it the name we want.
#Pass a certain amount of something to our own page using the get query function and use a variable and receive the query.
from django.views.generic import ListView
from .models import Product

from django.core.paginator import Paginator


from django.db.models import Count
from django.views.generic import ListView
from .models import Product, SuperCategory, ProductCategory, product_brand
from django.db.models import Q
from functools import reduce
import operator

class ProductListView(ListView):
    model = Product
    template_name = 'product_module/product_list.html'
    context_object_name = 'products'
    paginate_by = 3  # تعداد محصولات در هر صفحه

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).order_by('-created_at')

        # دریافت پارامترهای فیلتر از URL
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category__id=category_id).distinct()
        
        # فیلتر بر اساس جستجوی کاربر
        query = self.request.GET.get('q')
        if query:
            search_fields = [
                'title__icontains',
                'description__icontains',
                'short_description__icontains',
                'brand__title__icontains',
                'category__title__icontains',
                'category__super_category__title__icontains',
            ]
            queryset = queryset.filter(
                reduce(operator.or_, (Q(**{field: query}) for field in search_fields))
            ).distinct()
        
        selected_categories = self.request.GET.getlist('categories')
        selected_brands = self.request.GET.getlist('brands')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        super_category_id = self.request.GET.get('super_category')

        # فیلتر بر اساس ابر دسته‌بندی
        if super_category_id:
            queryset = queryset.filter(category__super_category_id=super_category_id).distinct()

        # فیلتر بر اساس دسته‌ها
        if selected_categories:
            queryset = queryset.filter(category__id__in=selected_categories).distinct()

        # فیلتر بر اساس برندها
        if selected_brands:
            queryset = queryset.filter(brand__id__in=selected_brands).distinct()

        # فیلتر بر اساس محدوده قیمت
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # پردازش پارامتر مرتب‌سازی
        sort = self.request.GET.get('sort')
        print(sort)
        if sort == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'date_desc':
            queryset = queryset.order_by('-created_at')
        elif sort == 'date_asc':
            queryset = queryset.order_by('created_at')
        else:
            # مرتب‌سازی پیش‌فرض
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # محاسبه تعداد محصولات برای ابر دسته‌بندی‌ها
        super_categories = SuperCategory.objects.annotate(
            product_count=Count('categories__product_categories', distinct=True))
        context['super_categories'] = super_categories
        context['sort'] = self.request.GET.get('sort', '')
        # استخراج محبوب‌ترین محصولات بر اساس سفارش‌های موفق:
        popular_products = Product.objects.filter(
            cartitem__cart__is_paid=True,
            cartitem__cart__status='به شهر شما رسیدیم'  # یا هر وضعیت موفق که مد نظر شماست
        ).annotate(
            purchase_count=Count('cartitem')
        ).order_by('-purchase_count')[:3]  # نمایش ۳ محصول محبوب به عنوان نمونه

        context['popular_products'] = popular_products
        # محاسبه تعداد محصولات برای برندها
        context['brands'] = product_brand.objects.annotate(
            product_count=Count('product'))
        
        # محاسبه تعداد محصولات برای دسته‌بندی‌ها
        context['category_data'] = ProductCategory.objects.annotate(
            product_count=Count('product_categories'))

        # اضافه کردن مقادیر انتخاب شده به context
        context.update({
            'selected_categories': self.request.GET.getlist('categories'),
            'selected_brands': self.request.GET.getlist('brands'),
            'min_price': self.request.GET.get('min_price', ''),
            'max_price': self.request.GET.get('max_price', ''),
            'selected_super_category': self.request.GET.get('super_category', '')
        })
        
        return context


class ProductDetailView(DetailView):
    template_name = 'product_module/product-slider.html'
    model = Product
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        slug = self.kwargs.get(self.slug_url_kwarg)
        product = get_object_or_404(Product, slug=slug, is_active=True, is_delete=False)
        return product

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = ProductCommentForm()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = ProductCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.product = self.object
            if request.user.is_authenticated:
                comment.user = request.user
            else:
                messages.error(request, 'برای ثبت نظر باید وارد شوید.')
                return redirect('login')
            comment.save()
            messages.success(request, 'نظر شما با موفقیت ثبت شد و پس از تایید نمایش داده خواهد شد.')
            return redirect(reverse('product_detail', kwargs={'slug': self.object.slug}))
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        request = self.request

        # دسته‌بندی‌های محصول
        context['categories'] = product.category.all()

        # ابر دسته‌بندی‌ها
        context['super_categories'] = SuperCategory.objects.filter(
            categories__in=product.category.all()
        ).distinct()

        # برند محصول
        context['brand'] = product.brand

        # **بروزرسانی رنگ‌ها و سایزها از طریق مدل ورایانت**
        # به این ترتیب رنگ‌ها و سایزهای موجود برای این محصول از مدل ورایانت استخراج می‌شوند.
        context['colors'] = Color.objects.filter(productvariant__product=product).distinct()
        context['sizes'] = Size.objects.filter(productvariant__product=product).distinct()

        # قیمت نهایی محصول پس از تخفیف
        context['final_price'] = product.get_final_price()

        approved_comments = ProductComment.objects.filter(
            product=product, is_approved=True).order_by('-created_at')
        context['approved_comments'] = approved_comments
        context['comments_count'] = approved_comments.count()

        if 'form' not in context:
            context['form'] = ProductCommentForm()

        # گالری محصول
        galleries = list(ProductGallery.objects.filter(product=product))
        context['product_galleries_group'] = group_list(galleries, 3)

        # محصولات مرتبط (بر اساس دسته‌بندی و برند)
        # دریافت لیست شناسه‌های محصولات مرتبط به صورت منحصربه‌فرد
        related_product_ids = Product.objects.filter(
            category__in=product.category.all(),
            is_active=True,
            is_delete=False
        ).exclude(id=product.id).values_list('id', flat=True).distinct()

        # سپس محصولات مرتبط را بر اساس این شناسه‌ها دریافت می‌کنیم
        related_products = Product.objects.filter(id__in=related_product_ids).order_by('-created_at')
        context['related_products'] = related_products

        # سایر اطلاعات محصول
        context['is_new'] = product.is_new
        context['is_featured'] = product.is_featured
        context['warranty_months'] = product.warranty_months
        context['shipping_cost'] = product.shipping_cost
        context['exchange_days'] = product.exchange_days

        # اطلاعات بنرها
        context['banners'] = SiteBanner.objects.filter(
            is_active=True,
            position__iexact=SiteBanner.SiteBannerPosition.product_detail
        )

        specifications = ProductSpecification.objects.filter(product=product).select_related('specification_title')
        context['specifications'] = specifications

        # علاقه‌مندی (در صورت نیاز)
        favorite_product_id = request.session.get("product_favorites")
        context['is_favorite'] = favorite_product_id == str(product.id)

        return context
# class AddProductFavorite(View):
#     def post(self, request):
#         product_id = request.POST["product_id"]
#         product = Product.objects.get(pk=product_id)
#         request.session["product_favorites"] = product_id
#         return redirect(product.get_absolute_url())
from django.http import JsonResponse
class ProductModalDetailView(DetailView):
    model = Product
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_object(self, queryset=None):
        return get_object_or_404(
            Product,
            slug=self.kwargs["slug"],
            is_active=True,
            is_delete=False
        )

    def render_to_response(self, context, **response_kwargs):
        product = self.object

        # محاسبه قیمت نهایی با استفاده از متد get_final_price
        if product.discount_percent > 0:
            discounted_price = product.get_final_price()
            original_price = product.price
        else:
            discounted_price = product.price
            original_price = None

        # دریافت عکس اصلی (با fallback به تصویر پیش‌فرض)
        main_image = product.get_main_image_url()

        # دریافت تصاویر گالری از طریق مدل ProductGallery
        gallery_images = [img.image.url for img in ProductGallery.objects.filter(product=product)]
        
        # ترکیب تصاویر اصلی و گالری - در اینجا عکس اصلی به عنوان اولین مورد قرار می‌گیرد.
        images = [main_image] + gallery_images

        # استخراج رنگ‌ها و سایزها از ورایانت‌های محصول
        raw_colors = product.variants.all().values("color__name", "color__code").distinct()
        colors = [{"name": item["color__name"], "code": item["color__code"]} for item in raw_colors]
        
        raw_sizes = product.variants.all().values_list("size__name", flat=True).distinct()
        sizes = list(raw_sizes)

        data = {
            "title": product.title,
            "price": discounted_price,
            "original_price": original_price,
            "quantity": product.quantity,
            "short_description": product.short_description,
            "description": product.description,
            "warranty_months": product.warranty_months,
            "shipping_cost": product.shipping_cost,
            "exchange_days": product.exchange_days,
            "is_new": product.is_new,
            "is_featured": product.is_featured,
            "images": images,
            "brand": product.brand.title if product.brand else None,
            "categories": list(product.category.values("title", "url_title")),
            "colors": colors,
            "sizes": sizes,
            "slug": product.slug,
        }
        return JsonResponse(data)

def product_categories_component(request: HttpRequest):
    product_categories = ProductCategory.objects.filter(is_active = True , is_delete = False)
    context = {
        'categories' : product_categories
    }
    return render (request , 'product_module/components/product_categories_component.html' , context)

def product_brands_component(request: HttpRequest):
    #point3 = go to code.txt
    product_brands = product_brand.objects.annotate(products_count=Count('product')).filter(is_active=True)
    context = {
        'brands': product_brands
    }
    return render(request, 'product_module/components/product_brands_component.html', context)

from openpyxl import Workbook
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone   
@staff_member_required
def export_products_to_excel(request):
    # ایجاد workbook و worksheet
    wb = Workbook()
    ws_products = wb.active
    ws_products.title = "Products"
    
    # ایجاد شیت دوم برای واریانت‌ها
    ws_variants = wb.create_sheet(title="Variants")

    # هدرهای شیت محصولات
    products_headers = [
        "ID",
        "عنوان",
        "دسته‌بندی‌ها",
        "برند",
        "قیمت اصلی",
        "قیمت نهایی",
        "درصد تخفیف",
        "درصد سود",
        "موجودی کلی",
        "وضعیت فعال",
        "تاریخ ایجاد",
        "محصول جدید",
        "گارانتی (ماه)",
        "هزینه ارسال",
        "مدت تعویض",
    ]
    ws_products.append(products_headers)

    # هدرهای شیت واریانت‌ها
    variants_headers = [
        "Product ID",
        "عنوان محصول",
        "رنگ",
        "سایز",
        "موجودی واریانت",
    ]
    ws_variants.append(variants_headers)

    # دریافت تمام محصولات
    products = Product.objects.prefetch_related('category', 'variants').all()

    for product in products:
        # آماده‌سازی داده‌های محصول
        categories = ", ".join([c.title for c in product.category.all()])
        brand = product.brand.title if product.brand else "---"
        
        # محاسبه فیلدهای مشتق شده
        final_price = product.get_final_price()
        profit_margin = product.calculate_profit_margin() or "---"

        # افزودن سطر محصول
        row = [
            product.id,
            product.title,
            categories,
            brand,
            product.price,
            final_price,
            product.discount_percent,
            f"{profit_margin}%" if profit_margin != "---" else profit_margin,
            product.quantity,
            "فعال" if product.is_active else "غیرفعال",
            product.created_at.strftime("%Y-%m-%d %H:%M"),
            "بله" if product.is_new else "خیر",
            product.warranty_months,
            product.shipping_cost,
            product.exchange_days,
        ]
        ws_products.append(row)

        # افزودن واریانت‌ها
        for variant in product.variants.all():
            variant_row = [
                product.id,
                product.title,
                variant.color.name,
                variant.size.name,
                variant.quantity,
            ]
            ws_variants.append(variant_row)

    # ایجاد پاسخ
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    filename = f"products_export_{timezone.now().strftime('%Y-%m-%d')}.xlsx"
    response["Content-Disposition"] = f"attachment; filename={filename}"
    
    # ذخیره workbook در response
    wb.save(response)

    return response