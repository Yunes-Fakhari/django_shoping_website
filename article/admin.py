from typing import Any
from django.contrib import admin
from . import models
from .models import Article
from .models import ArticleComment
from django.http import HttpRequest

# Register your models here.

class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'url_title' , 'parent' , 'is_active']
    list_editable = ['url_title','parent','is_active']
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug' ,'create_date', 'is_active' , 'author',]
    list_editable = ['is_active']

    def save_model(self, request: HttpRequest, obj: Article, form: Any, change: Any):
        if not change :
            obj.author = request.user
        return super().save_model(request, obj, form, change)
    

class ArticleComment(admin.ModelAdmin):
    list_display= ['user' , 'create_date' , 'parent']

admin.site.register(models.ArticleCategory,ArticleCategoryAdmin)
admin.site.register(models.Article,ArticleAdmin)
admin.site.register(models.ArticleComment,ArticleComment)

# Register your models here.
