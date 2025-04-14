from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
# Create your views here.
from django.views import View
from django.views.generic.list import ListView 
from django.views.generic import DetailView
from jalali_date import datetime2jalali, date2jalali
from article.models import Article , ArticleCategory , ArticleComment
from django.http import  HttpRequest , HttpResponse
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages
from django.shortcuts import redirect
# class ArticlesView(View):
#     def get(self, request):
#         articles = Article.objects.filter(is_active=True)
#         context = {
#             'articles': articles
#         }
#         return render(request, 'article_module/articles_page.html', context)



class ArticlesListView(ListView):
    model = Article
    paginate_by = 2  # تعداد مقالات هر صفحه
    template_name = 'article_module/article_page.html'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(is_active=True)
        category_name = self.kwargs.get('category')
        if category_name:
            queryset = queryset.filter(selected_categories__url_title__iexact=category_name)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # اضافه کردن مقادیر دلخواه به کانتکست (در صورت نیاز)
        return context


def article_detail_view(request, pk):
    # دریافت مقاله با pk مشخص و تنها مقالات فعال را پوشش می‌دهد.
    article = get_object_or_404(Article, pk=pk, is_active=True)
    
    # دریافت نظرات اصلی (بدون والد) مربوط به مقاله فعلی به ترتیب نزولی تاریخ ثبت
    comments = ArticleComment.objects.filter(
        article=article,
        parent=None,
        is_active=True
    ).order_by('-create_date').prefetch_related('articlecomment_set')
    
    # شمارش کل نظرات فعال مربوط به مقاله
    comments_count = ArticleComment.objects.filter(article=article, is_active=True).count()
    
    # دریافت آخرین پست‌های فعال بر اساس زمان ایجاد (تاریخ و ساعت)
    latest_articles = Article.objects.filter(is_active=True).order_by('-create_date')[:5]
    
    context = {
        'article': article,
        'comments': comments,
        'comments_count': comments_count,
        'latest_articles': latest_articles,
    }
    
    return render(request, 'article_module/article_detail.html', context)
    
def article_categories_component(request: HttpRequest):
    article_main_categories = ArticleCategory.objects.prefetch_related('articlecategory_set').filter(is_active=True, parent_id=None)

    context = {
        'main_categories': article_main_categories
    }
    return render(request, 'article_module/components/article_categories_component.html', context)




def add_article_comment(request):
    # دریافت داده‌های ارسال شده از فرم
    article_id = request.POST.get('article_id')
    article_comment = request.POST.get('article_comment')
    parent_id = request.POST.get('parent_id')

    # در اینجا می‌توانید اعتبارسنجی‌های لازم را انجام دهید
    if not article_comment:
        messages.error(request, "متن نظر نمی‌تواند خالی باشد.")
        return redirect(request.META.get("HTTP_REFERER", "/"))
    
    try:
        # ایجاد و ذخیره کامنت جدید
        new_comment = ArticleComment(
            article_id=article_id,
            text=article_comment,
            user=request.user,
            parent_id=parent_id if parent_id not in [None, ''] else None
        )
        new_comment.save()
        # ارسال پیام موفقیت
        messages.success(request, "پیام شما ارسال شد؛ پس از تایید ادمین نمایش داده خواهد شد.")
    except Exception as e:
        # در صورت خطا پیام خطا ارسال می‌شود
        messages.error(request, "خطایی رخ داده است. لطفاً دوباره تلاش کنید.")
    
    # کاربر به صفحه قبلی برگردانده می‌شود
    return redirect(request.META.get("HTTP_REFERER", "/"))



