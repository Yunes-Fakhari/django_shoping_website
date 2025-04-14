from typing import Any
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render , redirect
from django.views.generic import TemplateView, ListView
from django.http import HttpRequest, HttpResponse, JsonResponse , Http404
from django.views.generic import View
from .forms import ChangePasswordForm,ProfileUpdateForm
from account.models import User
from django.contrib.auth import  logout
from django.urls import reverse
from Cart.models import Cart , CartDetail
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required 
from django.utils.decorators import method_decorator
from django.db.models import F, ExpressionWrapper, IntegerField, Sum
from django.shortcuts import get_object_or_404
from .models import FavoriteItem,FavoriteList
from product.models import Product,ProductVariant
from functools import wraps
from django.contrib import messages
from django.http import HttpResponseRedirect
# # Create your views here.
def custom_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login_page')
        return view_func(request, *args, **kwargs)
    return wrapper

# دکوریتور کلاس برای اعمال دکوریتور روی CBV‌ها
def custom_login_required_class(cls):
    cls.dispatch = method_decorator(custom_login_required)(cls.dispatch)
    return cls

@custom_login_required_class
class UserPanelDashboardPage(TemplateView):
    template_name = 'User/user_panel_dashboard_page.html'

@login_required(login_url='login_page')
def update_profile(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            user = request.user
            # تقسیم نام کامل به نام و نام خانوادگی
            fullname = form.cleaned_data.get("fullname", "").strip()
            if fullname:
                names = fullname.split()
                user.first_name = names[0]
                user.last_name = " ".join(names[1:]) if len(names) > 1 else ""
            
            user.email = form.cleaned_data.get("email")
            user.mobile = form.cleaned_data.get("mobile")
            
            if form.cleaned_data.get("photo"):
                user.avatar = form.cleaned_data.get("photo")
            
            # به‌روزرسانی آدرس، کد ملی و کد پستی
            user.address = form.cleaned_data.get("address")
            user.legendry_code = form.cleaned_data.get("legendry_code")
            user.post_code = form.cleaned_data.get("post_code")
            
            # به‌روزرسانی سایر فیلدها
            gender_value = form.cleaned_data.get("gender")

            # بررسی مقدار ارسال شده و ذخیره مقدار دلخواه در مدل
            if gender_value == "مرد" or str(gender_value).strip().lower() == "مرد":
                user.gender = "Man"   # یا اگر می‌خواهید مقدار مدرن فارسی ذخیره شود،
                                    # می‌توانید به عنوان مثال "مرد" نیز ذخیره کنید
            elif gender_value == "زن" or str(gender_value).strip().lower() == "زن":
                user.gender = "Female"  # یا "زن"
            else:
                # در صورت عدم تطابق (مثلا مقدار دیگری ارسال شده باشد) مقدار پیش‌فرض
                user.gender = None
            user.state = form.cleaned_data.get("location")
            user.save()
            messages.success(request, "اطلاعات پروفایل شما با موفقیت به‌روزرسانی شد.")
            return redirect("user_panel_dashboard")
        else:
            # استخراج پیام خطا برای هر فیلد
            error_message = "<br>".join(
                f"{', '.join(errors)}" for field, errors in form.errors.items()
            )
            messages.error(request, error_message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    else:
        # در حالت GET فرم با دیتاهای اولیه کاربر پر می‌شود.
        initial_data = {
            "fullname": f"{request.user.first_name} {request.user.last_name}".strip(),
            "email": request.user.email,
            "mobile": request.user.mobile,
            "gender": "مرد" if request.user.gender == "Man" else "زن" if request.user.gender == "Female" else "نامشخص",
            "location":request.user.state,
            "address": request.user.address,
            "legendry_code": request.user.legendry_code,
            "post_code": request.user.post_code,
        }
        form = ProfileUpdateForm(initial=initial_data)
        
    return render(request, "User/components/profile.html", {"form": form})
@custom_login_required_class
class ChangePasswordPage(View):
    def get(self, request: HttpRequest):
        context = {
            'form': ChangePasswordForm()
        }
        return render(request, 'User/change_password_page.html', context)

    def post(self, request: HttpRequest):
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            current_user: User = User.objects.filter(id=request.user.id).first()
            if current_user.check_password(form.cleaned_data.get('current_password')):
                current_user.set_password(form.cleaned_data.get('password'))
                current_user.save()
                logout(request)
                return redirect(reverse('login_page'))
            else:
                form.add_error('password', 'کلمه عبور وارد شده اشتباه می باشد')

        context = {
            'form': form
        }
        return render(request, 'User/change_password_page.html', context)


@custom_login_required_class
class FavoriteListView(ListView):
    model = FavoriteItem
    template_name = 'User/favorites_list.html'
    context_object_name = 'favorite_items'

    def get_queryset(self):
        if hasattr(self.request.user, 'favorite_list'):
            return self.request.user.favorite_list.items.select_related('product')
        return FavoriteItem.objects.none()
    
@login_required(login_url='login_page')    
def add_to_favorites(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # دریافت یا ساخت لیست علاقه‌مندی کاربر
    favorite_list, created = FavoriteList.objects.get_or_create(user=request.user)
    
    # بررسی وجود محصول در لیست علاقه‌مندی
    if not FavoriteItem.objects.filter(favorite_list=favorite_list, product=product).exists():
        FavoriteItem.objects.create(favorite_list=favorite_list, product=product)
        messages.success(request, f"محصول '{product.title}' با موفقیت به لیست علاقه‌مندی‌ها اضافه شد.")
    else:
        messages.info(request, f"محصول '{product.title}' قبلاً در لیست علاقه‌مندی‌ها وجود داشته است.")
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='login_page')
def remove_favorite_item(request, pk):
    """
    حذف یک آیتم از لیست علاقه‌مندی کاربر با توجه به PK آیتم.
    پس از حذف، کاربر به صفحه لیست علاقه‌مندی هدایت می‌شود.
    """
    favorite_item = get_object_or_404(FavoriteItem, pk=pk, favorite_list__user=request.user)
    if request.method == 'POST':
        favorite_item.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@custom_login_required_class
class MyShopping(ListView):
    model = Cart
    template_name = 'User/components/Order.html'
    context_object_name = 'carts'
    def get_object(self, queryset=None):
        return self.request.user
    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related('items__product')
        request: HttpRequest = self.request
        queryset = queryset.filter(user=request.user, is_paid=True).order_by('-payment_date')
        return queryset
@login_required(login_url='login_page')
def invoice_view(request, cart_id):
    cart = get_object_or_404(Cart, id=cart_id, user=request.user, is_paid=True)
    return render(request, 'User/components/invoice.html', {'cart': cart})

@login_required(login_url='login_page')
def user_panel_menu_component(request: HttpRequest):
    return render(request , 'User/components/user_panel_menu_component.html' )

@login_required(login_url='login_page')
def user_cart(request: HttpRequest):
    try:
        cart = Cart.objects.get(user=request.user, is_paid=False)
        cart_items = CartDetail.objects.filter(cart=cart).select_related('product')
    except Cart.DoesNotExist:
        cart_items = []

    if request.method == "POST":
        for item in cart_items:
            qty_str = request.POST.get(f'quantity_{item.id}')
            if qty_str:
                try:
                    new_quantity = int(qty_str)
                    if new_quantity >= 1:
                        # جستجوی واریانت متناسب با رنگ و سایز
                        try:
                            variant = ProductVariant.objects.get(
                                product=item.product,
                                color__name=item.color,
                                size__name=item.size
                            )
                            # بررسی موجودی واریانت
                            if new_quantity > variant.quantity:
                                messages.error(
                                    request,
                                    f"محصول {item.product.title} (رنگ: {item.color}, سایز: {item.size}) در تعداد درخواستی موجود نمیباشد"
                                )
                                return redirect('user_cart_page')
                        except ProductVariant.DoesNotExist:
                            # اگر واریانت وجود نداشت، موجودی اصلی محصول چک شود
                            if new_quantity > item.product.quantity:
                                messages.error(
                                    request,
                                    f"موجودی {item.product.title} کافی نیست. موجودی: {item.product.quantity}"
                                )
                                return redirect('user_cart_page')

                        # بررسی کلی موجودی محصول بدون در نظر گرفتن واریانت
                        if new_quantity > item.product.quantity:
                            messages.error(
                                request,
                                f"موجودی کلی {item.product.title} کافی نیست. موجودی: {item.product.quantity}"
                            )
                            return redirect('user_cart_page')

                        item.count = new_quantity
                        item.save()
                except ValueError:
                    pass

        return redirect('user_cart_page')

    # محاسبات مالی
    cart_subtotal = 0
    cart_total_discount = 0
    
    for item in cart_items:
        product = item.product
        quantity = item.count
        original_price = product.price
        final_price = product.get_final_price()
        
        cart_subtotal += final_price * quantity
        discount_per_item = original_price - final_price
        cart_total_discount += discount_per_item * quantity

    delivery_cost = 50000 if cart_subtotal > 0 else 0
    cart_total = cart_subtotal + delivery_cost

    context = {
        'cart_items': cart_items,
        'cart_items_count': sum(item.count for item in cart_items),
        'cart_subtotal': cart_subtotal,
        'delivery_cost': delivery_cost,
        'cart_total_discount': cart_total_discount,
        'cart_total': cart_total,
    }
    return render(request, 'User/user_cart.html', context)


@login_required(login_url='login_page')
def remove_cart_detail(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        
        if not item_id:
            return JsonResponse({
                'status': 'error',
                'message': 'محصول مورد نظر یافت نشد.'
            })

        # دریافت آیتم سبد خرید و اطمینان از این که متعلق به کاربر و هنوز پرداخت نشده باشد
        cart_item = get_object_or_404(
            CartDetail,
            id=item_id,
            cart__is_paid=False,
            cart__user=request.user
        )

        # حذف کل محصول از سبد خرید (صرف نظر از تعداد)
        cart_item.delete()

        # به‌روزرسانی سبد خرید کاربر
        user_cart, created = Cart.objects.prefetch_related('cartdetail_set').get_or_create(
            is_paid=False,
            user=request.user
        )
        total_amount = user_cart.calculate_total_price()
        
        context = {
            'cart': user_cart,
            'sum': total_amount  # مجموع قیمت‌های به‌روز سبد خرید
        }
        
        return JsonResponse({
            'status': 'success',
            'body': render_to_string('User/user_cart_content.html', context)
        })
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'متد غیرمجاز.'
        })
    
    user_cart_content.html
@login_required(login_url='login_page')
def change_order_detail_count(request: HttpRequest):
    detail_id = request.GET.get('detail_id')
    state = request.GET.get('state')
    if detail_id is None or state is None:
        return JsonResponse({
            'status': 'not_found_detail_or_state'
        })
    
    cart_detail = CartDetail.objects.filter(id=detail_id , cart__is_paid=False , cart__user_id =request.user.id).first()

    if cart_detail is None:
        return JsonResponse({
            'status': 'detail_not_found'
        })
    if state == 'increase':
        cart_detail.count += 1
        cart_detail.save()
    elif state == 'decrease':
        if cart_detail.count == 1:
            cart_detail.delete()
        else:
            cart_detail.count -= 1
            cart_detail.save()
    else:
        return JsonResponse({
            'status': 'state_invalid'
        })
    

    user_open_cart , created =Cart.objects.prefetch_related('cartdetail_set').get_or_create(is_paid=False, user_id=request.user.id)
    total_amount = user_open_cart.calculate_total_price()
    
    
    context = {
        'cart' : user_open_cart ,
        'sum' : total_amount
    }
    return JsonResponse({
        'status': 'success',
        'body': render_to_string('User/user_cart_content.html', context)
    })



@login_required(login_url='login_page')
def my_shopping_detail(request: HttpRequest, cart_id):
    cart = Cart.objects.prefetch_related('cartdetail_set').filter(id=cart_id, user_id=request.user.id).first()
    if cart is None:
        raise Http404('سبد خرید مورد نظر یافت نشد')

    return render(request, 'User/user_shopping_detail.html', {
        'cart': cart
    })


