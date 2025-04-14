from django.urls import path
from . import views

urlpatterns = [
    path ('' , views.UserPanelDashboardPage.as_view(),name= 'user_panel_dashboard'),
    path ('edit-profile' , views.update_profile,name= 'edit_profile_page'),
    path ('change-pass' , views.ChangePasswordPage.as_view(),name= 'change_password_page'),
    path ('user-cart' , views.user_cart,name= 'user_cart_page'),
    path ('my-shopping' , views.MyShopping.as_view(),name= 'user_shopping_page'),
    path('invoice/<int:cart_id>/', views.invoice_view, name="invoice"),
    path('favorites', views.FavoriteListView.as_view(), name='favorite_list'),
    path('favorites/add/<int:product_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('favorites/remove/<int:pk>/', views.remove_favorite_item, name='favorite_remove'),
    path('my-shopping-detail/<cart_id>', views.my_shopping_detail, name='user_shopping_detail_page'),
    path ('remove-cart-detail' , views.remove_cart_detail,name= 'remove_cart_detail'),
    path ('change-cart-detail' , views.change_order_detail_count,name= 'remove_cart_detail_count_ajax'),
]
