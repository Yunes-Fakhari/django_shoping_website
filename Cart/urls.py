from django.urls import path
from . import views

urlpatterns = [
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('request-payment/', views.request_payment, name='request_payment'),
    path('verify-payment', views.verify_payment, name='checkout_page')
]