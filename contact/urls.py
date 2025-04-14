from django.urls import path
from . import views
urlpatterns = [
    path('', views.ContactUsView.as_view(), name='contact_us_page'),
    path('create-profile/', views.CreateProfileView.as_view(), name='create_profile_page'),
    path('profiles/', views.ProfilesView.as_view(), name='profiles_page'),
]
#If we use the base view class in our videos, we need to use the view 
#command in the URL so that Django recognizes that view as a view and not a form.