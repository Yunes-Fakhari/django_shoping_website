from django import forms
from .models import contact_us
from django.core import validators

# class ContactUsForm(forms.Form): #Inside the models, only Cher field can be used for text and there is no text field, so we can use widgets.
#     full_name = forms.CharField(
#         label='نام و نام خانوادگی',
#         max_length=50,
#         error_messages={
#             'required': 'لطفا نام و نام خانوادگی خود را وارد کنید',
#             'max_length': 'نام و نام خانوادگی نمی تواند بیشتر از 50 کاراکتر باشد'
#         },
#         #We can use attrs inside the widgets and give them the desired class as well as the police holder, which is the desired half of the text box.
#         widget=forms.TextInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'نام و نام خانوادگی'
#         })
#     )
#     email = forms.EmailField(
#         label='ایمیل',
#         widget=forms.EmailInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'ایمیل'
#         })
#     )
#     title = forms.CharField(
#         label='عنوان',
#         widget=forms.TextInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'عنوان'
#         })
#     )
#     massage = forms.CharField(
#         label='متن پیام',
#         widget=forms.Textarea(attrs={
#             'class': 'form-control',
#             'placeholder': 'متن پیام',
#             'rows': '5',
#             'id': 'message'
#         })
#     )

class ContactUsModelForm(forms.ModelForm):
    class Meta:
        model = contact_us
        #fields = '__all__' #The all command means to return all the values in our model
        #exclude = ['response'] #The exclude command returns what we want, that is, we want the rest of all the items except that item.
        fields = ['full_name', 'email', 'title', 'message']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'email': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'id': 'message'
            })
        }

        labels = {
            'full_name': 'نام و نام خانوادگی شما',
            'email': 'ایمیل شما'
        }

        error_messages = {
            'full_name': {
                'required': 'نام و نام خانوادگی اجباری می باشد. لطفا وارد کنید'
            }
        }

# class ProfileForm(forms.Form):
#     user_image = forms.ImageField()