# myapp/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('redirect/', views.role_redirect, name='role_redirect'),
    # Stock CRUD
    path('accounts/dashboard/', views.accounts_dashboard, name='accounts_dashboard'),
    path('accounts/stock/add/', views.stock_add, name='stock_add'),
    path('accounts/stock/<int:pk>/edit/', views.stock_edit, name='stock_edit'),
    path('accounts/stock/<int:pk>/delete/', views.stock_delete, name='stock_delete'),
    # DeliveryTicket CRUD
    path('delivery/dashboard/', views.delivery_tickets, name='delivery_dashboard'),
    path('delivery/ticket/add/', views.ticket_add, name='ticket_add'),
    path('delivery/ticket/<int:pk>/edit/', views.ticket_edit, name='ticket_edit'),
    path('delivery/ticket/<int:pk>/delete/', views.ticket_delete, name='ticket_delete'),
    path('delivery/ticket/<int:pk>/print/', views.print_ticket, name='print_ticket'),
]
