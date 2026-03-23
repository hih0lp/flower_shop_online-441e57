from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Public
    path('', views.index, name='index'),
    path('catalog/', views.catalog, name='catalog'),
    path('catalog/<int:flower_id>/', views.flower_detail, name='flower_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:flower_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:flower_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:flower_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/<int:order_id>/', views.payment, name='payment'),
    path('payment/create-checkout-session/<int:order_id>/', views.create_checkout_session, name='create_checkout_session'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
    # Auth
    path('accounts/login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/register/', views.register, name='register'),
    path('profile/orders/', views.order_history, name='order_history'),
    # Management
    path('manage/flowers/', views.manage_flower_list, name='manage_flower_list'),
    path('manage/flowers/add/', views.manage_flower_add, name='manage_flower_add'),
    path('manage/flowers/<int:flower_id>/edit/', views.manage_flower_edit, name='manage_flower_edit'),
    path('manage/flowers/<int:flower_id>/delete/', views.manage_flower_delete, name='manage_flower_delete'),
]
