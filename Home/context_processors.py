from product.models import SuperCategory

def categories_context(request):
    """دریافت دسته‌بندی‌ها و ارسال آنها به تمپلیت‌ها"""
    super_categories = SuperCategory.objects.filter(is_active=True, is_delete=False)  # فقط ابر دسته‌بندی‌های فعال و غیر حذف شده
    categories_data = []

    # ایجاد یک لیست از ابر دسته‌بندی‌ها و دسته‌بندی‌های مربوط به آن‌ها
    for super_cat in super_categories:
        categories = super_cat.categories.filter(is_active=True, is_delete=False)  # فقط دسته‌بندی‌های فعال
        categories_data.append({
            'id': super_cat.id,
            'title': super_cat.title,
            'categories': categories,
            'image': super_cat.image.url
        })

    return {
        'categories_data1': categories_data
    }