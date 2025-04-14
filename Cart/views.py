from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, JsonResponse
from product.models import Product,StockTransaction,ProductVariant
from .models import Cart , CartDetail,CartItem
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required 
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product, Cart, CartDetail, Color, Size
# Create your views here.
MERCHANT = 'ec11b7a7-6b22-41e6-8fbf-b65280a86fc3'
ZP_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/{authority}"
amount = 11000  # Rial / Required
description = "نهایی کردن خرید شما از سایت ما"  # Required
email = 'nima.alzd1382@gmail.com'  # Optional
mobile = '09333714077'  # Optional
# Important: need to edit for realy server.
CallbackURL = 'http://localhost:8000/cart/verify-payment/'
@login_required(login_url='login_page')
def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        color_id = request.POST.get('color_id')
        size_id = request.POST.get('size_id')
        quantity = int(request.POST.get('quantity', 1))

        # بررسی انتخاب رنگ و سایز
        if not color_id:
            messages.error(request, 'لطفاً رنگ محصول را انتخاب کنید.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        if not size_id:
            messages.error(request, 'لطفاً سایز محصول را انتخاب کنید.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        product = get_object_or_404(Product, id=product_id)
        color = get_object_or_404(Color, id=color_id)
        size = get_object_or_404(Size, id=size_id)

        # بررسی وجود ورایانت مربوط به محصول با رنگ و سایز انتخاب‌شده
        try:
            product_variant = ProductVariant.objects.get(product=product, color=color, size=size)
        except ProductVariant.DoesNotExist:
            messages.error(request, 'این محصول با این رنگ و سایز موجود نیست.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        # بررسی اینکه تعداد درخواست شده از موجودی ورایانت بیشتر نباشد
        if quantity > product_variant.quantity:
            messages.error(
                request,
                f'موجودی این محصول با این رنگ و سایز تنها {product_variant.quantity} عدد می‌باشد.'
            )
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        # بررسی ورود کاربر به سیستم و دریافت سبد خرید مربوطه
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user, is_paid=False)
            if not cart.pk:
                cart.save()  # اطمینان از اختصاص یک کلید اصلی
        else:
            messages.error(request, 'برای افزودن به سبد خرید، لطفاً ابتدا وارد حساب کاربری خود شوید.')
            return redirect('login_page')

        # اختصاص نام‌های متنی برای رنگ و سایز جهت ثبت در CartDetail
        color_name = color.name
        size_name = size.name



        # بررسی اینکه آیا محصول با همین رنگ و سایز هم اکنون در سبد خرید موجود است یا خیر
        cart_detail_exists = CartDetail.objects.filter(
            cart=cart,
            product=product,
            color__iexact=color_name,
            size__iexact=size_name
        ).exists()

        if cart_detail_exists:
            messages.warning(
                request,
                'این محصول با این رنگ و سایز در حال حاضر در سبد خرید شما موجود است.'
            )
        else:
            # افزودن محصول به سبد خرید
            CartDetail.objects.create(
                cart=cart,
                product=product,
                color=color_name,
                size=size_name,
                count=quantity,

            )
            messages.success(request, 'محصول با موفقیت به سبد خرید اضافه شد.')

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    return redirect('home_page')

@login_required(login_url='login_page')
def remove_from_cart(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')

        if not item_id:
            messages.error(request, 'محصول مورد نظر یافت نشد.')
            return redirect('cart')

        # دریافت آیتم سبد خرید
        cart_item = get_object_or_404(CartDetail, id=item_id)

        # بررسی مالکیت آیتم
        if request.user.is_authenticated and cart_item.cart.user == request.user:
            if cart_item.count > 1:
                cart_item.count -=1
                cart_item.save()
                messages.success(request, 'یک عدد از محصول از سبد خرید شما کم شد.')
            else:
                cart_item.delete()
                messages.success(request, 'محصول با موفقیت از سبد خرید حذف شد.')
        else:
            messages.error(request, 'شما اجازه انجام این کار را ندارید.')
            return redirect('home_page')
    else:
        return redirect('home_page')
    


@login_required(login_url='login_page')
def request_payment(request: HttpRequest):
    current_cart, created = Cart.objects.get_or_create(is_paid=False, user_id=request.user.id)
    total_price = current_cart.calculate_total_price()
    
    if total_price == 0:
        return redirect(reverse('user_cart_page'))

    # شبیه‌سازی پرداخت موفق
    payment_successful = True  # همیشه پرداخت موفق است

    if payment_successful:
        return redirect(reverse('verify_payment'))  # هدایت به مرحله تأیید پرداخت
    else:
        return render(request, 'cart_module/payment_result.html', {
            'error': 'پرداخت با خطا مواجه شد / کاربر از پرداخت ممانعت کرد'
        })

from django.db import transaction
from django.utils.timezone import now

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import transaction
from xhtml2pdf import pisa
from io import BytesIO
from django.utils.timezone import now
from django.template.loader import render_to_string
from melipayamak import Api

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils.timezone import now
from django.http import Http404
from django.utils import timezone
def send_sms(phone_number, message):
    """
    ارسال پیامک حاوی کد OTP از طریق ملی پیامک
    :param phone_number: شماره تلفن گیرنده
    :param otp_code: کد تایید
    :return: True در صورت ارسال موفق، False در صورت خطا
    """
    try:
        username = '09366800970'  # نام کاربری ملی پیامک
        password = 'cf1a166f-bf74-493e-983e-8755cc348133'  # رمز عبور ملی پیامک
        api = Api(username, password)
        sms_soap = api.sms('rest')

        _from = '500027100381222'  # شماره ارسال‌کننده در ملی پیامک
        text = f"{message}"  # متن پیامک
        response = sms_soap.send(phone_number, _from, text)

        print(f"✅ پیامک ارسال شد: {response}")  # لاگ برای تست
        return True  # ارسال موفقیت‌آمیز بود

    except Exception as e:
        print(f"❌ خطا در ارسال پیامک: {e}")
        return False  # ارسال ناموفق بود

@login_required(login_url='login_page')
def verify_payment(request):    

    current_cart, created = Cart.objects.get_or_create(user=request.user, is_paid=False)
    cart = get_object_or_404(Cart, user=request.user, is_paid=False)

    # اگر آیتمی در سبد خرید نباشد، خطای مناسب برگردانید.
    if not current_cart.cartdetail_set.exists():
        messages.error(request, "سبد خرید شما خالی است.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    # بررسی موجودی محصولات برای هر آیتم
    insufficient_stock = []
    for item in current_cart.cartdetail_set.all():
        if item.product.quantity < item.count:
            insufficient_stock.append(
                f"{item.product.title} (موجودی: {item.product.quantity}, درخواستی: {item.count})"
            )
    if insufficient_stock:
        error_message = "موجودی محصولات کافی نیست برای: " + ", ".join(insufficient_stock)
        messages.error(request, error_message)
        return render(request, 'cart_module/payment_result.html', {'error': error_message})
    
    try:
        with transaction.atomic():
            # ذخیره یک لیست از آیتم‌های CartDetail جهت استفاده بعدی (برای پیامک یا صدور فاکتور)
            detail_items = list(current_cart.cartdetail_set.all())
            
            # کاهش موجودی محصولات
            for item in detail_items:
                product = item.product
                product.quantity -= item.count
                product.save()
            
            # ایجاد آیتم‌های سبد خرید (CartItem) با ثبت قیمت واحد
            for item in detail_items:
                CartItem.objects.create(
                    cart=current_cart,
                    product=item.product,
                    color=item.color,
                    size=item.size,
                    count=item.count,
                    unit_price=item.product.get_final_price()  # ثبت قیمت واحد در زمان خرید
                )
            
            # حذف آیتم‌های CartDetail (پاکسازی)
            current_cart.cartdetail_set.all().delete()
            
            # علامت‌گذاری سبد خرید به عنوان پرداخت‌شده و ثبت تاریخ پرداخت
            current_cart.is_paid = True
            current_cart.payment_date = timezone.now()
            # حالا با وجود آیتم‌های ایجاد شده در CartItem، متد save قیمت کل را محاسبه می‌کند.
            current_cart.save()
            print("Cart marked as paid")
            
    except Exception as e:
        return render(request, 'cart_module/payment_result.html', {
            'error': f'خطا در پردازش پرداخت: {str(e)}'
        })
    
    # استفاده از آیتم‌های انتقال یافته (CartItem) جهت ساخت پیام فاکتور / SMS
    purchased_items = current_cart.items.all()  # از related_name 'items' در مدل CartItem استفاده می‌شود.
    
    sms_message = "فاکتور خرید شما:\n"
    for item in purchased_items:
        # استفاده از ذخیره شده‌ی unit_price در CartItem
        line = (
            f"{item.product.title} : \n تعداد: {item.count} | "
            f"قیمت واحد: {item.unit_price:,} تومان | "
            f"جمع: {(item.count * item.unit_price):,} تومان"
        )
        sms_message += line + "\n"
    
    total_price = sum(item.count * item.unit_price for item in purchased_items)
    sms_message += f"مبلغ کل: {total_price:,} تومان"
    #user_phone = request.user.mobile
    # در صورت وجود شماره تلفن کاربر، می‌توانید پیامک ارسال کنید.
    # if user_phone:
    #     send_sms(user_phone, sms_message)
    # else:
    #     print("شماره تلفن کاربر موجود نیست؛ پیامک ارسال نشد.")
    
    return render(request, "cart_module/payment_result.html", {
        'user': request.user,
        'cart': current_cart,
        'cart_items': purchased_items,
        'total_price': total_price,
        'payment_date': current_cart.payment_date,
        'cart_id':cart.id
    })



# @login_required(login_url='login_page')
# def verify_payment(request: HttpRequest):
#     current_cart, created = Cart.objects.get_or_create(is_paid=False, user_id=request.user.id)
#     total_price = current_cart.calculate_total_price()
#     t_authority = request.GET['Authority']
#     if request.GET.get('Status') == 'OK':
#         req_header = {"accept": "application/json", "content-type": "application/json'"}
#         req_data = {
#             "merchant_id": MERCHANT,
#             "amount": total_price * 10,
#             "authority": t_authority
#         }
#         req = requests.post(url=ZP_API_VERIFY, data=json.dumps(req_data), headers=req_header)
#         if len(req.json()['errors']) == 0:
#             t_status = req.json()['data']['code']
#             if t_status == 100:
#                 current_cart.is_paid = True
#                 current_cart.payment_date = time.time()
#                 current_cart.save()
#                 ref_str = req.json()['data']['ref_id']
#                 return render(request, 'cart_module/payment_result.html', {
#                     'success': f'تراکنش شما با کد پیگیری {ref_str} با موفقیت انجام شد'
#                 })
#             else:
#                 # return HttpResponse('Transaction failed.\nStatus: ' + str(
#                 #     req.json()['data']['message']
#                 # ))
#                 return render(request, 'cart_module/payment_result.html', {
#                     'error': str(req.json()['data']['message'])
#                 })
#         else:
#             e_code = req.json()['errors']['code']
#             e_message = req.json()['errors']['message']
#             # return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")
#             return render(request, 'cart_module/payment_result.html', {
#                 'error': e_message
#             })
#     else:
#         return render(request, 'cart_module/payment_result.html', {
#             'error': 'پرداخت با خطا مواجه شد / کاربر از پرداخت ممانعت کرد'
#         })
