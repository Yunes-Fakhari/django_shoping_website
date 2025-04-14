# myapp/dashboard.py
from django.db.models import Sum
from django.contrib.auth import get_user_model
from product.models import Product  # فرض کنید Product و Cart در myapp.models تعریف شده‌اند
from Cart.models import Cart
User = get_user_model()

class Dashboard:
    def __init__(self):
        # ویجت‌های داینامیک را بارگذاری می‌کنیم.
        self.widgets = self.load_dynamic_widgets()
    
    def load_dynamic_widgets(self):
        """
        در این متد مقادیر داینامیک از مدل‌ها خوانده می‌شود.
        توجه داشته باشید که اگر در پروژه حجم داده‌ها زیاد باشد ممکن است بخواهید این کوئری‌ها را کش کنید.
        """
        # تعداد کاربران فعال (استفاده از is_active که در AbstractUser تعریف شده)
        active_users = User.objects.filter(is_active=True).count()
        
        # تعداد کل سفارشات (سبدهای خرید)
        total_orders = Cart.objects.count()
        
        # تعداد سفارشات در انتظار (مثلاً سفارشاتی که هنوز پرداخت نشده‌اند)
        pending_orders = Cart.objects.filter(is_paid=False).count()
        
        # جمع کل قیمت سفارشات پرداخت‌شده (درآمد کل)
        total_revenue_dict = Cart.objects.filter(is_paid=True).aggregate(total=Sum('final_price'))
        total_revenue = total_revenue_dict.get('total') or 0
        
        # تعداد محصولات فعال (محصولاتی که is_active=True و is_delete=False هستند)
        products_count = Product.objects.filter(is_active=True, is_delete=False).count()
        
        # حالا ویجت‌ها را بر مبنای این آمار می‌سازیم.
        widgets = [
            {
                'color': 'primary',
                'formatted_value': active_users,
                'icon': 'fas fa-users',
                'title': 'کاربران فعال',
                
            },
            {
                'color': 'secondary',
                'formatted_value': total_orders,
                'icon': 'fas fa-shopping-bag',
                'title': 'کل سفارشات',
                # در این مثال از متنی ثابت استفاده کرده‌ایم؛
                # در صورت نیاز می‌توانید مقدار pending_orders را هم در بنر جایگزین کنید.
                'badge': {'text': f'{pending_orders} در انتظار', 'class': 'badge-warning'},
            },
            {
                'color': 'accent',
                # اگر می‌خواهید از intcomma استفاده کنید، در قالب می‌توانید آن را فیلتر کنید
                'formatted_value': f'{total_revenue} تومان',
                'icon': 'fas fa-wallet',
                'title': 'درآمد کل',
                'badge': {'text': '+24%', 'class': 'badge-success'},
            },
            {
                'color': 'neutral',
                'formatted_value': products_count,
                'icon': 'fas fa-cube',
                'title': 'محصولات فعال',
                'badge': {'text': 'جدید', 'class': 'badge-info'},
            },
        ]
        return widgets
    
    def get_dashboard_info(self):
        """
        این متد یک دیکشنری برمی‌گرداند که کلید "dashboard_widgets"
        شامل لیست ویجت‌های داینامیک است.
        """
        return { "dashboard_widgets": self.widgets }
