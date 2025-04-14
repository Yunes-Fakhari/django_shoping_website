from django.urls import path
from .import views
# from .views import home, RegisterView , profile
from django.contrib.auth import views as auth_views
# from product.views import CustomLoginView  
# from product.forms import LoginForm
urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('product-modal/<slug:slug>/', views.ProductModalDetailView.as_view(), name='product_modal_detail'),
    path('cat/<cat>', views.ProductListView.as_view(), name='product-categories-list'),
    path('brand/<brand>', views.ProductListView.as_view(), name='product-list-by-brands'),
    # path('product-favorite', views.AddProductFavorite.as_view(), name='product-favorite'),
    path('<slug:slug>', views.ProductDetailView.as_view(), name='product_detail'),
    path('export-products/',views.export_products_to_excel, name='export_products'),
    # path('', views.product_list, name='product-list'),
]