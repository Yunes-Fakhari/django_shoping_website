from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home_page'),
    path('about-us', views.AboutView.as_view(), name='about_page'),
    path('featured-products/', views.FeaturedProductListView.as_view(), name='featured_products'),
    path('search/', views.ProductSearchView.as_view(), name='product_search'),
    path('searchp_m/', views.ProductSearchMobileView.as_view(), name='product_mobile_search'),
    #path('', views.index_page , name='home_page'),
    #path('contact-us/' , views.contact_page),
    # path('site-header' , views.site_header_partial , name = 'site_header_partial')
]