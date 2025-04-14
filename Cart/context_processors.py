from .models import Cart, CartDetail

def cart_details(request):
    context = {
        'cart_items': [],
        'cart_items_count': 0,
        'total_price': 0
    }
    
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user, is_paid=False)
            cart_items = CartDetail.objects.filter(cart=cart).select_related('product')
            
            # محاسبه قیمت هر آیتم و مجموع کل
            total = 0
            for item in cart_items:
                item_price = item.product.get_final_price()  # دریافت قیمت از مدل Product
                item.total_price = item_price * item.count  # افزودن ویژگی داینامیک
                total += item.total_price

            context.update({
                'cart_items': cart_items,
                'cart_items_count': cart_items.count(),
                'total_price': total
            })
            
        except Cart.DoesNotExist:
            pass
            
    return context

