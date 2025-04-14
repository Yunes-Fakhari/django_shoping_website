from typing import Any
from django.shortcuts import render , redirect
from django.urls import reverse
from .forms import  ContactUsModelForm 
from .models import  UserProfile
from django .views import View
from django.views.generic.edit import FormView
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from django.views.generic.base import View
from pages.models import SiteSetting
from django.views.generic import TemplateView
# Create your views here.

class ContactUsView(TemplateView):
    template_name = 'contact_module/contact_us.html'



# class ContactUsView(FormView):
#     template_name = 'contact_module/contact_us.html'
#     form_class = ContactUsModelForm
#     success_url = '/contact-us/'

    # def form_valid(self, form):
    #     form.save()
    #     return super().form_valid(form)
    
def store_file(file):
    with open('temp/image.jpg', "wb+") as dest:
        for chunk in file.chunks():
            dest.write(chunk)


class CreateProfileView(CreateView):
    template_name = 'contact_module/create-profile-page.html'
    model = UserProfile
    fields = '__all__'
    success_url = '/contact-us/create-profile'


class ProfilesView(ListView):
    model = UserProfile
    template_name = 'contact_module/profile_list_page.html '
    context_object_name = 'profiles'

    



# class CreateProfileView(View):
#     def get(self, request):
#         form = ProfileForm()
#         return render(request, 'contact_module/create-profile-page.html', {
#             'form': form
#         })

#     def post(self, request):
#         submitted_form = ProfileForm(request.POST, request.FILES)

#         if submitted_form.is_valid():
#             # store_file(request.FILES['profile'])
#             profile = UserProfile(image=request.FILES["user_image"])
#             profile.save()
#             return redirect('/contact-us/create-profile')

#         return render(request, 'contact_module/create-profile-page.html', {
#             'form': submitted_form
#         })
#     def get (self,request):
#         contact_form = ContactUsModelForm()
#         return render(request, 'contact_module/contact_us.html', {
#             'contact_form': contact_form
#         })

#     def post(self,request):
#         contact_form = ContactUsModelForm(request.POST)
#         if contact_form.is_valid():
#             contact_form.save()
#             return redirect('home_page')

#         return render(request, 'contact_module/contact_us.html', {
#         'contact_form': contact_form
#         })




# class ContactUsView(View):
#     def get (self,request):
#         contact_form = ContactUsModelForm()
#         return render(request, 'contact_module/contact_us.html', {
#             'contact_form': contact_form
#         })

#     def post(self,request):
#         contact_form = ContactUsModelForm(request.POST)
#         if contact_form.is_valid():
#             contact_form.save()
#             return redirect('home_page')

#         return render(request, 'contact_module/contact_us.html', {
#         'contact_form': contact_form
#         })

# def contact_us_page(request):
#     #if request.method == 'POST':
#         #print(request.POST['email'])
#         #print(request.POST['fullname'])
#         #print(request.POST['subject'])
#         # print(request.POST['message'])
#     #return redirect(reverse('home_page')) #After the user is done with the redirect command, he will pass it to the desired page, as well as the reverse command, which takes us to the desired page in reverse, and its status code is 300.
#     #contact_form = ContactUsForm(request.POST or None)
#     if request.method == 'POST':
#         #contact_form = ContactUsForm(request.POST)
#         contact_form = ContactUsModelForm(request.POST)
#         if contact_form.is_valid():
#             #print(contact_form.cleaned_data)
#             #contact = contact_us(
#                 #title  = contact_form.cleaned_data.get('title'),
#                 #full_name  = contact_form.cleaned_data.get('full_name'),
#                 #email  = contact_form.cleaned_data.get('email'),
#                 #message  = contact_form.cleaned_data.get('message'),
#             #)
#             #contact.save()
#             contact_form.save()
#             return redirect('home_page')
#     else:
#         #contact_form = ContactUsForm()
#         contact_form = ContactUsModelForm()
#     return render(request, 'contact_module/contact_us.html', {
#         'contact_form': contact_form
#     })