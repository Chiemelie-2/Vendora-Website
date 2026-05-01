from django.urls import path
from . import views

app_name = 'vendor_dashboard'

urlpatterns = [
    path('',                                          views.dashboard,            name='dashboard'),
    path('products/',                                 views.products_list,        name='products'),
    path('orders/',                                   views.orders_list,          name='orders'),
    path('orders/<int:item_id>/update/<str:new_status>/', views.update_order_status, name='update_status'),
    path('settings/',                                 views.store_settings,       name='settings'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/delete/<int:product_id>/', views.delete_product, name= 'delete_product'),
]
