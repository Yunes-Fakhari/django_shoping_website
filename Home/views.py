from django.db.models import Count
from django.shortcuts import render
from django.views.generic.base import TemplateView
from pages.models import SiteBanner
from pages.models import SiteSetting , FooterLinkBox , Slider
from utils.convertors import group_list
from product.models import Product , ProductCategory,SuperCategory
from utils.convertors import group_list
from django.db.models import Sum
from django.views.generic import ListView
# Create your views here.
from django.http import JsonResponse
from django.db.models import Q
from django.urls import reverse 
#def index_page(request):
    #return render(request, 'home_module/index_page.html')
#We used the bottom class as the base view class and above we used the base view function
# class HomeView(View):
#     def get (self , request):
#         return render(request, 'home_module/index_page.html')

#To use a context in the base view class of the template view, we need to override a function called Get Context Data.
#And we must use the return super().get_context_data(**kwargs)key argument command
#If we don't want to make a change, we enter it manually, but if we want to make a change on it, we do it as follows
#Then we put that command in a variable called context and consider a key for that context and put the desired text or the desired value in it.

class HomeView(TemplateView):
    template_name = 'home_module/index_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # اسلایدرهای فعال
        sliders = Slider.objects.filter(is_active=True)
        context['sliders'] = sliders

        # جدیدترین محصولات
        latest_product = Product.objects.filter(is_active=True, is_delete=False).order_by('-id')[:12]

        # پربازدیدترین محصولات
        most_visit_products = Product.objects.filter(is_active=True, is_delete=False)\
            .annotate(visit_count=Count('productvisit'))\
            .order_by('-visit_count')[:12]

        context['latest_products'] = group_list(latest_product)
        context['most_visit_products'] = group_list(most_visit_products)




        # پرفروش‌ترین محصولات
        most_bought_products = Product.objects.filter(cartdetail__cart__is_paid=True)\
            .annotate(cart_count=Sum('cartdetail__count'))\
            .order_by('-cart_count')[:12]

        context['most_bought_products'] = group_list(most_bought_products)

        return context


class FeaturedProductListView(ListView):
    model = Product
    template_name = 'include/featured_product_list.html'  # تمپلیت مربوط به محصولات ویژه
    context_object_name = 'products'

    def get_queryset(self):
        queryset = Product.objects.filter(
            is_active=True,
            is_featured=True,
            is_delete=False
        ).order_by('-created_at')

        # دریافت super_category_id هم از kwargs یا GET:
        super_category_id = self.kwargs.get('super_category_id') or self.request.GET.get('super_category_id')
        if super_category_id:
            queryset = queryset.filter(category__super_category__id=super_category_id)
        return queryset


class NewProductListView(ListView):
    model = Product
    template_name = 'include/new_product_list.html'  # تمپلیت خروجی برای محصولات جدید (partial)
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(
            is_active=True,
            is_new=True,
            is_delete=False
        ).order_by('-created_at')

class BrandSectionView(TemplateView):
    template_name = 'include/brand_section.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # دریافت ۳ محصول ویژه آخر
        context['featured_products'] = Product.objects.filter(
            is_active=True,
            is_featured=True,
            is_delete=False
        ).order_by('-created_at')[:3]
        # دریافت ۳ محصول جدید آخر
        context['new_products'] = Product.objects.filter(
            is_active=True,
            is_new=True,
            is_delete=False
        ).order_by('-created_at')[:3]
        return context

class InstagramSectionView(ListView):
    model = Product
    template_name = 'include/instagram_section.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        # تمامی محصولات فعال و حذف نشده، به ترتیب آخرین ایجاد
        return Product.objects.filter(is_active=True, is_delete=False).order_by('-created_at')

def site_header_component(request):
    setting: SiteSetting = SiteSetting.objects.filter(is_main_setting=True).first()
    context = {
        'site_setting': setting
    }
    return render(request, 'shared/site_header_component.html', context)

#Using Django's partial or component feature, we can control our pages automatically

def site_footer_component(request):
    setting: SiteSetting = SiteSetting.objects.filter(is_main_setting=True).first()
    footer_link_boxes = FooterLinkBox.objects.all()
    for item in footer_link_boxes:
        item.footerlink_set
    context = {
        'site_setting': setting , 
        'footer_link_boxes' : footer_link_boxes
    }
    return render (request ,'shared/site_footer_component.html' , context)


class AboutView(TemplateView):
    template_name = 'home_module/about_page.html'
    def get_context_data(self, **kwargs):
        context = super(AboutView, self).get_context_data(**kwargs)
        site_setting: SiteSetting = SiteSetting.objects.filter(is_main_setting=True).first()
        context['site_setting'] = site_setting
        context['banners'] = SiteBanner.objects.filter(is_active=True , position__iexact =SiteBanner.SiteBannerPosition.about_us)
        return context
from django.views import View
class ProductSearchView(View):
    def get(self, request):
        query = request.GET.get('q', '').strip()
        
        if not query:
            return JsonResponse({'results': []})

        products = Product.objects.filter(
            Q(title__icontains=query) |
            Q(short_description__icontains=query) |
            Q(description__icontains=query),
            is_active=True,
            is_delete=False
        )[:10]

        results = []
        for product in products:
            original_price = product.price  # مستقیماً از IntegerField استفاده کنید
            discounted_price = None
            
            if product.discount_percent > 0:
                discount = original_price * (product.discount_percent / 100)
                discounted_price = int(original_price - discount)  # تبدیل به عدد صحیح

            results.append({
                'title': product.title,
                'image': product.image.url if product.image else '',
                'original_price': original_price,  # ارسال به صورت عدد صحیح
                'discounted_price': discounted_price,  # ارسال به صورت عدد صحیح
                'has_discount': product.discount_percent > 0,
                'url': reverse('product_detail', args=[product.slug]),
                'rating': 4,
                'warranty': product.warranty_months
            })

        return JsonResponse({'results': results})

class ProductSearchMobileView(View):
    template_name = 'home_module/search.html'

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        
        # فیلتر محصولات
        products = Product.objects.filter(
            title__icontains=query,
            is_active=True,
            is_delete=False
        )

        # پاسخ برای درخواست AJAX
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            products_data = []
            for product in products:
                # محاسبه قیمت با تخفیف
                original_price = product.price
                final_price = original_price
                discount_percent = 0

                if product.discount_percent > 0:
                    discount_percent = product.discount_percent
                    final_price = original_price * (100 - discount_percent) // 100

                products_data.append({
                    'title': product.title,
                    'original_price': original_price,
                    'final_price': final_price,
                    'discount_percent': discount_percent,
                    'image_url': product.image.url if product.image else '',
                    'slug': product.slug,
                    'url': reverse('product_detail', args=[product.slug]),
                    'short_description': product.short_description,
                })
            
            return JsonResponse({'products': products_data})
        
        # پاسخ عادی
        return render(request, self.template_name, {
            'products': products,
            'query': query
        })