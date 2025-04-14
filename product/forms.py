from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm 
from .models import ProductComment
class ProductCommentForm(forms.ModelForm):
    class Meta:
        model = ProductComment
        fields = ['comment_text']
        widgets = {
            'comment_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
        labels = {
            'comment_text': 'نظر شما',
        }