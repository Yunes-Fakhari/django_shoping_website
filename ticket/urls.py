from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    path('', views.TicketListView.as_view(), name='list'),
    path('create/', views.TicketCreateView.as_view(), name='create'),
    path('<int:pk>/', views.TicketDetailView.as_view(), name='detail'),
    path('<int:pk>/close/', views.CloseTicketView.as_view(), name='close'),
    path('<int:pk>/message/', views.TicketMessageCreateView.as_view(), name='add_message'),
]